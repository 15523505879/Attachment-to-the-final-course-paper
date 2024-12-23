from Scan import Scan
from Constant import Constant


class ProductScan(Scan):
    """与<i>product</i>关系代数运算符相对应的扫描类

    Attributes:
        __s1: 左扫描(LHS)
        __s2: 右扫描(RHS)
    """

    def __init__(self, s1: Scan, s2: Scan):
        self.__s1 = s1
        self.__s2 = s2
        self.beforeFirst()

    def beforeFirst(self):
        """将扫描定位在第一条记录之前。

        特别地，将LHS扫描定位在其第一条记录上，
        并将RHS扫描定位在其第一条记录之前。
        """
        self.__s1.beforeFirst()
        self.__s1.next()
        self.__s2.beforeFirst()

    def next(self) -> bool:
        """将扫描移到下一条记录。

        如果可能的话，该方法移动到下一个RHS记录。
        否则，它移动到下一个LHS记录和第一个RHS记录。
        如果没有更多的LHS记录，该方法返回false。
        """
        if self.__s2.next():
            return True
        else:
            self.__s2.beforeFirst()
            return self.__s2.next() and self.__s1.next()

    def getInt(self, fldname: str) -> int:
        """返回指定字段的整数值"""
        if self.__s1.hasField(fldname):
            return self.__s1.getInt(fldname)
        else:
            return self.__s2.getInt(fldname)

    def getString(self, fldname: str) -> str:
        """返回指定字段的字符串值"""
        if self.__s1.hasField(fldname):
            return self.__s1.getString(fldname)
        else:
            return self.__s2.getString(fldname)

    def getVal(self, fldname: str) -> Constant:
        """返回指定字段的值"""
        if self.__s1.hasField(fldname):
            return self.__s1.getVal(fldname)
        else:
            return self.__s2.getVal(fldname)

    def hasField(self, fldname: str) -> bool:
        """如果指定字段在任一底层扫描中，则返回true"""
        return self.__s1.hasField(fldname) or self.__s2.hasField(fldname)

    def close(self):
        """关闭两个底层扫描"""
        self.__s1.close()
        self.__s2.close()
