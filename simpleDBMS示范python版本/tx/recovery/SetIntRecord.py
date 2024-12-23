from LogRecord import LogRecord
from BlockID import BlockID
from Page import Page
from Transaction import Transaction
from LogMgr import LogMgr


class SetIntRecord(LogRecord):
    """SET_INT日志记录

    Attributes:
        __txnum: 指定事务的事务号
        __blk: 对磁盘块的引用
        __offset: 块内偏移量
        __val: 写入的值
    """

    def __init__(self, p: Page):
        tpos = 4
        self.__txnum = p.getInt(tpos)
        fpos = tpos + 4
        filename = p.getString(fpos)
        bpos = fpos + Page.maxLength(len(filename))
        blknum = p.getInt(bpos)
        self.__blk = BlockID(filename, blknum)
        opos = bpos + 4
        self.__offset = p.getInt(opos)
        vpos = opos + 4
        self.__val = p.getInt(vpos)

    def op(self) -> int:
        return LogRecord.SET_INT

    def txNumber(self) -> int:
        return self.__txnum

    def __str__(self):
        return f"<SETINT {str(self.__txnum)} {self.__blk} {str(self.__offset)} {str(self.__val)}>"

    def undo(self, tx: Transaction):
        """将日志记录中保存的值替换指定的数据值

        Args:
            :param tx: 指定的事务
        """
        tx.pin(self.__blk)
        tx.setInt(self.__blk, self.__offset, self.__val, False)
        tx.unpin(self.__blk)

    @staticmethod
    def writeToLog(lm: LogMgr, txnum: int, blk: BlockID, offset: int, val: int) -> int:
        """将SET_INT记录写入日志

        该日志记录包括SET_INT操作符，后跟事务ID，文件名，修改块的编号和偏移量

        Args:
            :param lm: 日志管理器
            :param txnum: 指定的事务号
            :param blk: 对磁盘块的引用
            :param offset: 块内偏移量
            :param val: 写入的值

        Returns:
            :return 最后一个日志的LSN
        """
        tpos = 4
        fpos = tpos + 4
        bpos = fpos + Page.maxLength(len(blk.fileName()))
        opos = bpos + 4
        vpos = opos + 4
        rec = bytes(vpos + 4)
        p = Page(rec)
        p.setInt(0, LogRecord.SET_INT)
        p.setInt(tpos, txnum)
        p.setString(fpos, blk.fileName())
        p.setInt(bpos, blk.number())
        p.setInt(opos, offset)
        p.setInt(vpos, val)
        rec = p.contents()
        return lm.append(rec)

