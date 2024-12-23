from abc import ABC, abstractmethod


class Plan(ABC):
    """每个查询计划实现的接口。

    对于每个关系代数运算符，都有一个Plan类。
    """

    @abstractmethod
    def open(self):
        """打开与此计划相对应的扫描器。

        扫描器将定位在第一条记录之前。
        """
        pass

    @abstractmethod
    def blocksAccessed(self):
        """返回扫描器读取完毕时将发生的块访问次数的估计值。"""
        pass

    @abstractmethod
    def recordsOutput(self):
        """返回查询输出表中记录的估计数量。"""
        pass

    @abstractmethod
    def distinctValues(self, fldname: str):
        """返回查询输出表中指定字段的估计不同值的数量。"""
        pass

    @abstractmethod
    def schema(self):
        """返回查询的模式。"""
        pass
