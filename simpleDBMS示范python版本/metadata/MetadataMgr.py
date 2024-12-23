from typing import Dict
from Transaction import Transaction
from TableMgr import TableMgr
from ViewMgr import ViewMgr
from StatMgr import StatMgr
from IndexInfo import IndexInfo
from IndexMgr import IndexMgr
from Schema import Schema
from Layout import Layout
from StatInfo import StatInfo


class MetadataMgr:
    """元数据管理器

    Attributes:
        __tblmgr: 表管理器
        __viewmgr: 视图管理器
        __statmgr: 统计信息管理器
        __idxmgr: 索引管理器
    """

    def __init__(self, isnew: bool, tx: Transaction):
        self.__tblmgr = TableMgr(isnew, tx)
        self.__viewmgr = ViewMgr(isnew, self.__tblmgr, tx)
        self.__statmgr = StatMgr(self.__tblmgr, tx)
        self.__idxmgr = IndexMgr(isnew, self.__tblmgr, self.__statmgr, tx)

    def createTable(self, tblname: str, sch: Schema, tx: Transaction):
        """创建一个具有指定名称和模式的新表"""
        self.__tblmgr.createTable(tblname, sch, tx)

    def getLayout(self, tblname: str, tx: Transaction) -> Layout:
        """获取指定表的布局"""
        return self.__tblmgr.getLayout(tblname, tx)

    # def getTableNames(self, tx: Transaction):
    #     return self.__tblmgr.getTableNames(tx)

    def createView(self, viewname: str, viewdef: str, tx: Transaction):
        """创建视图"""
        self.__viewmgr.createView(viewname, viewdef, tx)

    def getViewDef(self, viewname: str, tx: Transaction) -> str:
        """获取视图的定义语句"""
        return self.__viewmgr.getViewDef(viewname, tx)

    def createIndex(self, idxname: str, tblname: str, fldname: str, tx: Transaction):
        """为指定字段创建指定类型的索引"""
        self.__idxmgr.createIndex(idxname, tblname, fldname, tx)

    def getIndexInfo(self, tblname: str, tx: Transaction) -> Dict[str, IndexInfo]:
        """获取包含指定表上所有索引的索引信息的映射"""
        return self.__idxmgr.getIndexInfo(tblname, tx)

    def getStatInfo(self, tblname: str, layout: Layout, tx: Transaction) -> StatInfo:
        """获取指定表的统计信息"""
        return self.__statmgr.getStatInfo(tblname, layout, tx)
