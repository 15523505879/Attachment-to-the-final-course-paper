from TableMgr import TableMgr
from Transaction import Transaction
from Layout import Layout
from TableScan import TableScan
from StatInfo import StatInfo


class StatMgr:
    """统计管理器

    统计管理器负责保持关于每个表的统计信息。
    该管理器不在数据库中存储此信息。
    相反，它在系统启动时计算这些信息，并定期刷新它们。

    Attributes:
        __tblMgr: 表管理器
        __numcalls: 调用StatInfo的次数
        __tablestats: 表的统计信息
    """

    def __init__(self, tblmgr: TableMgr, tx: Transaction):
        self.__tblMgr = tblmgr
        self.__numcalls = 0
        self.__tablestats = {}
        self.__refreshStatistics(tx)

    def getStatInfo(self, tblname: str, layout: Layout, tx: Transaction) -> StatInfo:
        """获取指定表的统计信息

        Args:
            :param tblname: 表的名称
            :param layout: 表的布局
            :param tx: 调用事务

        Returns:
            :return 表的统计信息
        """
        self.__numcalls += 1
        if self.__numcalls > 100:
            self.__refreshStatistics(tx)
        si = self.__tablestats.get(tblname)
        if si is None:
            si = self.__calcTableStats(tblname, layout, tx)
            self.__tablestats[tblname] = si
        return si

    def __refreshStatistics(self, tx: Transaction):
        """重新计算表的成本值"""
        self.__tablestats = {}
        self.__numcalls = 0
        tcatlayout = self.__tblMgr.getLayout("tblcat", tx)
        tcat = TableScan(tx, "tblcat", tcatlayout)
        while tcat.next():
            tblname = tcat.getString("tblname")
            layout = self.__tblMgr.getLayout(tblname, tx)
            si = self.__calcTableStats(tblname, layout, tx)
            self.__tablestats[tblname] = si
        tcat.close()

    def __calcTableStats(self, tblname: str, layout: Layout, tx: Transaction) -> StatInfo:
        """计算表的统计信息"""
        numRecs = 0
        numblocks = 0
        ts = TableScan(tx, tblname, layout)
        while ts.next():
            numRecs += 1
            numblocks = ts.getRid().blockNumber() + 1
        ts.close()
        return StatInfo(numblocks, numRecs)
