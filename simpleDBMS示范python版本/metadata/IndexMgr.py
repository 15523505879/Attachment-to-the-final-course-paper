from typing import Dict
from TableMgr import TableMgr
from StatMgr import StatMgr
from Transaction import Transaction
from IndexInfo import IndexInfo
from Schema import Schema
from TableScan import TableScan


class IndexMgr:
    """索引管理器

    Attributes:
        __tblmgr: 表管理器
        __statmgr: 统计信息管理器
        __layout: 索引布局
    """

    def __init__(self, is_new: bool, tblmgr: TableMgr, statmgr: StatMgr, tx: Transaction):
        if is_new:
            sch = Schema()
            sch.addStringField("indexname", TableMgr.MAX_NAME)
            sch.addStringField("tablename", TableMgr.MAX_NAME)
            sch.addStringField("fieldname", TableMgr.MAX_NAME)
            tblmgr.createTable("idxcat", sch, tx)

        self.__tblmgr = tblmgr
        self.__statmgr = statmgr
        self.__layout = tblmgr.getLayout("idxcat", tx)

    def createIndex(self, idxname: str, tblname: str, fldname: str, tx: Transaction):
        """为指定字段创建指定类型的索引。

        为此索引分配唯一的ID，并将其信息存储在idxcat表中。

        Args:
            :param idxname: 索引的名称
            :param tblname: 索引的表名
            :param fldname: 索引的字段名
            :param tx: 调用的事务
        """
        ts = TableScan(tx, "idxcat", self.__layout)
        ts.insert()
        ts.setString("indexname", idxname)
        ts.setString("tablename", tblname)
        ts.setString("fieldname", fldname)
        ts.close()

    def getIndexInfo(self, tblname: str, tx: Transaction) -> Dict[str, IndexInfo]:
        """返回包含指定表上所有索引的索引信息的映射。

        Args:
            :param tblname: 表的名称
            :param tx: 调用的事务

        Returns:
            :return 以字段名为键的IndexInfo对象的映射
        """
        result: Dict[str, IndexInfo] = {}
        ts = TableScan(tx, "idxcat", self.__layout)
        while ts.next():
            if ts.getString("tablename") == tblname:
                idxname = ts.getString("indexname")
                fldname = ts.getString("fieldname")
                tblLayout = self.__tblmgr.getLayout(tblname, tx)
                tblsi = self.__statmgr.getStatInfo(tblname, tblLayout, tx)
                ii = IndexInfo(idxname, fldname, tblLayout.schema(), tx, tblsi)
                result[fldname] = ii
        ts.close()
        return result
