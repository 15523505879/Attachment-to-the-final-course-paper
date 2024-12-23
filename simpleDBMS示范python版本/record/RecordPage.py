from Transaction import Transaction
from BlockID import BlockID
from Layout import Layout


class RecordPage:
    """在块的指定位置存储记录

    Attributes:
        EMPTY: 表示槽未使用的标识符
        USED: 表示槽已使用的标识符
        __tx: 事务
        __blk: 记录所在的块
        __layout: 表的记录结构
    """

    EMPTY = 0
    USED = 1

    def __init__(self, tx: Transaction, blk: BlockID, layout: Layout):
        self.__tx = tx
        self.__blk = blk
        self.__layout = layout
        tx.pin(blk)

    # 返回指定槽位和字段的整数值。
    def getInt(self, slot: int, fldname: str) -> int:
        """获取指定槽位和字段的整数值。

        Args:
            :param slot: 槽位号
            :param fldname: 字段的名称

        Returns:
            :return 存储在该字段中的整数值
        """
        fldpos = self.__offset(slot) + self.__layout.offset(fldname)
        return self.__tx.getInt(self.__blk, fldpos)

    def getString(self, slot: int, fldname: str) -> str:
        """获取指定槽位和字段的字符串值。

        Args:
            :param slot: 槽位号
            :param fldname: 字段的名称

        Returns:
            :return 存储在该字段中的字符串值
        """
        fldpos = self.__offset(slot) + self.__layout.offset(fldname)
        return self.__tx.getString(self.__blk, fldpos)

    def setInt(self, slot: int, fldname: str, val: int):
        """在指定槽位和字段的位置存储整数。

        写入的位置在槽标志后

        Args:
            :param slot: 槽位号
            :param fldname: 字段名称
            :param val: 要存储的整数值
        """
        fldpos = self.__offset(slot) + self.__layout.offset(fldname)
        self.__tx.setInt(self.__blk, fldpos, val, True)

    def setString(self, slot: int, fldname: str, val: str):
        """在指定槽位和字段的位置存储字符串。

        写入的位置在槽标志后

        Args:
            :param slot: 槽位号
            :param fldname: 字段名称
            :param val: 要存储的字符串值
        """
        fldpos = self.__offset(slot) + self.__layout.offset(fldname)
        self.__tx.setString(self.__blk, fldpos, val, True)

    def delete(self, slot: int):
        self.__setFlag(slot, self.EMPTY)

    def format(self):
        """格式化块中的槽

        标志为0表示槽未使用
        """
        slot = 0
        while self.__isValidSlot(slot):
            self.__tx.setInt(self.__blk, self.__offset(slot), self.EMPTY, False)
            sch = self.__layout.schema()
            for fldname in sch.fields():
                fldpos = self.__offset(slot) + self.__layout.offset(fldname)
                if sch.type(fldname) == 4:
                    self.__tx.setInt(self.__blk, fldpos, 0, False)
                else:
                    self.__tx.setString(self.__blk, fldpos, "", False)
            slot += 1

    def nextAfter(self, slot: int) -> int:
        """寻找指定槽后的下一个使用过的槽"""
        return self.__searchAfter(slot, self.USED)

    def insertAfter(self, slot: int) -> int:
        """寻找下一个可使用的槽"""
        newslot = self.__searchAfter(slot, self.EMPTY)
        if newslot >= 0:
            self.__setFlag(newslot, self.USED)
        return newslot

    def block(self) -> BlockID:
        return self.__blk

    def __setFlag(self, slot: int, flag: int):
        """设置记录的空/使用标志"""
        self.__tx.setInt(self.__blk, self.__offset(slot), flag, True)

    def __searchAfter(self, slot: int, flag: int) -> int:
        """寻找下一个指定类型的槽（使用或未使用）

        Args:
            :param slot: 槽位号
            :param flag: 槽的标志（空/已使用）

        Returns:
            :return 如果找到指定标志的槽，则返回其槽号；否则返回-1
        """
        slot += 1
        while self.__isValidSlot(slot):
            if self.__tx.getInt(self.__blk, self.__offset(slot)) == flag:
                return slot
            slot += 1
        return -1

    def __isValidSlot(self, slot: int) -> bool:
        """判断槽是否超出块的大小

        如果未超出块的大小，返回True
        """
        return self.__offset(slot + 1) <= self.__tx.blockSize()

    def __offset(self, slot: int) -> int:
        """返回指定槽的起始位置"""
        return slot * self.__layout.slotSize()
