from Predicate import Predicate


class DeleteData:
    """SQL <i>delete</i> 语句的数据表示。

    Attributes:
        __tblname: 受影响的表名
        __pred: 描述哪些记录应该被删除的谓词
    """

    def __init__(self, tblname: str, pred: Predicate):
        self.__tblname = tblname
        self.__pred = pred

    def tableName(self) -> str:
        """返回受影响的表的名称"""
        return self.__tblname

    def pred(self) -> Predicate:
        """返回描述哪些记录应该被删除的谓词"""
        return self.__pred
