import unittest
import os
import sys
import time

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from storage_manager import FileMgr
from metadata_manager import TableMetadata
from query_manager import QueryManager
from sql_parser import SQLParser
from log_manager import LogManager
from recovery_manager import RecoveryManager
from transaction_manager import Transaction
from concurrency_manager import ConcurrencyMgr
from record_manager import TableScan

class TestRecovery(unittest.TestCase):
    """测试数据恢复功能"""
    
    def setUp(self):
        self.db_directory = "test_db"
        self.log_file = "test.log"
        
        # 清理旧文件
        if os.path.exists(self.db_directory):
            import shutil
            shutil.rmtree(self.db_directory)
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
            
        # 初始化组件
        self.file_mgr = FileMgr(self.db_directory)
        self.log_mgr = LogManager(self.log_file)
        self.table_metadata = TableMetadata(self.file_mgr)
        self.concurrency_mgr = ConcurrencyMgr()
        self.query_manager = QueryManager(self.table_metadata, TableScan, self.log_mgr)
        self.sql_parser = SQLParser(self.query_manager)
        self.query_manager.set_sql_parser(self.sql_parser)
        
    def test_basic_recovery(self):
        """测试基本的恢复功能"""
        # 1. 创建初始数据
        tx = Transaction(1, self.concurrency_mgr)
        tx.query_manager = self.query_manager
        self.query_manager.current_transaction = tx
        
        self.sql_parser.execute(self.file_mgr,
            "CREATE TABLE account (id INT, name STRING, balance INT)", tx.tx_id)
        self.sql_parser.execute(self.file_mgr,
            "INSERT INTO account VALUES (1, 'Alice', 1000)", tx.tx_id)
        tx.commit()
        
        # 2. 创建检查点
        checkpoint_data = {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'active_transactions': [],
            'tables': ['account']
        }
        self.log_mgr.write_checkpoint(checkpoint_data)
        
        # 3. 模拟系统崩溃
        self._clear_current_state()
        
        # 4. 执行恢复
        recovery_mgr = RecoveryManager(self.log_mgr, self.query_manager)
        recovery_mgr.recover(checkpoint_data)
        
        # 5. 验证恢复结果
        tx = Transaction(2, self.concurrency_mgr)
        self.query_manager.current_transaction = tx
        result = self.sql_parser.execute(self.file_mgr,
            "SELECT * FROM account WHERE id = 1", tx.tx_id)
        tx.commit()
        
        self.assertIsNotNone(result)
        self.assertIn("Alice", str(result))
        self.assertIn("1000", str(result))
        
    def test_multi_transaction_recovery(self):
        """测试多事务恢复"""
        # 1. 准备初始数据
        tx = Transaction(1, self.concurrency_mgr)
        tx.query_manager = self.query_manager
        self.query_manager.current_transaction = tx
        self.sql_parser.execute(self.file_mgr,
            "CREATE TABLE account (id INT, name STRING, balance INT)", tx.tx_id)
        tx.commit()
        
        # 2. 执行多个并发事务
        tx1 = Transaction(101, self.concurrency_mgr)
        tx1.query_manager = self.query_manager
        self.query_manager.current_transaction = tx1
        self.sql_parser.execute(self.file_mgr,
            "INSERT INTO account VALUES (1, 'Alice', 1000)", tx1.tx_id)
        tx1.commit()
        
        # 事务2：更新记录（未提交）
        tx2 = Transaction(102, self.concurrency_mgr)
        tx2.query_manager = self.query_manager
        self.query_manager.current_transaction = tx2
        self.sql_parser.execute(self.file_mgr,
            "UPDATE account SET balance = 2000 WHERE id = 1", tx2.tx_id)
        
        # 3. 创建检查点
        checkpoint_data = {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'active_transactions': [tx2.tx_id],
            'tables': ['account']
        }
        self.log_mgr.write_checkpoint(checkpoint_data)
        
        # 4. 模拟系统崩溃
        self._clear_current_state()
        
        # 5. 执行恢复
        recovery_mgr = RecoveryManager(self.log_mgr, self.query_manager)
        recovery_mgr.recover(checkpoint_data)
        
        # 重要修改：在恢复后重新初始化并释放所有锁
        self.concurrency_mgr = ConcurrencyMgr()
        
        # 6. 验证恢复结果
        tx = Transaction(3, self.concurrency_mgr)  # 使用新的并发管理器
        tx.query_manager = self.query_manager
        self.query_manager.current_transaction = tx
        result = self.sql_parser.execute(self.file_mgr,
            "SELECT * FROM account WHERE id = 1", tx.tx_id)
        tx.commit()
        
        # 验证未提交事务的更新被回滚
        self.assertIn("1000", str(result))
        
    def test_checkpoint_recovery(self):
        """测试检查点恢复"""
        # 1. 创建初始数据和检查点
        tx = Transaction(1, self.concurrency_mgr)
        tx.query_manager = self.query_manager
        self.query_manager.current_transaction = tx
        self.sql_parser.execute(self.file_mgr,
            "CREATE TABLE account (id INT, name STRING, balance INT)", tx.tx_id)
        self.sql_parser.execute(self.file_mgr,
            "INSERT INTO account VALUES (1, 'Alice', 1000)", tx.tx_id)
        tx.commit()
        
        checkpoint_data = {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'active_transactions': [],
            'tables': ['account']
        }
        self.log_mgr.write_checkpoint(checkpoint_data)
        
        # 2. 执行更多操作
        tx = Transaction(2, self.concurrency_mgr)
        tx.query_manager = self.query_manager
        self.query_manager.current_transaction = tx
        self.sql_parser.execute(self.file_mgr,
            "INSERT INTO account VALUES (2, 'Bob', 2000)", tx.tx_id)
        tx.commit()
        
        # 3. 模拟崩溃
        self._clear_current_state()
        
        # 4. 恢复到查点
        recovery_mgr = RecoveryManager(self.log_mgr, self.query_manager)
        recovery_mgr.recover(checkpoint_data)
        
        # 5. 验证结果
        tx = Transaction(3, self.concurrency_mgr)
        self.query_manager.current_transaction = tx
        result = self.sql_parser.execute(self.file_mgr,
            "SELECT * FROM account", tx.tx_id)
        tx.commit()
        
        # 验证检查点后的操作被正确恢复
        result_str = str(result)
        self.assertIn("Alice", result_str)
        self.assertIn("Bob", result_str)
        
    def _clear_current_state(self):
        """清理当前状态，模拟系统崩溃"""
        self.file_mgr = FileMgr(self.db_directory)
        self.table_metadata = TableMetadata(self.file_mgr)
        self.query_manager = QueryManager(self.table_metadata, TableScan, self.log_mgr)
        self.sql_parser = SQLParser(self.query_manager)
        self.query_manager.set_sql_parser(self.sql_parser) 

if __name__ == '__main__':
    # 只运行当前文件的测试
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRecovery)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite) 