import time
from LockAbortException import LockAbortException
from BlockID import BlockID


class LockTable:
    """锁表，提供对块进行加锁和解锁的方法

    X锁用-1表示，每有一个S锁，锁值+1，没有锁时用0表示。

    Attributes:
        __MAX_TIME: 最大等待时间
        __locks: 锁表
    """

    __MAX_TIME = 10

    def __init__(self):
        self.__locks = {}

    def sLock(self, blk: BlockID):
        """对指定快授予S锁

        如果块已经有X锁，则等待，直到锁被释放。
        如果等待超过最大等待时间则抛出异常。

        Args:
            :param blk: 对磁盘块的引用

        Raises:
            :raise InterruptedError: 无法加S锁时报错。
        """
        try:
            timestamp = time.time()
            while self.__hasXlock(blk) and not self.__waitingTooLong(timestamp):
                time.sleep(self.__MAX_TIME)
            if self.__hasXlock(blk):
                raise LockAbortException()
            val = self.__getLockVal(blk)
            self.__locks[blk] = val + 1
        except InterruptedError:
            raise LockAbortException()

    def xLock(self, blk: BlockID):
        """对指定块授予X锁

        如果在块中已经存在其他任何类型的锁，则等待，直到锁被释放。
        如果等待超过最大等待时间，则抛出异常。

        Args:
            :param blk: 对磁盘块的引用

        Raises:
            :raise InterruptedError: 无法加X锁时报错。
        """
        try:
            timestamp = time.time()
            while self.__hasOtherSLocks(blk) and not self.__waitingTooLong(timestamp):
                time.sleep(self.__MAX_TIME)
            if self.__hasOtherSLocks(blk):
                raise LockAbortException()
            self.__locks[blk] = -1
        except InterruptedError:
            raise LockAbortException()

    def unLock(self, blk: BlockID):
        """释放对指定块的锁

        Args:
            :param blk: 对磁盘块的引用。
        """
        val = self.__getLockVal(blk)
        if val > 1:
            self.__locks[blk] = val - 1
        else:
            del self.__locks[blk]

    def __hasXlock(self, blk: BlockID) -> bool:
        """判断是否有X锁"""
        return self.__getLockVal(blk) < 0

    def __hasOtherSLocks(self, blk: BlockID) -> bool:
        """判断是否有S锁"""
        return self.__getLockVal(blk) > 1

    def __waitingTooLong(self, startTime: float) -> bool:
        return time.time() - startTime > self.__MAX_TIME

    def __getLockVal(self, blk: BlockID) -> int:
        """获取锁值"""
        ival = self.__locks.get(blk)
        return 0 if ival is None else ival
