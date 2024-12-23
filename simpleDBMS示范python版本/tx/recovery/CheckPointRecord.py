from Page import Page
from LogRecord import LogRecord
from LogMgr import LogMgr
from Transaction import Transaction


class CheckPointRecord(LogRecord):
    """CHECKPOINT 日志记录"""

    def __init__(self):
        pass

    def op(self) -> int:
        return LogRecord.CHECKPOINT

    def txNumber(self) -> int:
        return -1

    def undo(self, tx: Transaction):
        """不执行任何操作

        因为checkpoint记录不包含任何撤销信息。
        """
        pass

    def __str__(self):
        return "<CHECKPOINT>"

    @staticmethod
    def writeToLog(lm: LogMgr) -> int:
        """将CHECKPOINT记录写入日志

        该日志记录仅包含CHECKPOINT操作符

        Args:
            :param lm: 日志管理器

        Returns:
            :return 上一个日志值的LSN
        """
        rec = bytes(4)
        p = Page(rec)
        p.setInt(0, LogRecord.CHECKPOINT)
        rec = p.contents()
        return lm.append(rec)


