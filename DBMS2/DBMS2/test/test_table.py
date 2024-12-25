import unittest
import os
import sys

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

class TestTable(unittest.TestCase):
    """测试数据库表的创建和管理功能"""
    
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

    def test_create_table(self):
        """测试创建表"""
        tx = Transaction(1, self.concurrency_mgr)
        self.query_manager.current_transaction = tx
        
        # 1. 创建简单表
        result = self.sql_parser.execute(self.file_mgr,
            "CREATE TABLE student (id INT, name STRING)", tx.tx_id)
        self.assertTrue("created successfully" in str(result))
        
        # 验证表是否存在
        tables = self.table_metadata.list_tables()
        self.assertIn("student", tables)
        
        # 验证字段信息
        fields = self.table_metadata.get_table_fields("student")
        self.assertEqual(len(fields), 2)
        self.assertEqual(fields[0][0], "id")
        self.assertEqual(fields[0][1], "INT")
        self.assertEqual(fields[1][0], "name")
        self.assertEqual(fields[1][1], "STRING")
        
        tx.commit()
        
    def test_create_complex_table(self):
        """测试创建复杂表"""
        tx = Transaction(1, self.concurrency_mgr)
        self.query_manager.current_transaction = tx
        
        # 创建包含多个字段的表
        result = self.sql_parser.execute(self.file_mgr,
            "CREATE TABLE employee (id INT, name STRING, age INT, salary INT)", tx.tx_id)
        self.assertTrue("created successfully" in str(result))
        
        # 验证表是否存在
        tables = self.table_metadata.list_tables()
        self.assertIn("employee", tables)
        
        # 验证字段信息
        fields = self.table_metadata.get_table_fields("employee")
        self.assertEqual(len(fields), 4)
        self.assertEqual(fields[0][0], "id")
        self.assertEqual(fields[2][0], "age")
        self.assertEqual(fields[3][1], "INT")
        
        tx.commit()
        
    def test_duplicate_table(self):
        """测试重复创建表"""
        tx = Transaction(1, self.concurrency_mgr)
        self.query_manager.current_transaction = tx
        
        # 第一次创建表
        result1 = self.sql_parser.execute(self.file_mgr,
            "CREATE TABLE test (id INT)", tx.tx_id)
        self.assertTrue("created successfully" in str(result1))
        
        # 尝试重复创建
        result2 = self.sql_parser.execute(self.file_mgr,
            "CREATE TABLE test (id INT)", tx.tx_id)
        self.assertTrue("already exists" in str(result2).lower())
        
        tx.commit()

if __name__ == '__main__':
    # 只运行当前文件的测试
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTable)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite) 