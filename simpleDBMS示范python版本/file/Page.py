import struct
import typing


class Page:
    """页的实现。

    页是一个数据缓冲区。

    Attributes:
        __CHARSET: 字符编码方式。
        __bb: 数据缓冲区。
    """

    __CHARSET = 'utf-8'

    def __init__(self, b: typing.Union[int | bytes]):
        self.__bb = bytearray(b)

    def getInt(self, offset: int) -> int:
        """从指定位置读取整数值。"""
        return struct.unpack_from('!i', self.__bb, offset)[0]

    def setInt(self, offset: int, n: int):
        """将整数值写入指定位置。"""
        struct.pack_into('!i', self.__bb, offset, n)

    def getBytes(self, offset: int) -> bytes:
        """从指定位置读取字节数组。"""
        length = self.getInt(offset)
        return bytes(self.__bb[offset + 4: offset + 4 + length])

    def setBytes(self, offset: int, b: bytes):
        """将字节数组写入指定位置，同时记录数组长度。"""
        self.setInt(offset, len(b))
        self.__bb[offset + 4:offset + 4 + len(b)] = b

    def getString(self, offset: int) -> str:
        """从指定位置读取字符串。"""
        b = self.getBytes(offset)
        return b.decode(self.__CHARSET)

    def setString(self, offset: int, s: str):
        """将字符串写入指定位置。"""
        b = s.encode(self.__CHARSET)  # 将字符串转为字符数组
        self.setBytes(offset, b)

    @staticmethod
    def maxLength(strlen: int) -> int:
        """计算存储指定长度字符串所需的最大字节数。"""
        bytesPerChar = len('A'.encode(Page.__CHARSET))
        return 4 + (strlen * bytesPerChar)

    def contents(self) -> bytearray:
        return self.__bb


if __name__ == "__main__":
    a = Page(50)
    a.setInt(3, 5)
    print(a.getInt(3))
    a.setString(7, "abc")
    print(a.getString(7))
    print(a.getInt(3))

