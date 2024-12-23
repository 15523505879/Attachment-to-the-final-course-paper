from BlockID import BlockID
from FileMgr import FileMgr
from LogMgr import LogMgr
from BufferMgr import BufferMgr
from ConcurrencyMgr import ConcurrencyMgr
from BufferList import BufferList


class Transaction:
    """事务管理器

    为客户端提供事务管理。

    Attributes:
        __nextTxNum: 下一个事务号
        __END_OF_FILE: 文件结束标志
        __fm: 文件管理器
        __bm: 缓冲区管理器
        __txnum: 事务号
        __recoveryMgr: 恢复管理器
        __concurMgr: 并发管理器
        __mybuffers: 事务当前固定的缓冲区
    """
    __nextTxNum = 0
    __END_OF_FILE = -1

    def __init__(self, fm: FileMgr, lm: LogMgr, bm: BufferMgr):
        from RecoveryMgr import RecoveryMgr     # 避免循环引用报错。

        self.__fm = fm
        self.__bm = bm
        self.__txnum = self.__nextTxNumber()
        self.__recoveryMgr = RecoveryMgr(self, self.__txnum, lm, bm)
        self.__concurMgr = ConcurrencyMgr()
        self.__mybuffers = BufferList(bm)

    def commit(self):
        """提交当前事务

        刷新所有修改的缓冲区及其日志记录，
        向日志写入提交记录
        释放所有锁，并取消固定任何已固定的缓冲区
        """
        self.__recoveryMgr.commit()
        print("transaction", self.__txnum, "committed")
        self.__concurMgr.release()
        self.__mybuffers.unpinAll()

    def rollback(self):
        """回滚当前事务

        撤销任何修改的值，刷新这些缓冲区，
        向日志写入回滚记录，
        释放所有锁，并取消固定任何已固定的缓冲区。
        """
        self.__recoveryMgr.rollback()
        print("transaction", self.__txnum, "rolled back")
        self.__concurMgr.release()
        self.__mybuffers.unpinAll()

    def recover(self):
        """恢复数据库"""
        self.__bm.flushAll(self.__txnum)
        self.__recoveryMgr.recover()

    def pin(self, blk: BlockID):
        """固定指定的块

        事务为客户端管理缓冲区

        Args:
            :param blk: 对磁盘块的引用。
        """
        self.__mybuffers.pin(blk)

    def unpin(self, blk: BlockID):
        """取消固定指定的块

        Args:
            :param blk: 对磁盘块的引用。
        """
        self.__mybuffers.unpin(blk)

    def getInt(self, blk: BlockID, offset: int) -> int:
        """返回存储在指定块的在指定偏移处的整数值。

        Args:
            :param blk: 对磁盘块的引用。
            :param offset: 块内的字节偏移量。

        Returns:
            :return 存储在该偏移处的整数值
        """
        self.__concurMgr.sLock(blk)
        buff = self.__mybuffers.getBuffer(blk)
        return buff.contents().getInt(offset)

    def getString(self, blk: BlockID, offset: int) -> str:
        """返回存储在指定块的在指定偏移处的字符串值。

        Args:
            :param blk: 对磁盘块的引用。
            :param offset: 块内的字节偏移量。

        Returns:
            :return 存储在该偏移处的字符串值
        """
        self.__concurMgr.sLock(blk)
        buff = self.__mybuffers.getBuffer(blk)
        return buff.contents().getString(offset)

    def setInt(self, blk: BlockID, offset: int, val: int, okToLog: bool):
        """在指定块的指定偏移处存储整数。

        Args:
            :param blk: 对磁盘块的引用。
            :param offset: 块内的字节偏移量
            :param val: 要存储的值
            :param okToLog: 是否写入日志
        """
        self.__concurMgr.xLock(blk)
        buff = self.__mybuffers.getBuffer(blk)
        lsn = -1
        if okToLog:
            lsn = self.__recoveryMgr.setInt(buff, offset)
        p = buff.contents()
        p.setInt(offset, val)
        buff.setModified(self.__txnum, lsn)

    def setString(self, blk: BlockID, offset: int, val: str, okToLog: bool):
        """在指定块的指定偏移处存储整数。

        Args:
            :param blk: 对磁盘块的引用。
            :param offset: 块内的字节偏移量
            :param val: 要存储的值
            :param okToLog: 是否写入日志
        """
        self.__concurMgr.xLock(blk)
        buff = self.__mybuffers.getBuffer(blk)
        lsn = -1
        if okToLog:
            lsn = self.__recoveryMgr.setString(buff, offset)
        p = buff.contents()
        p.setString(offset, val)
        buff.setModified(self.__txnum, lsn)

    def size(self, filename: str) -> int:
        """获取指定文件中的块数

        Args:
            :param filename: 文件的名称

        Returns:
            :return 文件中的块数
        """
        dummyblk = BlockID(filename, self.__END_OF_FILE)
        self.__concurMgr.sLock(dummyblk)
        return self.__fm.length(filename)

    def append(self, filename: str) -> BlockID:
        """将新块添加到指定文件的末尾

        Args:
            :param filename: 文件的名称

        Returns:
            :return 对新创建的磁盘块的引用。
        """
        dummyblk = BlockID(filename, self.__END_OF_FILE)
        self.__concurMgr.xLock(dummyblk)
        return self.__fm.append(filename)

    def blockSize(self) -> int:
        """获取块的大小"""
        return self.__fm.blockSize()

    def availableBuffs(self) -> int:
        """获取可用的缓冲区"""
        return self.__bm.available()

    @staticmethod
    def __nextTxNumber() -> int:
        Transaction.__nextTxNum += 1
        return Transaction.__nextTxNum
