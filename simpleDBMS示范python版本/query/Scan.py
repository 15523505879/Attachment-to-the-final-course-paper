from abc import ABC, abstractmethod


class Scan(ABC):
    """该接口将由每个查询扫描实现。

    每个关系代数运算符都有一个对应的Scan类。
    """

    @abstractmethod
    def beforeFirst(self):
        """将扫描定位在第一条记录之前。

        后续调用next()将返回第一条记录。
        """
        pass

    @abstractmethod
    def next(self):
        """将扫描移动到下一条记录。"""
        pass

    @abstractmethod
    def getInt(self, fldname: str):
        """返回当前记录中指定整数字段的值。"""
        pass

    @abstractmethod
    def getString(self, fldname: str):
        """返回当前记录中指定字符串字段的值。"""
        pass

    @abstractmethod
    def getVal(self, fldname: str):
        """返回当前记录中指定字段的值。"""
        pass

    @abstractmethod
    def hasField(self, fldname: str):
        """如果扫描具有指定的字段，则返回true。"""
        pass

    @abstractmethod
    def close(self):
        """关闭扫描及其子扫描（如果有的话）。"""
        pass
