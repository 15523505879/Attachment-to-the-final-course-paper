import unittest
import os
import sys
import time
import threading

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from storage_manager import FileMgr
from metadata_manager import TableMetadata
from query_manager import QueryManager
from sql_parser import SQLParser
from log_manager import LogManager
from transaction_manager import Transaction
from concurrency_manager import ConcurrencyMgr
from record_manager import TableScan

class TestConcurrency(unittest.TestCase):
    """测试并发控制功能"""
    
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
        
        # 准备测试数据
        tx = Transaction(1, self.concurrency_mgr)
        self.query_manager.current_transaction = tx
        self.sql_parser.execute(self.file_mgr,
            "CREATE TABLE account (id INT, name STRING, balance INT)", tx.tx_id)
        self.sql_parser.execute(self.file_mgr,
            "INSERT INTO account VALUES (1, 'Alice', 1000)", tx.tx_id)
        self.sql_parser.execute(self.file_mgr,
            "INSERT INTO account VALUES (2, 'Bob', 2000)", tx.tx_id)
        tx.commit()
        
    def test_read_write_conflict(self):
        """测试读写冲突"""
        results = []
        
        def tx1_operation():
            tx = None
            try:
                tx = Transaction(101, self.concurrency_mgr)
                tx.query_manager = self.query_manager
                self.query_manager.current_transaction = tx
                
                print("[TX1] Starting update operation...")
                self.sql_parser.execute(self.file_mgr,
                    "UPDATE account SET balance = balance + 500 WHERE id = 1", tx.tx_id)
                time.sleep(0.1)  # 模拟操作时间
                tx.commit()
                print("[TX1] Update committed")
                results.append(("TX1", "SUCCESS"))
            except Exception as e:
                print(f"[TX1] Error: {str(e)}")
                if tx:
                    tx.rollback()
                results.append(("TX1", "FAILED"))
                
        def tx2_operation():
            tx = None
            try:
                time.sleep(0.05)  # 等待TX1开始
                tx = Transaction(102, self.concurrency_mgr)
                tx.query_manager = self.query_manager
                self.query_manager.current_transaction = tx
                
                print("[TX2] Starting read operation...")
                result = self.sql_parser.execute(self.file_mgr,
                    "SELECT * FROM account WHERE id = 1", tx.tx_id)
                print(f"[TX2] Read result: {result}")
                tx.commit()
                print("[TX2] Read committed")
                results.append(("TX2", "SUCCESS"))
            except Exception as e:
                print(f"[TX2] Error: {str(e)}")
                if tx:
                    tx.rollback()
                results.append(("TX2", "FAILED"))
        
        # 并发执行事务
        t1 = threading.Thread(target=tx1_operation)
        t2 = threading.Thread(target=tx2_operation)
        
        print("\n=== Starting read-write conflict test ===")
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        
        print(f"Test results: {results}")
        success_count = sum(1 for r in results if r[1] == "SUCCESS")
        self.assertLess(success_count, 2, "应该有一个事务失败")
        
    def test_deadlock_prevention(self):
        """测试死锁预防"""
        results = []
        
        def tx1_operation():
            tx = None
            try:
                tx = Transaction(201, self.concurrency_mgr)
                tx.query_manager = self.query_manager
                self.query_manager.current_transaction = tx
                
                print("[TX1] Trying to lock account 1...")
                self.sql_parser.execute(self.file_mgr,
                    "UPDATE account SET balance = balance - 100 WHERE id = 1", tx.tx_id)
                print("[TX1] Acquired lock on account 1")
                time.sleep(0.1)  # 等待TX2锁定账户2
                
                print("[TX1] Trying to lock account 2...")
                self.sql_parser.execute(self.file_mgr,
                    "UPDATE account SET balance = balance + 100 WHERE id = 2", tx.tx_id)
                print("[TX1] Acquired lock on account 2")
                
                tx.commit()
                print("[TX1] Transaction committed")
                results.append(("TX1", "SUCCESS"))
            except Exception as e:
                print(f"[TX1] Error: {str(e)}")
                if tx:
                    tx.rollback()
                results.append(("TX1", "FAILED"))
                
        def tx2_operation():
            tx = None
            try:
                time.sleep(0.05)  # 等待TX1开始
                tx = Transaction(202, self.concurrency_mgr)
                tx.query_manager = self.query_manager
                self.query_manager.current_transaction = tx
                
                print("[TX2] Trying to lock account 2...")
                self.sql_parser.execute(self.file_mgr,
                    "UPDATE account SET balance = balance - 100 WHERE id = 2", tx.tx_id)
                print("[TX2] Acquired lock on account 2")
                time.sleep(0.1)  # 等待TX1锁定账户1
                
                print("[TX2] Trying to lock account 1...")
                self.sql_parser.execute(self.file_mgr,
                    "UPDATE account SET balance = balance + 100 WHERE id = 1", tx.tx_id)
                print("[TX2] Acquired lock on account 1")
                
                tx.commit()
                print("[TX2] Transaction committed")
                results.append(("TX2", "SUCCESS"))
            except Exception as e:
                print(f"[TX2] Error: {str(e)}")
                if tx:
                    tx.rollback()
                results.append(("TX2", "FAILED"))
        
        # 并发执行事务
        t1 = threading.Thread(target=tx1_operation)
        t2 = threading.Thread(target=tx2_operation)
        
        print("\n=== Starting deadlock prevention test ===")
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        
        print(f"Test results: {results}")
        self.assertEqual(len(results), 2, "应该有两个事务完成")
        failed_count = sum(1 for r in results if r[1] == "FAILED")
        self.assertGreater(failed_count, 0, "应该至少有一个事务失败以避免死锁")
        
    def test_concurrent_reads(self):
        """测试并发读取"""
        results = []
        
        def read_operation(tx_id):
            tx = None
            try:
                tx = Transaction(tx_id, self.concurrency_mgr)
                tx.query_manager = self.query_manager
                self.query_manager.current_transaction = tx
                
                print(f"[TX{tx_id}] Starting read operation...")
                result = self.sql_parser.execute(self.file_mgr,
                    "SELECT * FROM account", tx.tx_id)
                print(f"[TX{tx_id}] Read result: {result}")
                
                tx.commit()
                print(f"[TX{tx_id}] Read committed")
                results.append((f"TX{tx_id}", "SUCCESS"))
            except Exception as e:
                print(f"[TX{tx_id}] Error: {str(e)}")
                if tx:
                    tx.rollback()
                results.append((f"TX{tx_id}", "FAILED"))
        
        # 创建多个读取线程
        threads = []
        print("\n=== Starting concurrent reads test ===")
        for i in range(5):
            t = threading.Thread(target=read_operation, args=(300+i,))
            threads.append(t)
            t.start()
        
        # 等待所有线程完成
        for t in threads:
            t.join()
        
        print(f"Test results: {results}")
        success_count = sum(1 for r in results if r[1] == "SUCCESS")
        self.assertEqual(success_count, 5, "所有读取操作应该成功")

if __name__ == '__main__':
    # 只运行当前文件的测试
    suite = unittest.TestLoader().loadTestsFromTestCase(TestConcurrency)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite) 