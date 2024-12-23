from LogMgr import LogMgr
from BufferMgr import BufferMgr
from Buffer import Buffer
from StartRecord import StartRecord
from CommitRecord import CommitRecord
from RollbackRecord import RollbackRecord
from LogRecord import LogRecord
from SetIntRecord import SetIntRecord
from SetStringRecord import SetStringRecord
from Transaction import Transaction


class RecoveryMgr:
    """恢复管理器

    每个事务都有自己的恢复管理器

    Attributes:
        __tx: 指定的事务
        __txnum: 指定事务的事务号
        __lm: 日志管理器
        __bm: 缓冲区管理器
    """

    def __init__(self, tx: Transaction, txnum: int, lm: LogMgr, bm: BufferMgr):
        self.__tx = tx
        self.__txnum = txnum
        self.__lm = lm
        self.__bm = bm
        StartRecord.writeToLog(lm, txnum)

    def commit(self):
        """向日志写入提交记录，并更新到磁盘"""
        self.__bm.flushAll(self.__txnum)
        lsn = CommitRecord.writeToLog(self.__lm, self.__txnum)
        self.__lm.flush(lsn)

    def rollback(self):
        """向日志写入回滚记录，并更新到磁盘"""
        self.__doRollback()
        self.__bm.flushAll(self.__txnum)
        lsn = RollbackRecord.writeToLog(self.__lm, self.__txnum)
        self.__lm.flush(lsn)

    def recover(self):
        """从日志中恢复未完成的事务"""
        self.__doRecover()
        self.__bm.flushAll(self.__txnum)
        lsn = RollbackRecord.writeToLog(self.__lm, self.__txnum)
        self.__lm.flush(lsn)

    def setInt(self, buff: Buffer, offset: int) -> int:
        """向日志写入SET_INT记录

        Args:
            :param buff: 日志缓冲区
            :param offset: 写入的位置

        Returns:
            :return SET_INT记录的日志号
        """
        oldValue = buff.contents().getInt(offset)
        blk = buff.block()
        return SetIntRecord.writeToLog(self.__lm, self.__txnum, blk, offset, oldValue)

    def setString(self, buff: Buffer, offset: int) -> int:
        """向日志写入SET_STRING记录

        Args:
            :param buff: 日志缓冲区
            :param offset: 写入的位置

        Returns:
            :return SET_STRING记录的日志号
        """
        oldValue = buff.contents().getString(offset)
        blk = buff.block()
        return SetStringRecord.writeToLog(self.__lm, self.__txnum, blk, offset, oldValue)

    def __doRollback(self):
        """回滚事务

        直到找到START记录为止，对事务的每个日志记录调用undo()
        """
        iter = self.__lm.iterator()
        while iter.hasNext():
            bytes = iter.next()
            rec = LogRecord.createLogRecord(bytes)
            if rec.txNumber() == self.__txnum:
                if rec.op() == LogRecord.START:
                    return
                rec.undo(self.__tx)

    def __doRecover(self):
        """完整的数据库恢复

        没找到一个未完成的日志记录则调用undo(), 直到遇到CHECKPOINT记录或日志结尾为止
        """
        finishedTxs = []
        iter = self.__lm.iterator()
        while iter.hasNext():
            bytes = iter.next()
            rec = LogRecord.createLogRecord(bytes)
            if rec.op() == LogRecord.CHECKPOINT:
                return
            if rec.op() == LogRecord.COMMIT or rec.op() == LogRecord.ROLLBACK:
                finishedTxs.append(rec.txNumber())
            elif rec.txNumber() not in finishedTxs:
                rec.undo(self.__tx)


