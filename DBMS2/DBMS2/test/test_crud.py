import unittest
import os
import sys
from pathlib import Path

# 获取项目根目录（DBMS2目录的父目录）
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# 现在直接从当前目录导入
from storage_manager import FileMgr
from metadata_manager import TableMetadata
from query_manager import QueryManager
from sql_parser import SQLParser
from log_manager import LogManager
from transaction_manager import Transaction
from concurrency_manager import ConcurrencyMgr
from record_manager import TableScan

class TestCRUD(unittest.TestCase):
    """测试数据的增删改查功能"""
    
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
        
        # 创建测试表
        tx = Transaction(1, self.concurrency_mgr)
        self.query_manager.current_transaction = tx
        self.sql_parser.execute(self.file_mgr,
            "CREATE TABLE student (id INT, name STRING, age INT)", tx.tx_id)
        tx.commit()

    def test_insert(self):
        """测试插入记录"""
        tx = Transaction(2, self.concurrency_mgr)
        tx.query_manager = self.query_manager
        self.query_manager.current_transaction = tx
        
        # 插入单条记录
        result = self.sql_parser.execute(self.file_mgr,
            "INSERT INTO student VALUES (1, '张三', 20)", tx.tx_id)
        self.assertTrue("inserted" in str(result).lower())
        
        # 验证插入结果
        result = self.sql_parser.execute(self.file_mgr,
            "SELECT * FROM student WHERE id = 1", tx.tx_id)
        self.assertEqual(len(result), 1)
        self.assertIn("张三", str(result))
        self.assertIn("20", str(result))
        
        tx.commit()
        
    def test_update(self):
        """测试更新记录"""
        # 准备数据
        tx = Transaction(2, self.concurrency_mgr)
        tx.query_manager = self.query_manager
        self.query_manager.current_transaction = tx
        self.sql_parser.execute(self.file_mgr,
            "INSERT INTO student VALUES (1, '张三', 20)", tx.tx_id)
        tx.commit()
        
        # 执行更新
        tx = Transaction(3, self.concurrency_mgr)
        tx.query_manager = self.query_manager
        self.query_manager.current_transaction = tx
        result = self.sql_parser.execute(self.file_mgr,
            "UPDATE student SET age = 21 WHERE id = 1", tx.tx_id)
        self.assertTrue("updated" in str(result).lower())
        
        # 验证更新结果
        result = self.sql_parser.execute(self.file_mgr,
            "SELECT * FROM student WHERE id = 1", tx.tx_id)
        self.assertIn("21", str(result))
        
        tx.commit()
        
    def test_delete(self):
        """测试删除记录"""
        # 准备数据
        tx = Transaction(2, self.concurrency_mgr)
        tx.query_manager = self.query_manager
        self.query_manager.current_transaction = tx
        self.sql_parser.execute(self.file_mgr,
            "INSERT INTO student VALUES (1, '张三', 20)", tx.tx_id)
        tx.commit()
        
        # 执行删除
        tx = Transaction(3, self.concurrency_mgr)
        tx.query_manager = self.query_manager
        self.query_manager.current_transaction = tx
        result = self.sql_parser.execute(self.file_mgr,
            "DELETE FROM student WHERE id = 1", tx.tx_id)
        self.assertTrue("deleted" in str(result).lower())
        
        # 验证删除结果
        result = self.sql_parser.execute(self.file_mgr,
            "SELECT * FROM student WHERE id = 1", tx.tx_id)
        self.assertEqual(len(result), 0)
        
        tx.commit() 

if __name__ == '__main__':
    # 只运行当前文件的测试
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCRUD)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite) 