from ProductScan import ProductScan
from Schema import Schema
from Plan import Plan


class ProductPlan(Plan):
    """与<i>product</i>关系代数运算符相对应的查询计划类"""

    def __init__(self, p1: Plan, p2: Plan):
        self.__p1 = p1
        self.__p2 = p2
        self.__schema = Schema()
        self.__schema.addAll(p1.schema())
        self.__schema.addAll(p2.schema())

    def open(self) -> ProductScan:
        """为此查询创建一个product扫描"""
        s1 = self.__p1.open()
        s2 = self.__p2.open()
        return ProductScan(s1, s2)

    def blocksAccessed(self) -> int:
        """估计product中的块访问次数"""
        return self.__p1.blocksAccessed() + (self.__p1.recordsOutput() * self.__p2.blocksAccessed())

    def recordsOutput(self) -> int:
        """估计product中的输出记录数"""
        return self.__p1.recordsOutput() * self.__p2.recordsOutput()

    def distinctValues(self, fldname: str) -> int:
        """估计product中字段值的不同数量"""
        if self.__p1.schema().hasField(fldname):
            return self.__p1.distinctValues(fldname)
        else:
            return self.__p2.distinctValues(fldname)

    def schema(self) -> Schema:
        """返回product的模式，即底层查询模式的联合"""
        return self.__schema
