from UpdateScan import UpdateScan
from Transaction import Transaction
from Layout import Layout
from RID import RID
from RecordPage import RecordPage
from BlockID import BlockID
from Constant import Constant
from BadSyntaxException import BadSyntaxException


class TableScan(UpdateScan):
    """表扫描

    一个TableScan保存当前块的记录页

    Attributes:
        __rp: 记录页
        __currentslot: 当前槽
        __tx: 事务
        __layout: 记录结构
        __filename: 表名
    """

    def __init__(self, tx: Transaction, tblname: str, layout: Layout):
        self.__tx = tx
        self.__layout = layout
        self.__filename = tblname + ".tbl"
        self.__rp = None
        self.__currentslot = None
        if tx.size(self.__filename) == 0:
            self.__moveToNewBlock()
        else:
            self.__moveToBlock(0)

    def beforeFirst(self):
        """将扫描位置移到第一个块之前"""
        self.__moveToBlock(0)

    def next(self) -> bool:
        """寻找下一个有记录的槽

        将扫描移到下一条记录

        Returns:
            :return 如果存在下一条记录则返回True
        """
        self.__currentslot = self.__rp.nextAfter(self.__currentslot)
        while self.__currentslot < 0:
            if self.__atLastBlock():
                return False
            self.__moveToBlock(self.__rp.block().number() + 1)
            self.__currentslot = self.__rp.nextAfter(self.__currentslot)
        return True

    def getInt(self, fldname: str) -> int:
        """获取记录中指定字段的整数值"""
        return self.__rp.getInt(self.__currentslot, fldname)

    def getString(self, fldname: str) -> str:
        """获取记录中指定字段的字符串值"""
        return self.__rp.getString(self.__currentslot, fldname)

    def getVal(self, fldname: str) -> Constant:
        """获取记录中指定字段的值, 以常量形式表示"""
        if self.__layout.schema().type(fldname) == 4:
            return Constant(self.getInt(fldname))
        else:
            return Constant(self.getString(fldname))

    def hasField(self, fldname: str) -> bool:
        return self.__layout.schema().hasField(fldname)

    def close(self):
        if self.__rp is not None:
            self.__tx.unpin(self.__rp.block())

    def setInt(self, fldname: str, val: int):
        """将整数值插入指定字段"""
        self.__rp.setInt(self.__currentslot, fldname, val)

    def setString(self, fldname: str, val: str):
        """将字符串值插入指定字段"""
        self.__rp.setString(self.__currentslot, fldname, val)

    def setVal(self, fldname: str, val: Constant):
        """修改指定字段值"""
        if self.__layout.schema().type(fldname) == 4:
            self.setInt(fldname, val.asInt())
        else:
            self.setString(fldname, val.asString())
        # elif self.__layout.schema().length(fldname) >= len(val.asString()):
        #     self.setString(fldname, val.asString())
        # else:
        #     raise BadSyntaxException()

    def insert(self):
        """找到一个可用的槽

        如果块内没有更多的块，则移动到下一个块。
        """
        self.__currentslot = self.__rp.insertAfter(self.__currentslot)
        while self.__currentslot < 0:
            if self.__atLastBlock():
                self.__moveToNewBlock()
            else:
                self.__moveToBlock(self.__rp.block().number() + 1)
            self.__currentslot = self.__rp.insertAfter(self.__currentslot)

    def delete(self):
        """删除当前槽的记录"""
        self.__rp.delete(self.__currentslot)

    def moveToRid(self, rid: RID):
        """将扫描移动到具有指定标识符的记录"""
        self.close()
        blk = BlockID(self.__filename, rid.blockNumber())
        self.__rp = RecordPage(self.__tx, blk, self.__layout)
        self.__currentslot = rid.slot()

    def getRid(self) -> RID:
        """获取当前记录的表示符

        表示符的第一位为块号，第二位为槽号。
        """
        return RID(self.__rp.block().number(), self.__currentslot)

    def __moveToBlock(self, blknum: int):
        """移动到指定的磁盘块"""
        self.close()
        blk = BlockID(self.__filename, blknum)
        self.__rp = RecordPage(self.__tx, blk, self.__layout)
        self.__currentslot = -1

    def __moveToNewBlock(self):
        """添加新的块，并格式化块内的槽"""
        self.close()
        blk = self.__tx.append(self.__filename)
        self.__rp = RecordPage(self.__tx, blk, self.__layout)
        self.__rp.format()
        self.__currentslot = -1

    def __atLastBlock(self) -> bool:
        """判断是否为最后一个块"""
        return self.__rp.block().number() == self.__tx.size(self.__filename) - 1


