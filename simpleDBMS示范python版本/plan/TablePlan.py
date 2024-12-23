from Plan import Plan
from Transaction import Transaction
from MetadataMgr import MetadataMgr
from TableScan import TableScan
from Schema import Schema


class TablePlan(Plan):
    """与表相对应的查询计划类"""

    def __init__(self, tx: Transaction, tblname: str, md: MetadataMgr):
        self.__tblname = tblname
        self.__tx = tx
        self.__layout = md.getLayout(tblname, tx)
        try:
            self.__si = md.getStatInfo(tblname, self.__layout, tx)
        except:
            raise RuntimeError("table " + tblname + " not found.")

    def open(self) -> TableScan:
        """为此查询创建一个表扫描"""
        return TableScan(self.__tx, self.__tblname, self.__layout)

    def blocksAccessed(self) -> int:
        """估计表的块访问次数"""
        return self.__si.blocksAccessed()

    def recordsOutput(self) -> int:
        """估计表中的记录数"""
        return self.__si.recordsOutput()

    def distinctValues(self, fldname: str) -> int:
        """估计表中字段的不同值的数量"""
        return self.__si.distinctValues()

    def schema(self) -> Schema:
        """确定表的模式"""
        return self.__layout.schema()
