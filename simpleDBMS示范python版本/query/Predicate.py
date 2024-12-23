from Term import Term
from Schema import Schema
from Scan import Scan
from Plan import Plan
from Constant import Constant


class Predicate:
    """谓词是一系列术语的布尔组合。

    Attributes:
        __terms: 谓词中的术语
    """

    def __init__(self, t: Term = None):
        self.__terms = []
        if t is not None:
            self.__terms.append(t)

    def conjoinWith(self, pred):
        """修改谓词，使其成为自身与指定谓词的合取"""
        self.__terms.extend(pred.__terms)

    def isSatisfied(self, s: Scan) -> bool:
        """如果谓词在指定的扫描中评估为true，则返回true"""
        for t in self.__terms:
            if not t.isSatisfied(s):
                return False
        return True

    def reductionFactor(self, p: Plan) -> int:
        """计算在谓词上选择的程度，

        用于查询优化

        Args:
            :param p: 查询的计划

        Returns:
            :return 整数减少因子
        """
        factor = 1
        for t in self.__terms:
            factor *= t.reductionFactor(p)
        return factor

    def selectSubPred(self, sch: Schema):
        """获取适用于指定模式的子谓词

        Args:
            :param sch: 模式

        Returns:
            :return 适用于模式的子谓词
        """
        result = Predicate()
        for t in self.__terms:
            if t.appliesTo(sch):
                result.__terms.append(t)
        if len(result.__terms) == 0:
            return None
        else:
            return result

    def joinSubPred(self, sch1: Schema, sch2: Schema):
        """返回由适用于两个指定模式的联合，

        但不适用于任何一个模式的术语组成的子谓词。

        Args:
            :param sch1: 第一个模式
            :param sch2: 第二个模式

        Returns:
            :return 其术语适用于两个模式的联合但不适用于任何一个模式的子谓词。
        """
        result = Predicate()
        newsch = Schema()
        newsch.addAll(sch1)
        newsch.addAll(sch2)
        for t in self.__terms:
            if not t.appliesTo(sch1) and not t.appliesTo(sch2) and t.appliesTo(newsch):
                result.__terms.append(t)
        if len(result.__terms) == 0:
            return None
        else:
            return result

    def equatesWithConstant(self, fldname: str) -> Constant | None:
        """确定是否有形式为 "F=c" 的术语

        其中F是指定的字段，c是某个常量。

        Args:
            :param fldname: 字段的名称

        Returns:
            :return 常量或None
        """
        for t in self.__terms:
            c = t.equatesWithConstant(fldname)
            if c is not None:
                return c
        return None

    def equatesWithField(self, fldname: str) -> str | None:
        """确定是否有形式为 "F1=F2" 的术语

        其中F1是指定的字段，F2是另一个字段。

        Args:
            :param fldname: 字段的名称

        Returns:
            :return 另一个字段的名称或None
        """
        for t in self.__terms:
            s = t.equatesWithField(fldname)
            if s is not None:
                return s
        return None

    def __str__(self):
        if not self.__terms:
            return None
        result = str(self.__terms[0])
        for t in self.__terms[1:]:
            result += " and " + str(t)
        return result
