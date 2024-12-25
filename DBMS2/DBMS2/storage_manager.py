import os
import struct


class FileMgr:
    """
    文件管理器，用于管理数据库文件
    """
    def __init__(self, db_directory: str, block_size: int = 4096):
        self.db_directory = db_directory
        self.block_size = block_size
        self.files = {}  # 表名 -> list of blocks

        # 确保数据库目录存在
        if not os.path.exists(db_directory):
            os.makedirs(db_directory)

    def read_block(self, table_name: str, block_number: int) -> bytes:
        """
        读取指定表的指定块
        """
        file_path = os.path.join(self.db_directory, f"{table_name}.db")
        with open(file_path, 'rb') as f:
            f.seek(block_number * self.block_size)
            return f.read(self.block_size)

    def write_block(self, table_name: str, block_number: int, data: bytes):
        """
        写入数据到指定表的指定块
        """
        file_path = os.path.join(self.db_directory, f"{table_name}.db")
        with open(file_path, 'r+b' if os.path.exists(file_path) else 'wb') as f:
            f.seek(block_number * self.block_size)
            data = data.ljust(self.block_size, b'\0')  # 固定块大小
            f.write(data)

    def append_block(self, table_name: str) -> int:
        """
        在表文件末尾添加新块
        :return: 新块的块号
        """
        file_path = os.path.join(self.db_directory, f"{table_name}.db")
        
        # 如果文件不存在，创建它
        if not os.path.exists(file_path):
            with open(file_path, 'wb') as f:
                f.write(bytearray(self.block_size))
            return 0
            
        # 获取当前文件大小
        file_size = os.path.getsize(file_path)
        block_number = file_size // self.block_size
        
        # 添加新块
        with open(file_path, 'ab') as f:
            f.write(bytearray(self.block_size))
            
        return block_number

    def size(self, table_name: str) -> int:
        """
        返回表文件的块数
        """
        file_path = os.path.join(self.db_directory, f"{table_name}.db")
        if not os.path.exists(file_path):
            return 0
        return os.path.getsize(file_path) // self.block_size

    def create_table_file(self, table_name: str):
        """
        创建新的表文件
        """
        file_path = os.path.join(self.db_directory, f"{table_name}.db")
        if not os.path.exists(file_path):
            with open(file_path, 'wb') as f:
                # 写入一个空块作为初始块
                f.write(bytearray(self.block_size))

    def flush_all(self):
        """刷新所有文件到磁盘"""
        try:
            # 遍历所有打开的文件
            for table_name in self.files:
                file_path = os.path.join(self.db_directory, f"{table_name}.db")
                if os.path.exists(file_path):
                    # 强制刷新文件缓冲区
                    with open(file_path, 'rb+') as f:
                        f.flush()
                        os.fsync(f.fileno())  # 确保写入磁盘
                        
            return True
        except Exception as e:
            print(f"[ERROR] Failed to flush files: {str(e)}")
            return False
