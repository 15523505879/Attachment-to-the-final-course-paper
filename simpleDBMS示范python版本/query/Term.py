from Expression import Expression
from Scan import Scan
from Plan import Plan
from Constant import Constant
from Schema import Schema


class Term:
    """Term（术语）是两个表达式之间的比较。

    Attributes:
        __lhs: 左侧值
        __rhs: 右侧值
    """

    def __init__(self, lhs: Expression, rhs: Expression):
        self.__lhs = lhs
        self.__rhs = rhs

    def isSatisfied(self, s: Scan) -> bool:
        """判断两个表达式是否相同"""
        lhsval = self.__lhs.evaluate(s)
        rhsval = self.__rhs.evaluate(s)
        return lhsval == rhsval

    def reductionFactor(self, p: Plan) -> int | float:
        """计算术语对查询输出的记录数减少了多少。

        用于查询优化

        Args:
            :param p: 查询的计划

        Returns:
            :return 整数减少因子
        """
        if self.__lhs.isFieldName() and self.__rhs.isFieldName():
            lhsName = self.__lhs.asFieldName()
            rhsName = self.__rhs.asFieldName()
            return max(p.distinctValues(lhsName), p.distinctValues(rhsName))
        if self.__lhs.isFieldName():
            lhsName = self.__lhs.asFieldName()
            return p.distinctValues(lhsName)
        if self.__rhs.isFieldName():
            rhsName = self.__rhs.asFieldName()
            return p.distinctValues(rhsName)
        if self.__lhs.asConstant() == self.__rhs.asConstant():
            return 1
        else:
            return float('inf')     # 无穷大

    def equatesWithConstant(self, fldname: str) -> Constant | None:
        """确定此术语是否具有形式 "F=c"

        其中F是指定的字段，c是某个常量。
        如果是，则返回该常量

        Args:
            :param fldname: 字段的名称

        Returns:
            :return 常量或None
        """
        if self.__lhs.isFieldName() and self.__lhs.asFieldName() == fldname and not self.__rhs.isFieldName():
            return self.__rhs.asConstant()
        elif self.__rhs.isFieldName() and self.__rhs.asFieldName() == fldname and not self.__lhs.isFieldName():
            return self.__lhs.asConstant()
        else:
            return None

    def equatesWithField(self, fldname: str) -> str | None:
        """确定此术语是否具有形式 "F1=F2"

        其中F1是指定的字段，F2是另一个字段。
        如果是，返回该字段的名称。

        Args:
            :param fldname: 字段的名称

        Returns:
            :return 另一个字段的名称或None
        """
        if self.__lhs.isFieldName() and self.__lhs.asFieldName() == fldname and self.__rhs.isFieldName():
            return self.__rhs.asFieldName()
        elif self.__rhs.isFieldName() and self.__rhs.asFieldName() == fldname and self.__lhs.isFieldName():
            return self.__lhs.asFieldName()
        else:
            return None

    def appliesTo(self, sch: Schema) -> bool:
        """判断术语的两个表达式是否都适用于指定的模式"""
        return self.__lhs.appliesTo(sch) and self.__rhs.appliesTo(sch)

    def __str__(self):
        return f"{str(self.__lhs)}={str(self.__rhs)}"
