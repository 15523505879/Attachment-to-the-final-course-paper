from Expression import Expression
from Predicate import Predicate


class ModifyData:
    """SQL <i>update</i> 语句的数据表示。

    Attributes:
        __tblname: 受影响的表名
        __fldname: 被修改的字段
        __newval: 字段的新值
        __pred: 返回描述哪些记录应该被修改的谓词
    """

    def __init__(self, tblname: str, fldname: str, newval: Expression, pred: Predicate):
        self.__tblname = tblname
        self.__fldname = fldname
        self.__newval = newval
        self.__pred = pred

    def tableName(self) -> str:
        """返回受影响的表的名称。"""
        return self.__tblname

    def targetField(self) -> str:
        """返回将要修改值的字段名"""
        return self.__fldname

    def newValue(self) -> Expression:
        """返回一个表达式"""
        return self.__newval

    def pred(self) -> Predicate:
        """返回描述哪些记录应该被修改的谓词"""
        return self.__pred
