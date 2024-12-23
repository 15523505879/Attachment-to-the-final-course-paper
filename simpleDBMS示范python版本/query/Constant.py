import typing


class Constant:
    """表示存储在数据库中的值

    Attributes:
        __ival: 整数值
        __sval: 字符串值
    """

    def __init__(self, ivalOrSval: typing.Union[int, str]):
        if isinstance(ivalOrSval, int):
            self.__ival = ivalOrSval
            self.__sval = None
        else:
            self.__ival = None
            self.__sval = ivalOrSval

    def asInt(self) -> int:
        return self.__ival

    def asString(self) -> str:
        return self.__sval

    def __eq__(self, other):
        if isinstance(other, Constant):
            return self.__ival == other.__ival if self.__ival is not None else self.__sval == other.__sval
        return False

    def __lt__(self, other):
        if self.__ival is not None:
            if self.__ival == other.__ival:
                return 0
            return 1 if self.__ival > other.__ival else -1
        elif self.__sval == other.sval:
            return 0
        return 1 if self.__sval > other.sval else -1

    def __hash__(self):
        return hash(self.__ival) if self.__ival is not None else hash(self.__sval)

    def __str__(self):
        return str(self.__ival) if self.__ival is not None else str(self.__sval)
