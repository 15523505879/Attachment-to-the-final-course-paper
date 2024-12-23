from TableMgr import TableMgr
from Transaction import Transaction
from Schema import Schema
from TableScan import TableScan


class ViewMgr:
    """视图管理

    Attributes:
        __MAX_VIEWDEF: 视图定义的最大长度
        tblMgr: 表管理器
    """

    __MAX_VIEWDEF = 100

    def __init__(self, isNew: bool, tblMgr: TableMgr, tx: Transaction):
        self.tblMgr = tblMgr
        if isNew:
            sch = Schema()
            sch.addStringField("viewname", tblMgr.MAX_NAME)
            sch.addStringField("viewdef", self.__MAX_VIEWDEF)
            tblMgr.createTable("viewcat", sch, tx)

    def createView(self, vname: str, vdef: str, tx: Transaction):
        """创建视图

        Args:
            :param vname: 视图名
            :param vdef: 视图的定义
            :param tx: 创建视图的事务
        """
        layout = self.tblMgr.getLayout("viewcat", tx)
        ts = TableScan(tx, "viewcat", layout)
        ts.insert()
        ts.setString("viewname", vname)
        ts.setString("viewdef", vdef)
        ts.close()

    def getViewDef(self, vname: str, tx: Transaction) -> str:
        """获取视图的定义语句"""
        result = None
        layout = self.tblMgr.getLayout("viewcat", tx)
        ts = TableScan(tx, "viewcat", layout)
        while ts.next():
            if ts.getString("viewname") == vname:
                result = ts.getString("viewdef")
                break
        ts.close()
        return result
