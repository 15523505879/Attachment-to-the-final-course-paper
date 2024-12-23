from Schema import Schema


class CreateTableData:
    """SQL <i>create table</i> 语句的数据表示。

    Attributes:
        __tblname: 表名
        __sch: 表的模式
    """

    def __init__(self, tblname: str, sch: Schema):
        self.__tblname = tblname
        self.__sch = sch

    def tableName(self) -> str:
        """返回新表的名称"""
        return self.__tblname

    def newSchema(self) -> Schema:
        """返回新表的模式"""
        return self.__sch
