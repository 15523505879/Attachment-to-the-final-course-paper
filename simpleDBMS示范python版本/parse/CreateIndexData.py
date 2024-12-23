class CreateIndexData:
    """<i>create index</i> 语句的解析器。

    Attributes:
        __idxname: 索引名
        __tblname: 表名
        __fldname: 字段名
    """

    def __init__(self, idxname: str, tblname: str, fldname: str):
        self.__idxname = idxname
        self.__tblname = tblname
        self.__fldname = fldname

    def indexName(self) -> str:
        """返回索引的名称"""
        return self.__idxname

    def tableName(self) -> str:
        """返回被索引的表的名称"""
        return self.__tblname

    def fieldName(self) -> str:
        """返回被索引的字段的名称 """
        return self.__fldname
