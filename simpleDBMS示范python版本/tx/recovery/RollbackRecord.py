from LogRecord import LogRecord
from Page import Page
from Transaction import Transaction
from LogMgr import LogMgr


class RollbackRecord(LogRecord):
    """ROLLBACK 日志记录

    Attributes:
        __txnum: 指定事务的事务号
    """

    def __init__(self, p: Page):
        tpos = 4
        self.__txnum = p.getInt(tpos)

    def op(self) -> int:
        return LogRecord.ROLLBACK

    def txNumber(self) -> int:
        return self.__txnum

    def undo(self, tx: Transaction):
        pass

    def __str__(self):
        return f"<ROLLBACK {str(self.__txnum)}>"

    @staticmethod
    def writeToLog(lm: LogMgr, txnum: int) -> int:
        """将ROLLBACK记录写入日志

        该日志记录包含ROLLBACK操作符，后跟事务ID

        Args:
            :param lm: 日志管理器
            :param txnum: 事务号

        Returns:
            :return 最后一个日志值的LSN
        """
        rec = bytes(2 * 4)
        p = Page(rec)
        p.setInt(0, LogRecord.ROLLBACK)
        p.setInt(4, txnum)
        rec = p.contents()
        return lm.append(rec)
