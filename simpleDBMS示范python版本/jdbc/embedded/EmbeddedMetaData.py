from Schema import Schema


class EmbeddedMetaData:
    """元数据的嵌入式实现

    Attributes:
        __sch: 模式
    """

    def __init__(self, sch: Schema):
        self.__sch = sch

    def getColumnCount(self) -> int:
        """获取字段列表的大小"""
        return len(self.__sch.fields())

    def getColumnName(self, column: int) -> str:
        """获取指定列号的字段名"""
        return self.__sch.fields()[column - 1]

    def getColumnType(self, column: int) -> int:
        """获取指定列的类型"""
        fldname = self.getColumnName(column)
        return self.__sch.type(fldname)

    def getColumnDisplaySize(self, column: int) -> int:
        """获取显示指定列所需的字符数

        对于字符串类型字段，该方法简单地查找模式中的字段长度并返回。
        对于整数类型字段，方法决定整数为6个字符
        """
        fldname = self.getColumnName(column)
        fldtype = self.__sch.type(fldname)
        fldlength = 6 if fldtype == 4 else self.__sch.length(fldname)
        return max(len(fldname), fldlength) + 1
