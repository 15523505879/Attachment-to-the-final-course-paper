from QueryPlanner import QueryPlanner
from UpdatePlanner import UpdatePlanner
from Transaction import Transaction
from Plan import Plan
from Parse import Parser
from InsertData import InsertData
from DeleteData import DeleteData
from ModifyData import ModifyData
from CreateTableData import CreateTableData
from CreateIndexData import CreateIndexData
from CreateViewData import CreateViewData


class Planner:
    """执行SQL语句的对象"""

    def __init__(self, qplanner: QueryPlanner, uplanner: UpdatePlanner):
        self.__qplanner = qplanner
        self.__uplanner = uplanner

    def createQueryPlan(self, qry: str, tx: Transaction) -> Plan:
        """使用提供的计划器为SQL选择语句创建计划

        Args:
            :param qry: SQL查询字符串
            :param tx: 事务

        Returns:
            :return 与查询计划对应的扫描
        """
        parser = Parser(qry)
        data = parser.query()
        return self.__qplanner.createPlan(data, tx)
        # if qry.startswith("select"):
        #     data = parser.query()
        #     return self.__qplanner.createPlan(data, tx)
        # elif qry.startswith("show"):
        #     parser.queryTable()
        #     return self.__qplanner.getTableNames(tx)

    def executeUpdate(self, cmd: str, tx: Transaction) -> int:
        """执行SQL插入、删除、修改或创建语句。

        该方法分派到提供的更新计划器的适当方法，具体取决于解析器返回的内容。

        Args:
            :param cmd: SQL更新字符串
            :param tx: 事务

        Returns:
            :return 表示受影响的记录数的整数。
        """
        parser = Parser(cmd)
        data = parser.updateCmd()
        if isinstance(data, InsertData):
            return self.__uplanner.executeInsert(data, tx)
        elif isinstance(data, DeleteData):
            return self.__uplanner.executeDelete(data, tx)
        elif isinstance(data, ModifyData):
            return self.__uplanner.executeModify(data, tx)
        elif isinstance(data, CreateTableData):
            return self.__uplanner.executeCreateTable(data, tx)
        elif isinstance(data, CreateViewData):
            return self.__uplanner.executeCreateView(data, tx)
        elif isinstance(data, CreateIndexData):
            return self.__uplanner.executeCreateIndex(data, tx)
        else:
            return 0
