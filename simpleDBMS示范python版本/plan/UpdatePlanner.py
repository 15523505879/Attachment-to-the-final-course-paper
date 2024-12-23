from abc import ABC, abstractmethod
from InsertData import InsertData
from Transaction import Transaction
from DeleteData import DeleteData
from ModifyData import ModifyData
from CreateTableData import CreateTableData
from CreateViewData import CreateViewData
from CreateIndexData import CreateIndexData


class UpdatePlanner(ABC):
    """由SQL插入、删除和修改语句的计划器实现的接口"""

    @abstractmethod
    def executeInsert(self, data: InsertData, tx: Transaction):
        """执行指定的插入语句，并返回受影响的记录数"""
        pass

    @abstractmethod
    def executeDelete(self, data: DeleteData, tx: Transaction):
        """执行指定的删除语句，并返回受影响的记录数"""
        pass

    @abstractmethod
    def executeModify(self, data: ModifyData, tx: Transaction):
        """执行指定的修改语句，并返回受影响的记录数"""
        pass

    @abstractmethod
    def executeCreateTable(self, data: CreateTableData, tx: Transaction):
        """执行指定的创建表语句，并返回受影响的记录数"""
        pass

    @abstractmethod
    def executeCreateView(self, data: CreateViewData, tx: Transaction):
        """执行指定的创建视图语句，并返回受影响的记录数"""
        pass

    @abstractmethod
    def executeCreateIndex(self, data: CreateIndexData, tx: Transaction):
        """执行指定的创建索引语句，并返回受影响的记录数"""
        pass
