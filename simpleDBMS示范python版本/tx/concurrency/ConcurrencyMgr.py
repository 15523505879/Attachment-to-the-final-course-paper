from LockTable import LockTable
from BlockID import BlockID


class ConcurrencyMgr:
    """事务的并发管理器

    每个事务都有自己的并发管理器。
    并发管理器跟踪事务当前持有的锁，并根据需要与全局锁表交互。

    Attributes:
        __lockTbl: 全局锁表，所有事务共享一张表
        __locks: 当前事务的锁表
    """

    __lockTbl = LockTable()

    def __init__(self):
        self.__locks: [BlockID, str] = {}

    def sLock(self, blk: BlockID):
        """为指定块授予S锁

        Args:
            :param blk: 对磁盘块的引用
        """
        if self.__locks.get(blk) is None:
            self.__lockTbl.sLock(blk)
            self.__locks[blk] = "S"

    def xLock(self, blk: BlockID):
        """为指定块授予X锁

        如果事务没有对该块的X锁，则先获取该块的S锁，然后升级为X锁

        Args:
            :param blk: 对磁盘块的引用
        """
        if not self.__hasXlock(blk):
            self.sLock(blk)
            self.__lockTbl.xLock(blk)
            self.__locks[blk] = "X"

    def release(self):
        """释放所有锁"""
        for blk in self.__locks.keys():
            self.__lockTbl.unLock(blk)
        self.__locks.clear()

    def __hasXlock(self, blk: BlockID) -> bool:
        """判断是否有X锁"""
        lockType = self.__locks.get(blk)
        return lockType is not None and lockType == "X"
