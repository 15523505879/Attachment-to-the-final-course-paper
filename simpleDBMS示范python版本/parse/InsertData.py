from typing import List
from Constant import Constant


class InsertData:
    """SQL <i>insert</i> 语句的数据表示。

    Attributes:
        __tblname: 要插入数据的表明
        __flds: 要插入值的字段
        __vals: 要插入的值
    """

    def __init__(self, tblname: str, flds: List[str], vals: List[Constant]):
        self.__tblname = tblname
        self.__flds = flds
        self.__vals = vals

    def tableName(self) -> str:
        """返回受影响的表的名称。"""
        return self.__tblname

    def fields(self) -> List[str]:
        """返回新记录中将指定值的字段的列表"""
        return self.__flds

    def vals(self) -> List[Constant]:
        """返回指定字段的值的列表。

        这个值列表与字段列表之间有一一对应的关系。
        """
        return self.__vals
