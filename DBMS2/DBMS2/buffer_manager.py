# buffer_manager.py
import os
import time
import threading


class Buffer:
    def __init__(self, block_size=4096):
        self.buffers = {}  # 缓冲池
        self.lru = []      # LRU队列
        self.lock = threading.Lock()
        self.saved_data = {}  # 添加一个字典来保存刷新的数据

    def get_buffer(self, filename, block_num):
        """获取缓冲区页面"""
        with self.lock:
            key = (filename, block_num)
            
            # 如果数据在saved_data中，先恢复它
            if key in self.saved_data:
                data = self.saved_data[key]
                self.buffers[key] = (data, False, 0)
                del self.saved_data[key]
                return data
                
            if key in self.buffers:
                # 更新LRU
                if key in self.lru:
                    self.lru.remove(key)
                self.lru.append(key)
                return self.buffers[key][0]
            
            # 分配新的缓冲区
            data = bytearray(self.block_size)
            self.buffers[key] = (data, False, 0)
            self.lru.append(key)
            return data

    def flush_all(self):
        """刷新所有脏页"""
        with self.lock:
            # 保存所有脏页的数据
            for key, (data, is_dirty, _) in list(self.buffers.items()):
                if is_dirty:
                    self.saved_data[key] = data.copy()  # 保存数据的副本
            
            # 清空缓冲区
            self.buffers.clear()
            self.lru.clear()

    def _replace(self):
        """替换策略（LRU）"""
        for key in self.lru:
            if self.buffers[key][2] == 0:  # pin_count == 0
                if self.buffers[key][1]:  # is_dirty
                    self._flush(key)
                del self.buffers[key]
                self.lru.remove(key)
                return
        raise Exception("No unpinned buffers available")

    def _flush(self, key):
        """将脏页写回磁盘"""
        filename, block_num = key
        data, _, _ = self.buffers[key]
        # 这里应该调用文件管理器写回磁盘
        # file_mgr.write_block(filename, block_num, data)

    def pin(self, filename, block_num):
        """固定页面"""
        with self.lock:
            key = (filename, block_num)
            if key in self.buffers:
                _, is_dirty, pin_count = self.buffers[key]
                self.buffers[key] = (self.buffers[key][0], is_dirty, pin_count + 1)

    def unpin(self, filename, block_num):
        """解除页面固定"""
        with self.lock:
            key = (filename, block_num)
            if key in self.buffers:
                _, is_dirty, pin_count = self.buffers[key]
                if pin_count > 0:
                    self.buffers[key] = (self.buffers[key][0], is_dirty, pin_count - 1)

    def set_modified(self, filename, block_num):
        """标记页面为脏页"""
        with self.lock:
            key = (filename, block_num)
            if key in self.buffers:
                self.buffers[key] = (self.buffers[key][0], True, self.buffers[key][2])

    def get_dirty_pages(self) -> list:
        """获取所有脏页"""
        dirty_pages = []
        with self.lock:
            for key, (data, is_dirty, _) in self.buffers.items():
                if is_dirty:
                    dirty_pages.append({
                        'file': key[0],
                        'block': key[1],
                        'data': data.copy()
                    })
        return dirty_pages


class BufferMgr:
    def __init__(self, num_buffers: int, block_size: int = 4096):
        """
        初始化缓冲区管理器
        :param num_buffers: 缓冲池中的缓冲区数量
        :param block_size: 块的大小
        """
        self.num_buffers = num_buffers
        self.block_size = block_size
        self.buffers = [Buffer(block_size) for _ in range(num_buffers)]
        self.buffer_pool = {}  # 块到缓冲区的映射

    def pin(self, block):
        """
        固定一个块到缓冲区
        :param block: 块标识符
        :return: 固定的缓冲区
        """
        start_time = time.time()

        while True:
            buffer = self._try_to_pin(block)
            if buffer:
                return buffer

            if time.time() - start_time > 10:
                raise BufferAbortException("Buffer allocation timed out")

            time.sleep(0.1)  # 等待缓冲区释放

    def unpin(self, buffer: Buffer):
        """
        取消缓冲区的固定
        :param buffer: 目标缓冲区
        """
        buffer.unpin()

    def _try_to_pin(self, block) -> Buffer:
        """
        尝试将块固定到缓冲区
        :param block: 块标识符
        :return: 固定的缓冲区或None
        """
        buffer = self.buffer_pool.get(block)
        if buffer:
            if not buffer.is_pinned():
                buffer.pin()
            return buffer

        for buffer in self.buffers:
            if not buffer.is_pinned():
                self._replace_buffer(buffer, block)
                buffer.pin()
                self.buffer_pool[block] = buffer
                return buffer

        return None

    def _replace_buffer(self, buffer: Buffer, block):
        """
        替换缓冲区中的内容
        :param buffer: 目标缓冲区
        :param block: 新块标识符
        """
        buffer.assign_to_block(block)

    def available(self) -> int:
        """
        返回可用缓冲区的数量
        :return: 可用缓冲区数量
        """
        return sum(1 for buffer in self.buffers if not buffer.is_pinned())


class BufferAbortException(Exception):
    """当缓冲区分配超时时抛出此异常"""
    pass
