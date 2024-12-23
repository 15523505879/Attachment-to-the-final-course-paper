class Schema:
    """表的记录模式

    一个模式包含表的每个字段的名称和类型，
    以及每个varchar字段的长度。

    Attributes:
        __fields: 字段名
        __info: 具体字段信息，包括字段的类型和长度
    """

    def __init__(self):
        self.__fields = []
        self.__info = {}

    def addField(self, fldname: str, type: int, length: int):
        """向模式添加一个具有指定名称、类型和长度的字段。

        如果类型为整数型，则长度值无关紧要。

        Args:
            :param fldname: 字段名
            :param type: 字段类型
            :param length: 字段长度
        """
        self.__fields.append(fldname)
        self.__info[fldname] = self.FieldInfo(type, length)

    def addIntField(self, fldname: str):
        """向模式添加一个整数字段"""
        self.addField(fldname, 4, 0)

    def addStringField(self, fldname: str, length: int):
        """向模式添加一个字符串字段"""
        self.addField(fldname, 12, length)

    def add(self, fldname: str, sch):
        """向模式添加一个字段，该字段具有与另一个模式中相应字段相同的类型和长度。

        Args:
            :param fldname: 字段名
            :param sch: 另一个模式的引用
        """
        type = sch.type(fldname)
        length = sch.length(fldname)
        self.addField(fldname, type, length)

    def addAll(self, sch):
        """将指定模式中的所有字段添加到当前模式中。"""
        for fldname in sch.__fields:
            self.add(fldname, sch)

    def fields(self) -> list:
        """返回包含模式中每个字段的名称的集合。"""
        return self.__fields

    def hasField(self, fldname: str) -> bool:
        """判断模式中是否含有指定字段

        如果指定字段在模式中则返回True
        """
        return fldname in self.__fields

    def type(self, fldname: str) -> int:
        """返回指定字段的类型"""
        if fldname in self.__info:
            return self.__info.get(fldname).type
        else:
            raise RuntimeError("field " + fldname + " not found.")

    def length(self, fldname: str) -> int:
        """返回指定字段的长度

        如果不是字符串型，则长度为定义，为0
        """
        if fldname in self.__info:
            return self.__info.get(fldname).length
        else:
            raise RuntimeError("field " + fldname + " not found.")

    class FieldInfo:
        """字段

        Attributes:
            type: 字段的类型
            length: 字段的长度
        """
        def __init__(self, type: int, length: int):
            self.type = type
            self.length = length
