from Page import Page
from Schema import Schema


class Layout:
    """记录结构的描述

    包含表中每个字段的名称、类型、长度和偏移量。

    Attributes:
        __schema: 表记录的模式
        __offsets: 记录内字段的偏移量
        __slotsize: 槽的大小
    """

    def __init__(self, schema: Schema, offsets: dict[str, int] = None, slotsize: int = None):
        self.__schema = schema
        if offsets is not None and slotsize is not None:
            """从指定的元数据创建Layout对象
            从目录中检索元数据时使用
            """
            self.__offsets = offsets
            self.__slotsize = slotsize
        else:
            """从模式中创建一个Layout对象
            在创建表时使用
            """
            self.__offsets = {}
            pos = 4
            for fldname in schema.fields():
                self.__offsets[fldname] = pos
                pos += self.__lengthInBytes(fldname)
            self.__slotsize = pos

    def schema(self) -> Schema:
        """返回表记录的模式"""
        return self.__schema

    def offset(self, fldname: str) -> int:
        """返回记录中指定字段的偏移量。"""
        return self.__offsets.get(fldname)

    def slotSize(self) -> int:
        """返回槽的大小，以字节为单位。"""
        return self.__slotsize

    def __lengthInBytes(self, fldname: str) -> int:
        fldtype = self.__schema.type(fldname)
        if fldtype == 4:
            return 4
        else:
            return Page.maxLength(self.__schema.length(fldname))
