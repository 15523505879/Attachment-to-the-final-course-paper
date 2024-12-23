from BufferMgr import BufferMgr
from Buffer import Buffer
from BlockID import BlockID


class BufferList:
    """管理事务当前已固定的缓冲区

    Attributes:
        __bm: 缓冲区管理器
        __buffers: 事务固定的缓冲区
        __pins: 事务固定的块
    """

    def __init__(self, bm: BufferMgr):
        self.__bm = bm
        self.__buffers: [BlockID, Buffer] = dict()
        self.__pins: [BlockID] = []

    def getBuffer(self, blk: BlockID) -> Buffer:
        """获取固定到指定块的缓冲区

        Args:
            :param blk: 对磁盘块的引用

        Returns:
            :return 固定到该块的缓冲区，如果事务未固定该块，则返回None
        """
        return self.__buffers.get(blk)

    def pin(self, blk: BlockID):
        """固定指定的块

        Args:
            :param blk: 对磁盘块的引用
        """
        buff = self.__bm.pin(blk)
        self.__buffers[blk] = buff
        self.__pins.append(blk)

    def unpin(self, blk: BlockID):
        """解除对指定块的固定。

        Args:
            :param blk: 对磁盘块的引用
        """
        buff = self.__buffers.get(blk)
        self.__bm.unpin(buff)
        self.__pins.remove(blk)
        if blk not in self.__pins:
            del self.__buffers[blk]

    def unpinAll(self):
        """解除事务固定的所有缓冲区"""
        for blk in self.__pins:
            buff = self.__buffers.get(blk)
            self.__bm.unpin(buff)
        self.__buffers.clear()
        self.__pins.clear()
