from UpdatePlanner import UpdatePlanner
from ModifyData import ModifyData
from DeleteData import DeleteData
from Transaction import Transaction
from MetadataMgr import MetadataMgr
from InsertData import InsertData
from TablePlan import TablePlan
from SelectPlan import SelectPlan
from CreateTableData import CreateTableData
from CreateViewData import CreateViewData
from CreateIndexData import CreateIndexData
from BadSyntaxException import BadSyntaxException


class BasicUpdatePlanner(UpdatePlanner):
    """基础的更新规划器"""

    def __init__(self, mdm: MetadataMgr):
        self.__mdm = mdm

    def executeDelete(self, data: DeleteData, tx: Transaction) -> int:
        """删除数据"""
        p = TablePlan(tx, data.tableName(), self.__mdm)
        p = SelectPlan(p, data.pred())
        us = p.open()
        count = 0
        while us.next():
            us.delete()
            count += 1
        us.close()
        return count

    def executeModify(self, data: ModifyData, tx: Transaction) -> int:
        """修改数据"""
        p = TablePlan(tx, data.tableName(), self.__mdm)
        p = SelectPlan(p, data.pred())
        us = p.open()
        count = 0
        while us.next():
            val = data.newValue().evaluate(us)
            # try:
            us.setVal(data.targetField(), val)
            # except:
            #     raise BadSyntaxException()
            count += 1
        us.close()
        return count

    def executeInsert(self, data: InsertData, tx: Transaction) -> int:
        """插入数据"""
        p = TablePlan(tx, data.tableName(), self.__mdm)
        us = p.open()
        us.insert()
        iterVals = iter(data.vals())
        for fldname in data.fields():
            val = next(iterVals)
            # try:
            us.setVal(fldname, val)
            # except:
            #     raise BadSyntaxException()
        us.close()
        return 1

    def executeCreateTable(self, data: CreateTableData, tx: Transaction) -> int:
        """创建表"""
        self.__mdm.createTable(data.tableName(), data.newSchema(), tx)
        return 0

    def executeCreateView(self, data: CreateViewData, tx: Transaction) -> int:
        """创建视图"""
        self.__mdm.createView(data.viewName(), data.viewDef(), tx)
        return 0

    def executeCreateIndex(self, data: CreateIndexData, tx: Transaction) -> int:
        """创建索引"""
        self.__mdm.createIndex(data.indexName(), data.tableName(), data.fieldName(), tx)
        return 0
