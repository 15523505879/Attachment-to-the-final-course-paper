import time
from Buffer import Buffer
from BufferAbortException import BufferAbortException
from FileMgr import FileMgr
from LogMgr import LogMgr
from BlockID import BlockID


class BufferMgr:
    """缓冲区管理器

    管理缓冲区对数据块的固定和取消固定

    Attributes:
        __MAX_TIME: int型，最大等待时间（秒）
        __bufferpool: Buffer型，缓冲区池
        __numAvailable: 可用缓冲区的数量
    """

    __MAX_TIME = 10     # 最大等待时间为10s

    def __init__(self, fm: FileMgr, lm: LogMgr, numbuffs: int):
        self.__bufferpool = [Buffer(fm, lm) for _ in range(numbuffs)]
        self.__numAvailable = numbuffs

    def available(self) -> int:
        """可用缓冲区的数量

        Returns:
            :return __numAvailable: 可用缓冲区的数量
        """
        return self.__numAvailable

    def flushAll(self, txnum: int):
        """刷新由指定事务修改的脏缓冲区

        Args:
            :param txnum: 事务号
        """
        for buff in self.__bufferpool:
            if buff.modifyingTx() == txnum:
                buff.flush()

    def unpin(self, buff: Buffer):
        """解除指定缓冲区的固定

        Args:
            :param buff: 指定的缓冲区
        """
        buff.unpin()
        if not buff.isPinned():
            self.__numAvailable += 1

    def pin(self, blk: BlockID) -> Buffer:
        """将缓冲区固定到指定块。

        如果没有可用的缓冲区则等待，若在固定时间内没有可用的缓冲区，则抛出异常。

        Args:
            :param blk: 对磁盘块的引用

        Raises:
            :raise InterruptedError: 无法固定到指定块时报错

        Returns:
            :return buff: 固定到该块的缓冲区
        """
        try:
            timestamp = time.time()
            buff = self.__tryToPin(blk)
            while buff is None and not self.__waitingTooLong(timestamp):
                time.sleep(self.__MAX_TIME)
                buff = self.__tryToPin(blk)
            if buff is None:
                raise BufferAbortException()
            return buff
        except InterruptedError:
            raise BufferAbortException()

    def __waitingTooLong(self, startTime: float) -> bool:
        return time.time() - startTime > self.__MAX_TIME

    def __tryToPin(self, blk: BlockID) -> Buffer | None:
        """尝试将缓冲区固定到指定的块

        如果有一个分配给该块的缓冲区，则使用该缓冲区；
        否则，选择池中一个未固定的缓冲区。

        Args:
            :param blk: 对磁盘块的引用

        Returns:
            :return 固定的缓冲区
        """
        buff = self.__findExistingBuffer(blk)
        if buff is None:    # 无已固定到指定块的缓冲区
            buff = self.__chooseUnpinnedBuffer()
            if buff is None:    # 无空闲缓冲区
                return None
            buff.assignToBlock(blk)
        if not buff.isPinned():
            self.__numAvailable -= 1
        buff.pin()
        return buff

    def __findExistingBuffer(self, blk: BlockID) -> Buffer | None:
        """查找固定到指定块的缓冲区

        Args:
            :param blk: 对磁盘块的引用

        Returns:
            :return 对应的缓冲区
        """
        for buff in self.__bufferpool:
            b = buff.block()
            if b is not None and b == blk:
                return buff
        return None

    def __chooseUnpinnedBuffer(self) -> Buffer | None:
        """选择一个未固定的缓冲区

        Returns:
            :return 未固定的缓冲区
        """
        for buff in self.__bufferpool:
            if not buff.isPinned():
                return buff
        return None
