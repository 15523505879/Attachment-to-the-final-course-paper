from QueryPlanner import QueryPlanner
from Plan import Plan
from Transaction import Transaction
from QueryData import QueryData
from Parse import Parser
from ProductPlan import ProductPlan
from TablePlan import TablePlan
from SelectPlan import SelectPlan
from ProjectPlan import ProjectPlan
from MetadataMgr import MetadataMgr


class BasicQueryPlanner(QueryPlanner):
    """基础的查询规划器"""

    def __init__(self, mdm: MetadataMgr):
        self.__mdm = mdm

    # def getTableNames(self, tx):
    #     return self.mdm.getTableNames(tx)

    def createPlan(self, data: QueryData, tx: Transaction) -> Plan:
        """创建查询计划

        首先获取所有表和视图的笛卡尔积；
        然后根据谓词进行选择；
        最后根据字段列表进行投影。
        """
        # 步骤1：为每个提到的表或视图创建计划。
        plans = []
        for tblname in data.tables():
            viewdef = self.__mdm.getViewDef(tblname, tx)
            if viewdef is not None:  # Recursively plan the view.
                parser = Parser(viewdef)
                viewdata = parser.query()
                plans.append(self.createPlan(viewdata, tx))
            else:
                plans.append(TablePlan(tx, tblname, self.__mdm))
        # 步骤2：创建所有表计划的笛卡尔积。
        p = plans.pop(0)
        for nextplan in plans:
            p = ProductPlan(p, nextplan)

        # 步骤3：为谓词添加选择计划。
        p = SelectPlan(p, data.pred())

        # 步骤4：根据字段名称进行投影。
        p = ProjectPlan(p, data.fields())
        return p
