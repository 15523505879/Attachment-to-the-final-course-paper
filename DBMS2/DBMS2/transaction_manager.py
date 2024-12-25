import time

from DBMS2.DBMS2.recovery_manager import RecoveryManager


class Transaction:
    def __init__(self, tx_id: int, concurrency_mgr):
        self.tx_id = tx_id
        self.concurrency_mgr = concurrency_mgr
        self.status = "active"
        self.operations = []  # 记录操作用于回滚
        self.locks = set()  # 记录获取的锁
        self.query_manager = None
        self.is_recovery = False

    def add_operation(self, operation_type: str, table_name: str, record: str, old_value=None):
        """记录操作用于回滚"""
        if operation_type == 'UPDATE':
            # 确保old_value是字典，包含字段名和值
            if isinstance(old_value, dict):
                # 获取字段类型信息
                fields = self.query_manager.table_metadata.get_table_fields(table_name)
                field_types = {f[0]: f[1] for f in fields}

                # 根据字段类型转换值
                typed_values = {}
                for field, value in old_value.items():
                    if field in field_types:
                        if field_types[field] == 'INT':
                            typed_values[field] = int(value)
                        else:
                            typed_values[field] = value

                self.operations.append({
                    'type': operation_type,
                    'table': table_name,
                    'record': record,
                    'old_value': typed_values
                })
        else:
            self.operations.append({
                'type': operation_type,
                'table': table_name,
                'record': record,
                'old_value': old_value
            })

    def acquire_lock(self, resource_name: str, lock_type: str) -> bool:
        """获取锁"""
        # 恢复模式下跳过锁检查
        if self.is_recovery:
            return True

        # 记录级锁在恢复模式下也跳过
        if ':record:' in resource_name and self.is_recovery:
            return True

        result = self.concurrency_mgr.acquire_lock(self.tx_id, resource_name, lock_type)
        if result:
            self.locks.add(resource_name)
        return result

    def release_all_locks(self):
        """释放所有锁"""
        for resource in list(self.locks):
            try:
                self.concurrency_mgr.release_lock(self.tx_id, resource)
                self.locks.remove(resource)
            except Exception:
                pass
        self.locks.clear()

    def commit(self):
        """提交事务"""
        self.status = "committed"
        self.release_all_locks()

    def rollback(self):
        """回滚事务 - 基本版本，只释放锁和更新状态"""
        print(f"[TRANSACTION] Basic rollback for transaction {self.tx_id}")
        self.status = "rolled_back"
        self.release_all_locks()
        self.operations.clear()  # 清空操作列表

    def set_recovery_mode(self, mode: bool):
        """设置恢复模式"""
        self.is_recovery = mode


class TransactionManager:
    def __init__(self):
        self.recovery_manager = RecoveryManager()

    def rollback_transaction(self, transaction_id):
        """回滚事务"""
        try:
            self.recovery_manager.rollback_transaction(transaction_id)
            return True, "事务回滚成功"
        except Exception as e:
            return False, f"事务回滚失败: {str(e)}"
