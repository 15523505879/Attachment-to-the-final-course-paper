import struct


class RID:
    """
    记录标识符 (Record ID)
    """
    def __init__(self, block_number: int, slot: int):
        """
        初始化记录标识符
        :param block_number: 块号
        :param slot: 槽号（记录在块中的位置）
        """
        self.block_number = block_number
        self.slot = slot

    def __eq__(self, other):
        return self.block_number == other.block_number and self.slot == other.slot

    def __str__(self):
        return f"RID(Block: {self.block_number}, Slot: {self.slot})"


class RecordPage:
    """
    管理一个页面中的记录
    """
    def __init__(self, block_size: int):
        """
        初始化记录页面
        :param block_size: 页面大小
        """
        self.block_size = block_size
        self.data = bytearray(block_size)
        self.header_size = 4  # 记录页面头部大小（存储记录数量）

    def insert_record(self, record: bytes) -> int:
        """
        插入一条记录
        :param record: 记录的字节数据
        :return: 插入的槽号（位置）
        """
        num_records = struct.unpack_from("!I", self.data, 0)[0]  # 获取记录数量
        record_size = len(record)
        offset = self.header_size + num_records * record_size

        if offset + record_size > self.block_size:
            raise Exception("No space in page for new record.")

        # 插入记录
        self.data[offset:offset + record_size] = record
        struct.pack_into("!I", self.data, 0, num_records + 1)  # 更新记录数量
        return num_records

    def get_record(self, slot: int, record_size: int) -> bytes:
        """
        获取指定槽号的记录
        :param slot: 记录的槽号
        :param record_size: 记录的大小
        :return: 记录的字节数据
        """
        offset = self.header_size + slot * record_size
        return self.data[offset:offset + record_size]

    def delete_record(self, slot: int, record_size: int):
        """
        删除指定槽号的记录
        :param slot: 记录的槽号
        :param record_size: 记录的大小
        """
        num_records = struct.unpack_from("!I", self.data, 0)[0]
        if slot >= num_records:
            return

        # 计算要删除的记录的偏移量
        delete_offset = self.header_size + slot * record_size
        next_record_offset = delete_offset + record_size

        # 将后面的记录向前移动
        self.data[delete_offset:delete_offset + (num_records - slot - 1) * record_size] = \
            self.data[next_record_offset:next_record_offset + (num_records - slot - 1) * record_size]

        # 更新记录数量
        struct.pack_into("!I", self.data, 0, num_records - 1)

    def num_records(self) -> int:
        """
        返回页面中记录的数量
        """
        try:
            return struct.unpack_from("!I", self.data, 0)[0]
        except struct.error:
            print("[WARNING] Failed to read record count, returning 0")
            return 0


class TableScan:

    """
    提供对表中记录的顺序扫描
    """
    def __init__(self, file_mgr, table_name: str, record_size: int):
        """
        初始化表扫描
        """
        self.file_mgr = file_mgr
        self.table_name = table_name
        self.record_size = record_size
        self.current_block = 0
        self.current_slot = -1
        self.page = RecordPage(file_mgr.block_size)
        self.total_blocks = file_mgr.size(table_name)

        # 初始化第一个块
        if self.total_blocks > 0:
            self.page.data = bytearray(file_mgr.read_block(self.table_name, self.current_block))

    def before_first(self):
        """
        将扫描重置到第一条记录之前
        """
        self.current_block = 0
        self.current_slot = -1
        self.total_blocks = self.file_mgr.size(self.table_name)
        if self.total_blocks > 0:
            try:
                self.page.data = bytearray(self.file_mgr.read_block(self.table_name, self.current_block))
            except Exception as e:
                print(f"[ERROR] Failed to read initial block: {e}")
                self.page = RecordPage(self.file_mgr.block_size)
        else:
            self.page = RecordPage(self.file_mgr.block_size)

    def insert_record(self, record: bytes):
        """
        插入新记录
        :param record: 记录的字节数据
        """
        # 确保记录大小合适
        if len(record) > self.record_size:
            raise ValueError(f"Record size ({len(record)}) exceeds maximum size ({self.record_size})")

        # 填充到固定长度
        record = record.ljust(self.record_size, b'\0')

        # 尝试在当前页面插入
        try:
            # 如果当前页面已满，尝试创建新页面
            if self.page.num_records() * self.record_size + self.page.header_size + self.record_size > self.page.block_size:
                raise Exception("Page is full")

            slot = self.page.insert_record(record)
            self.file_mgr.write_block(self.table_name, self.current_block, self.page.data)
            self.total_blocks = max(self.total_blocks, self.current_block + 1)

        except Exception as e:
            # 创建新页面
            self.current_block = self.file_mgr.append_block(self.table_name)
            self.page = RecordPage(self.file_mgr.block_size)
            slot = self.page.insert_record(record)
            self.file_mgr.write_block(self.table_name, self.current_block, self.page.data)
            self.total_blocks = self.current_block + 1

    def next(self) -> bool:
        """
        移动到下一条记录
        """
        while True:
            self.current_slot += 1
            num_records = self.page.num_records()

            # 如果当前块中的所有记录都已读完
            if self.current_slot >= num_records:
                self.current_block += 1
                # 如果所有块都读完了
                if self.current_block >= self.total_blocks:
                    return False

                # 读取下一个块
                try:
                    self.page.data = bytearray(self.file_mgr.read_block(self.table_name, self.current_block))
                    self.current_slot = 0
                    num_records = self.page.num_records()

                    # 如果新块是空的，继续查找下一个块
                    if num_records == 0:
                        continue
                except Exception as e:
                    print(f"[ERROR] Failed to read block {self.current_block}: {e}")
                    return False

            return True

    def get_current_record(self) -> bytes:
        """
        获取当前记录，去除尾部的空字节
        """
        offset = self.page.header_size + self.current_slot * self.record_size
        record = bytes(self.page.data[offset:offset + self.record_size])
        clean_record = record.rstrip(b'\x00')  # 去除尾部的空字节
        if not clean_record:  # 如果记录为空，跳过
            return None
        return clean_record

    def delete_current_record(self):
        """
        删除当前记录
        """
        self.page.delete_record(self.current_slot, self.record_size)
        self.file_mgr.write_block(self.table_name, self.current_block, self.page.data)
        self.current_slot -= 1  # 回退一个位置，因为记录已经被删除
