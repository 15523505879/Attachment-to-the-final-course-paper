from Plan import Plan
from Predicate import Predicate
from SelectScan import SelectScan
from Schema import Schema


class SelectPlan(Plan):
    """与<i>select</i>关系代数运算符相对应的查询计划类"""

    def __init__(self, p: Plan, pred: Predicate):
        self.__p = p
        self.__pred = pred

    def open(self) -> SelectScan:
        """为此查询创建一个select扫描"""
        s = self.__p.open()
        return SelectScan(s, self.__pred)

    def blocksAccessed(self) -> int:
        """估计选择中的块访问次数"""
        return self.__p.blocksAccessed()

    def recordsOutput(self) -> int:
        """估计选择中的输出记录数"""
        return self.__p.recordsOutput() // self.__pred.reductionFactor(self.__p)

    def distinctValues(self, fldname: str) -> int:
        """估计投影中的不同字段值的数量"""
        if self.__pred.equatesWithConstant(fldname) is not None:
            return 1
        else:
            fldname2 = self.__pred.equatesWithField(fldname)
            if fldname2 is not None:
                return min(self.__p.distinctValues(fldname), self.__p.distinctValues(fldname2))
            else:
                return self.__p.distinctValues(fldname)

    def schema(self) -> Schema:
        """返回选择的模式"""
        return self.__p.schema()
