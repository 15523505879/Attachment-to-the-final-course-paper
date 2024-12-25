from transaction_manager import Transaction
from concurrency_manager import ConcurrencyMgr  # 添加这行导入

class QueryManager:
    """
    管理查询和更新操作
    """
    def __init__(self, table_metadata, table_scan_cls, log_mgr):
        self.table_metadata = table_metadata  # 表元数据管理器
        self.table_scan_cls = table_scan_cls  # 表扫描类
        self.log_mgr = log_mgr  # 日志管理器
        self.concurrency_mgr = ConcurrencyMgr()
        self.current_transaction = None  # 当前事务
        self.transactions = {}  # {tx_id: Transaction}
        self.file_mgr = table_metadata.file_mgr  # 从 table_metadata 获取 file_mgr
        self.sql_parser = None  # 添加sql_parser属性

    def start_transaction(self, tx_id: int):
        """开始新事务"""
        if tx_id in self.transactions:
            raise Exception(f"事务 {tx_id} 已存在")
        tx = Transaction(tx_id, self.concurrency_mgr)
        self.set_transaction_query_manager(tx)  # 设置 query_manager 引用
        self.transactions[tx_id] = tx
        self.current_transaction = tx
        self.log_mgr.write_log(tx_id, "START", "Transaction started")
        return tx

    def get_transaction(self, tx_id: int):
        """获取事务对象"""
        if tx_id not in self.transactions:
            tx = self.start_transaction(tx_id)
        return self.transactions[tx_id]

    def create_table(self, table_name: str, fields: list, types: list):
        """创建表"""
        if self.table_metadata.create_table(table_name, fields, types):
            print(f"[CRUD] 创建表 {table_name}")
            self.log_mgr.write_log(0, "CREATE", f"Table '{table_name}' created with fields: {fields}")
            return f"Table '{table_name}' created successfully."
        else:
            return f"Table '{table_name}' already exists."

    def insert_query(self, file_mgr, table_name: str, values: bytes, tx_id: int):
        """插入记录"""
        try:
            if not self.current_transaction.acquire_lock(table_name, "X"):
                raise Exception(f"无法获取表 {table_name} 的排他锁")
            
            # 记录插入操作用于回滚
            self.current_transaction.add_operation(
                'INSERT', 
                table_name, 
                values.decode('utf-8')
            )
            
            table_scan = self.table_scan_cls(file_mgr, table_name, 128)
            table_scan.insert_record(values)
            
            # 只输出插入信息
            record_str = values.decode('utf-8')
            print(f"[CRUD] TX {tx_id} 插入记录: {record_str}")
            self.log_mgr.write_log(tx_id, "INSERT", f"Record inserted into {table_name}: {record_str}")
            
            return f"Record inserted into table '{table_name}'"
            
        except Exception as e:
            self.current_transaction.rollback()  # 发生异常时自动回滚
            raise e

    def delete_query(self, file_mgr, table_name: str, condition_func, tx_id: int):
        """删除记录"""
        try:
            # 1. 获取表的排他锁
            if not self.current_transaction.acquire_lock(table_name, "X"):
                raise Exception(f"无法获取表 {table_name} 的排他锁")

            table_scan = self.table_scan_cls(file_mgr, table_name, 128)
            table_scan.before_first()
            deleted = False
            records_to_delete = []
            while table_scan.next():
                record = table_scan.get_current_record()
                if record:
                    record_str = record.decode('utf-8').strip()
                    if condition_func(record):
                        records_to_delete.append((table_scan.current_block, table_scan.current_slot, record_str))

            for block_num, slot_num, record_str in records_to_delete:
                table_scan.current_block = block_num
                table_scan.current_slot = slot_num
                table_scan.page.data = bytearray(file_mgr.read_block(table_name, block_num))
                table_scan.delete_current_record()
                print(f"[CRUD] TX {tx_id} 删除记录: {record_str}")
                self.log_mgr.write_log(tx_id, "DELETE", record_str)
                deleted = True

            if deleted:
                return f"Records deleted from table '{table_name}'."
            else:
                return "No records matched the delete condition."

        except Exception as e:
            self.log_mgr.write_log(tx_id, "ERROR", f"Failed to delete records: {str(e)}")
            raise e

    def _get_record_key(self, table_name: str, record_id: str) -> str:
        """生成记录锁的键"""
        return f"{table_name}:record:{record_id}"

    def update_query(self, file_mgr, table_name: str, set_values: dict, condition_func, tx_id: int):
        """更新记录"""
        try:
            # 1. 获取表的排他锁
            if not self.current_transaction.acquire_lock(table_name, "X"):
                raise Exception(f"无法获取表 {table_name} 的排他锁")
            
            # 2. 获取表的字段信息
            fields = self.table_metadata.get_table_fields(table_name)
            if not fields:
                raise ValueError(f"表 {table_name} 不存在或字段信息获取失败")
            
            field_names = [field[0] for field in fields]
            field_types = [field[1] for field in fields]
            
            # 3. 先扫描找到所有需要更新的记录
            table_scan = self.table_scan_cls(file_mgr, table_name, 128)
            records_to_update = []
            record_ids = set()
            
            table_scan.before_first()
            while table_scan.next():
                record = table_scan.get_current_record()
                if record and condition_func(record):
                    record_str = record.decode('utf-8').strip()
                    record_id = record_str.split(",")[0].strip()
                    record_ids.add(record_id)
                    
                    # 保存记录信息
                    records_to_update.append((
                        table_scan.current_block,
                        table_scan.current_slot,
                        record_str
                    ))
                    
                    # 保存原始值用于回滚
                    old_parts = [p.strip() for p in record_str.split(',')]
                    old_values = {}
                    for field_name in set_values.keys():
                        if field_name in field_names:
                            idx = field_names.index(field_name)
                            old_values[field_name] = old_parts[idx]
                    
                    self.current_transaction.add_operation(
                        'UPDATE',
                        table_name,
                        record_str,
                        old_values
                    )
            
            # 4. 一次性获取所有记录的排他锁
            for record_id in record_ids:
                record_key = self._get_record_key(table_name, record_id)
                if not self.current_transaction.acquire_lock(record_key, "X"):
                    raise Exception(f"无法获取记录 {record_id} 的排他锁")
            
            # 5. 执行更新操作
            updated = False
            for block_num, slot_num, record_str in records_to_update:
                # 解析记录
                parts = [p.strip().strip("'") for p in record_str.split(",")]
                
                # 更新字段值
                for field, value_info in set_values.items():
                    idx = field_names.index(field)
                    current_value = int(parts[idx])
                    
                    if value_info['type'] == 'add':
                        parts[idx] = str(current_value + value_info['amount'])
                    elif value_info['type'] == 'subtract':
                        parts[idx] = str(current_value - value_info['amount'])
                    else:  # direct
                        parts[idx] = str(value_info['value'])
                
                # 重新格式化记录
                new_record = ", ".join(
                    f"'{p}'" if t == "STRING" else p 
                    for p, t in zip(parts, field_types)
                )
                
                # 写入新记录
                table_scan.current_block = block_num
                table_scan.current_slot = slot_num
                table_scan.page.data = bytearray(file_mgr.read_block(table_name, block_num))
                table_scan.delete_current_record()
                table_scan.insert_record(new_record.encode('utf-8'))
                print(f"[CRUD] TX {tx_id} 更新记录: {record_str} -> {new_record}")
                updated = True
            
            if updated:
                return f"Records updated in table '{table_name}'."
            else:
                return "No records matched the update condition."
            
        except Exception as e:
            self.current_transaction.rollback()  # 发生异常时自动回滚
            raise e

    def select_query(self, table_name: str, condition=None):
        """查询记录"""
        try:
            # 只获取一次表级共享锁
            if not self.current_transaction.acquire_lock(table_name, "S"):
                raise Exception(f"无法获取表 {table_name} 的共享锁")
            
            records = []
            table_scan = self.table_scan_cls(self.file_mgr, table_name, 128)
            table_scan.before_first()
            
            # 收集所有需要的记录ID
            record_ids = set()
            while table_scan.next():
                record = table_scan.get_current_record()
                if record:
                    record_str = record.decode('utf-8').strip()
                    if condition and not condition(record_str):
                        continue
                    
                    record_id = record_str.split(",")[0].strip()
                    record_ids.add(record_id)
            
            # 一次性获取所有需要的记录锁
            if not self.current_transaction.is_recovery:
                for record_id in record_ids:
                    record_key = f"{table_name}:record:{record_id}"
                    if not self.current_transaction.acquire_lock(record_key, "S"):
                        raise Exception(f"无法获取记录 {record_id} 的共享锁")
            
            # 再次扫描获取数据
            table_scan.before_first()
            while table_scan.next():
                record = table_scan.get_current_record()
                if record:
                    record_str = record.decode('utf-8').strip()
                    if condition and not condition(record_str):
                        continue
                    records.append(record_str)
                    
            return records
            
        except Exception as e:
            print(f"[ERROR] 查询失败: {str(e)}")
            raise e

    def execute_query(self, sql, tx_id):
        """执行查询"""
        try:
            result = self.sql_parser.execute(sql, tx_id)
            if result:
                return result
        except Exception as e:
            print(f"查询执行错误: {str(e)}")
            raise e

    def _get_current_record(self, table_name: str, condition_func) -> str:
        """获取当前记录"""
        try:
            table_scan = self.table_scan_cls(self.file_mgr, table_name, 128)
            table_scan.before_first()
            
            while table_scan.next():
                record = table_scan.get_current_record()
                if record and condition_func(record):
                    return record.decode('utf-8').strip()
            return None
            
        except Exception as e:
            print(f"[ERROR] Failed to get current record: {str(e)}")
            return None

    def set_transaction_query_manager(self, transaction):
        """设置事务的 query_manager 引用"""
        transaction.query_manager = self

    def set_sql_parser(self, sql_parser):
        """设置SQL解析器"""
        self.sql_parser = sql_parser
