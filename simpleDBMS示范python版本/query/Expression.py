import typing
from Constant import Constant
from Scan import Scan
from Schema import Schema


class Expression:
    """与SQL表达式相对应的接口。

    Attributes:
        __val: 常数值
        __fldname: 字段名
    """

    def __init__(self, valOrFldname: typing.Union[Constant, str]):
        if isinstance(valOrFldname, Constant):
            self.__val = valOrFldname
            self.__fldname = None
        else:
            self.__val = None
            self.__fldname = valOrFldname

    def evaluate(self, s: Scan) -> Constant:
        """根据指定扫描的当前记录评估表达式。"""
        return self.__val if self.__val is not None else s.getVal(self.__fldname)

    def isFieldName(self) -> bool:
        """判断是否是字段引用"""
        return self.__fldname is not None

    def asConstant(self) -> Constant:
        """获取常量值"""
        return self.__val

    def asFieldName(self) -> str:
        """获取字段名"""
        return self.__fldname

    def appliesTo(self, sch: Schema) -> bool:
        """确定此表达式中提到的所有字段是否都包含在指定的模式中"""
        return self.__val is not None or sch.hasField(self.__fldname)

    def __str__(self):
        return str(self.__val) if self.__val is not None else str(self.__fldname)
