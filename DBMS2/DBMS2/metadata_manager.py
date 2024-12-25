import os

class TableMetadata:
    """
    管理表的元数据：字段名、字段类型等信息
    """

    def __init__(self, file_mgr):
        self.file_mgr = file_mgr
        self.metadata = {}  # 存储表的元数据
        self._load_existing_tables()  # 加载已存在的表
        
    def _load_existing_tables(self):
        """从文件系统加载已存在的表"""
        if not os.path.exists(self.file_mgr.db_directory):
            return
            
        for filename in os.listdir(self.file_mgr.db_directory):
            if filename.endswith('.db'):
                table_name = filename[:-3]  # 移除 .db 后缀
                if table_name not in self.metadata:
                    # 默认字段结构 - 统一为两个字段
                    self.metadata[table_name] = [
                        ('id', 'INT'),
                        ('name', 'STRING')
                    ]

    def create_table(self, table_name: str, fields: list, types: list) -> bool:
        """
        创建表的元数据
        :param table_name: 表名
        :param fields: 字段名列
        :param types: 字段类型列表
        :return: 是否创建成功
        """
        if table_name in self.metadata:
            print(f"[WARNING] Table '{table_name}' already exists.")
            return False
            
        # 存储字段信息为元组列表 [(field_name, field_type), ...]
        field_info = list(zip(fields, types))
        self.metadata[table_name] = field_info
        
        # 创建表文件
        self.file_mgr.create_table_file(table_name)
        print(f"[INFO] Creating table '{table_name}' with fields: {fields}")
        return True
        
    def get_table_fields(self, table_name: str) -> list:
        """
        获取表的字段信息
        :param table_name: 表名
        :return: 字段信息列表 [(field_name, field_type), ...]
        """
        if table_name not in self.metadata:
            print(f"[ERROR] Table '{table_name}' does not exist.")
            return None
            
        return self.metadata[table_name]

    def list_tables(self):
        """列出所有表"""
        # 直接返回当前内存中的表列表，不重新加载
        return list(self.metadata.keys())
