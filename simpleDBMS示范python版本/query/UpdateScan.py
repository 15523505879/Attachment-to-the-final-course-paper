from abc import ABC, abstractmethod
from Scan import Scan
from Constant import Constant
from RID import RID


class UpdateScan(Scan, ABC):
    """所有更新扫描实现的接口。"""

    @abstractmethod
    def setVal(self, fldname: str, val: Constant):
        """修改当前记录的字段值。"""
        pass

    @abstractmethod
    def setInt(self, fldname: str, val: int):
        """修改当前记录的字段值。"""
        pass

    @abstractmethod
    def setString(self, fldname: str, val: str):
        """修改当前记录的字段值。"""
        pass

    @abstractmethod
    def insert(self):
        """在扫描中的某个位置插入新记录。"""
        pass

    @abstractmethod
    def delete(self):
        """从扫描中删除当前记录。"""
        pass

    @abstractmethod
    def getRid(self):
        """返回当前记录的标识符。"""
        pass

    @abstractmethod
    def moveToRid(self, rid: RID):
        """将扫描定位到具有指定标识符的当前记录。"""
        pass
