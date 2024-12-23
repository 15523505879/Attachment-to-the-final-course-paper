from Scan import Scan
from Constant import Constant


class ProjectScan(Scan):
    """与<i>project</i>关系代数运算符相对应的扫描类。

    Attributes:
        __s: 底层扫描
        __fieldlist: 字段名称列表
    """

    def __init__(self, s: Scan, fieldlist: list):
        self.__s = s
        self.__fieldlist = fieldlist

    def beforeFirst(self):
        self.__s.beforeFirst()

    def next(self) -> bool:
        return self.__s.next()

    def getInt(self, fldname: str) -> int:
        if self.hasField(fldname):
            return self.__s.getInt(fldname)
        else:
            raise RuntimeError(f"field {fldname} not found")

    def getString(self, fldname: str) -> str:
        if self.hasField(fldname):
            return self.__s.getString(fldname)
        else:
            raise RuntimeError(f"field {fldname} not found")

    def getVal(self, fldname: str) -> Constant:
        if self.hasField(fldname):
            return self.__s.getVal(fldname)
        else:
            raise RuntimeError(f"field {fldname} not found")

    def hasField(self, fldname: str) -> bool:
        return fldname in self.__fieldlist

    def close(self):
        self.__s.close()
