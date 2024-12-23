from typing import List, Collection
from Predicate import Predicate


class QueryData:
    """SQL <i>select</i> 语句的数据表示。

    Attributes:
        __fields: select的字段
        __tables: from中的表
        __pred: 描述输出表中应该有哪些记录的谓词
    """

    def __init__(self, fields: List[str], tables: Collection[str], pred: Predicate):
        self.__fields = fields
        self.__tables = tables
        self.__pred = pred

    def fields(self) -> List[str]:
        """返回在 select 子句中提到的字段"""
        return self.__fields

    def tables(self) -> Collection[str]:
        """返回在 from 子句中提到的表"""
        return self.__tables

    def pred(self) -> Predicate:
        """返回描述输出表中应该有哪些记录的谓词"""
        return self.__pred

    def __str__(self):
        result = "select "
        for fldname in self.__fields:
            result += fldname + ", "
        result = result[0:-2] # 去掉最后的逗号
        result += " from "
        for tblname in self.__tables:
            result += tblname + ", "
        result = result[0:-2]  # 去掉最后的逗号
        predstring = self.__pred.__str__()
        if predstring is not None:
            result += " where " + predstring
        return result
