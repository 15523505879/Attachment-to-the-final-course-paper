from LogRecord import LogRecord
from Page import Page
from Transaction import Transaction
from LogMgr import LogMgr


class StartRecord(LogRecord):
    """START日志记录"""

    def __init__(self, p: Page):
        tpos = 4
        self.__txnum = p.getInt(tpos)

    def op(self) -> int:
        return LogRecord.START

    def txNumber(self) -> int:
        return self.__txnum

    def undo(self, tx: Transaction):
        pass

    def __str__(self):
        return f"<START {str(self.__txnum)}>"

    @staticmethod
    def writeToLog(lm: LogMgr, txnum: int) -> int:
        """将START记录写入日志

        该日志记录包含START操作符，后跟事务号

        Args:
            :param lm: 日志管理器
            :param txnum: 指定事务的事务号

        Returns:
            :return 上一个日志值的LSN
        """
        rec = bytes(2 * 4)
        p = Page(rec)
        p.setInt(0, LogRecord.START)
        p.setInt(4, txnum)
        rec = p.contents()
        return lm.append(rec)
