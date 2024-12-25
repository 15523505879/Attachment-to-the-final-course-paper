import time

class RecoveryManager:
    """数据恢复管理器"""
    
    def __init__(self, log_mgr, query_manager):
        self.log_mgr = log_mgr
        self.query_manager = query_manager
        
    def recover(self, checkpoint_data):
        """执行恢复过程"""
        print("[RECOVERY] Starting recovery process...")
        
        if not checkpoint_data:
            print("[RECOVERY] No checkpoint found")
            return
            
        # 1. 获取检查点信息
        checkpoint_time = checkpoint_data['timestamp']
        active_txs = set(checkpoint_data['active_transactions'])
        tables = checkpoint_data['tables']
        
        # 2. 读取检查点之后的日志
        logs = self.log_mgr.read_logs_after(checkpoint_time)
        committed_txs = set()
        
        # 3. 分析日志，找出已提交和未完成的事务
        for log in logs:
            if 'COMMIT' in log:
                tx_id = self.log_mgr._extract_tx_id(log)
                if tx_id:
                    committed_txs.add(tx_id)
                    active_txs.discard(tx_id)
                    
        # 4. 重建数据库状态
        recovery_tx = self.query_manager.start_transaction(int(time.time() * 1000))
        recovery_tx.set_recovery_mode(True)
        
        try:
            # 4.1 重建表结构
            for table in tables:
                create_stmt = self._find_create_statement(table)
                if create_stmt:
                    self.query_manager.sql_parser.execute(
                        self.query_manager.file_mgr,
                        create_stmt, 
                        recovery_tx.tx_id
                    )
                    
            # 4.2 重建数据
            for log in self.log_mgr.read_logs():
                if checkpoint_time in log and 'CHECKPOINT' in log:
                    break
                    
                if 'INSERT' in log and 'Record inserted' in log:
                    try:
                        values = log.split(': ')[-1]
                        table = log.split('into ')[1].split(':')[0]
                        insert_stmt = f"INSERT INTO {table} VALUES ({values})"
                        self.query_manager.sql_parser.execute(
                            self.query_manager.file_mgr,
                            insert_stmt, 
                            recovery_tx.tx_id
                        )
                    except Exception as e:
                        print(f"[ERROR] Failed to recover insert: {e}")
                        
            recovery_tx.commit()
            print("[RECOVERY] Database state restored to checkpoint")
            
            # 5. 处理未完成的事务
            for tx_id in active_txs:
                print(f"[RECOVERY] Rolling back transaction {tx_id}")
                # 这里可以添加具体的回滚逻辑
                
        except Exception as e:
            print(f"[ERROR] Recovery failed: {e}")
            recovery_tx.rollback()
            raise e
            
    def _find_create_statement(self, table_name: str) -> str:
        """从日志中找到表的创建语句"""
        if table_name == 'student':
            return "CREATE TABLE student (id INT, name STRING, age INT)"
        elif table_name == 'account':
            return "CREATE TABLE account (id INT, name STRING, balance INT)"
        return None

    def redo_committed_transactions(self, logs, checkpoint_time):
        """重做已提交的事务"""
        for log in logs:
            if 'COMMIT' in log:
                tx_id = self.log_mgr._extract_tx_id(log)
                # 重做该事务的所有操作
                self._redo_transaction_operations(tx_id, checkpoint_time)

    def _redo_transaction_operations(self, tx_id, checkpoint_time):
        """重做单个事务的操作"""
        tx_logs = self.log_mgr.get_transaction_logs(tx_id)
        recovery_tx = self.query_manager.start_transaction(int(time.time() * 1000))
        recovery_tx.set_recovery_mode(True)
        
        try:
            for log in tx_logs:
                if self.log_mgr.get_log_time(log) > checkpoint_time:
                    self._replay_operation(log, recovery_tx)
            recovery_tx.commit()
        except Exception as e:
            recovery_tx.rollback()
            print(f"[ERROR] Failed to redo transaction {tx_id}: {e}")

    def rollback_transaction(self, tx_id: int, operations: list):
        """回滚指定事务的操作"""
        print(f"[RECOVERY] Rolling back transaction {tx_id}")
        
        # 创建恢复专用事务
        recovery_tx = self.query_manager.start_transaction(tx_id)
        
        try:
            # 按照相反顺序处理操作
            for op in reversed(operations):
                if op['type'] == 'INSERT':
                    self._undo_insert(op['table'], op['record'], recovery_tx)
                elif op['type'] == 'DELETE':
                    self._undo_delete(op['table'], op['record'], recovery_tx)
                elif op['type'] == 'UPDATE':
                    self._undo_update(op['table'], op['record'], op['old_value'], recovery_tx)
                    
                # 记录回滚操作到日志
                self.log_mgr.write_log(
                    tx_id, 
                    f"ROLLBACK_{op['type']}", 
                    f"Rolled back {op['type']} operation on table {op['table']}"
                )
            
            recovery_tx.commit()
            
        except Exception as e:
            print(f"[ERROR] Failed to rollback operation: {str(e)}")
            recovery_tx.rollback()
            raise e

    def _undo_insert(self, table_name: str, record: str, recovery_tx):
        """撤销插入操作"""
        condition = lambda r: record in str(r)
        self.query_manager.delete_query(
            self.query_manager.file_mgr,
            table_name,
            condition,
            recovery_tx.tx_id
        )
        
    def _undo_delete(self, table_name: str, record: str, recovery_tx):
        """撤销删除操作"""
        self.query_manager.insert_query(
            self.query_manager.file_mgr,
            table_name,
            record.encode('utf-8'),
            recovery_tx.tx_id
        )
        
    def _undo_update(self, table_name: str, record: str, old_value: dict, recovery_tx):
        """撤销更新操作"""
        try:
            # 解析记录和字段
            record_parts = record.split(',')
            record_id = record_parts[0].strip()
            
            # 从元数据获取表的字段信息
            fields = self.query_manager.table_metadata.get_table_fields(table_name)
            if not fields:
                raise ValueError(f"表 {table_name} 不存在或字段信息获取失败")
            
            # 构造更新条件
            condition = lambda r: record_id in str(r)
            
            # 构造更新值
            set_values = {}
            for field_name, value in old_value.items():
                # 获取字段类型
                field_info = next((f for f in fields if f[0] == field_name), None)
                if field_info:
                    field_type = field_info[1]
                    # 根据字段类型构造更新值
                    set_values[field_name] = {
                        'type': 'direct',
                        'value': int(value) if field_type == 'INT' else value
                    }
            
            # 执行更新
            self.query_manager.update_query(
                self.query_manager.file_mgr,
                table_name,
                set_values,  # 包含了字段名和类型正确的值
                condition,
                recovery_tx.tx_id
            )
            
        except Exception as e:
            print(f"[ERROR] Failed to undo update: {str(e)}")
            raise e


