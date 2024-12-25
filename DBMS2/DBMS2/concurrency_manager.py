import threading
import time


class ConcurrencyMgr:
    """并发管理器：管理事务的锁和并发访问"""

    def __init__(self):
        self.locks = {}  # {resource_name: {tx_id: lock_type}}
        self.log_mgr = None  # 将在初始化时设置
        self.recovery_mode = False  # 添加恢复模式标志

    def set_log_manager(self, log_mgr):
        self.log_mgr = log_mgr

    def set_recovery_mode(self, mode: bool):
        """设置恢复模式"""
        self.recovery_mode = mode

    def acquire_lock(self, tx_id: int, resource_name: str, lock_type: str) -> bool:
        """
        获取锁
        """
        # 在恢复模式下直接授予锁
        if self.recovery_mode:
            if resource_name not in self.locks:
                self.locks[resource_name] = {}
            self.locks[resource_name][tx_id] = lock_type
            return True

        # 正常模式下的锁检查
        if resource_name not in self.locks:
            self.locks[resource_name] = {}

        # 检查锁冲突
        for other_tx_id, other_lock_type in self.locks[resource_name].items():
            if other_tx_id != tx_id:
                if lock_type == "X" or other_lock_type == "X":
                    return False

        # 授予锁
        self.locks[resource_name][tx_id] = lock_type
        if self.log_mgr:
            self.log_mgr.write_lock_log(tx_id, "ACQUIRED", resource_name, lock_type)
        return True

    def release_lock(self, tx_id: int, resource_name: str):
        """
        释放锁
        """
        if resource_name in self.locks and tx_id in self.locks[resource_name]:
            lock_type = self.locks[resource_name][tx_id]
            del self.locks[resource_name][tx_id]
            if self.log_mgr:
                self.log_mgr.write_lock_log(tx_id, "RELEASED", resource_name, lock_type)

    def clear_all_locks(self):
        """清空所有锁"""
        if self.log_mgr:
            # 记录清空锁的操作
            self.log_mgr.write_log(0, "CLEAR", "Clear all locks")
        self.locks.clear()
