from sqlite3 import Error
from Plan import Plan
from EmbeddedConnection import EmbeddedConnection
from EmbeddedMetaData import EmbeddedMetaData


class EmbeddedResultSet:
    """ResultSet的嵌入式实现

    Attributes:
        __s: 表扫描
        __sch: 表模式
        __conn: 服务器连接
    """

    def __init__(self, plan: Plan, conn: EmbeddedConnection):
        self.__s = plan.open()
        self.__sch = plan.schema()
        self.__conn = conn

    def next(self) -> bool:
        """移动到结果集中的下一条记录，

        通过移动到保存的扫描中的下一条记录实现。"""
        try:
            return self.__s.next()
        except RuntimeError as e:
            self.__conn.rollback()
            raise Error(e)

    def getInt(self, fldname: str) -> int:
        """获取指定字段的整数值"""
        try:
            fldname = fldname.lower()
            return self.__s.getInt(fldname)
        except RuntimeError as e:
            self.__conn.rollback()
            raise Error(e)

    def getString(self, fldname: str) -> str:
        """获取指定字段的字符串值"""
        try:
            fldname = fldname.lower()
            return self.__s.getString(fldname)
        except RuntimeError as e:
            self.__conn.rollback()
            raise Error(e)

    def getMetaData(self) -> EmbeddedMetaData:
        """获取结果集的元数据"""
        return EmbeddedMetaData(self.__sch)

    def close(self):
        """通过关闭其扫描并提交来关闭结果集"""
        self.__s.close()
        self.__conn.commit()
