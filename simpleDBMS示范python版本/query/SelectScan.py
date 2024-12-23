from UpdateScan import UpdateScan
from Scan import Scan
from Predicate import Predicate
from Constant import Constant
from RID import RID


class SelectScan(UpdateScan):
    """与<i>select</i>关系代数运算符相对应的扫描类。

    Attributes:
        __s: 底层查询的扫描
        __pred: 选择谓词
    """

    def __init__(self, s: Scan, pred: Predicate):
        self.__s = s
        self.__pred = pred

    def beforeFirst(self):
        self.__s.beforeFirst()

    def next(self) -> bool:
        while self.__s.next():
            if self.__pred.isSatisfied(self.__s):
                return True
        return False

    def getInt(self, fldname: str) -> int:
        return self.__s.getInt(fldname)

    def getString(self, fldname: str) -> str:
        return self.__s.getString(fldname)

    def getVal(self, fldname: str) -> Constant:
        return self.__s.getVal(fldname)

    def hasField(self, fldname: str) -> bool:
        return self.__s.hasField(fldname)

    def close(self):
        self.__s.close()

    def setInt(self, fldname: str, val: int):
        us = self.__s
        us.setInt(fldname, val)

    def setString(self, fldname: str, val: str):
        us = self.__s
        us.setString(fldname, val)

    def setVal(self, fldname: str, val: Constant):
        us = self.__s
        us.setVal(fldname, val)

    def delete(self):
        us = self.__s
        us.delete()

    def insert(self):
        us = self.__s
        us.insert()

    def getRid(self) -> RID:
        us = self.__s
        return us.getRid()

    def moveToRid(self, rid: RID):
        us = self.__s
        us.moveToRid(rid)
