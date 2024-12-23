from BlockID import BlockID
from Page import Page
from FileMgr import FileMgr


class LogIterator:
    """逆序遍历日志文件记录的类

    遍历块的顺序为从后往前，块内遍历的顺序为从前到后

    Attributes:
        __fm: 存储管理器，FileMgr类
        __blk: 当前所在块，BlockID类
        __p: 当前日志块对应的缓冲区
        __currentpos: 当前所在位置
        __boundary: 最后写入记录的位置
    """

    def __init__(self, fm: FileMgr, blk: BlockID):
        self.__fm = fm
        self.__blk = blk
        b = bytes(fm.blockSize())
        self.__p = Page(b)
        self.__currentpos = 0
        self.__boundary = 0
        self.__moveToBlock(blk)

    def hasNext(self) -> bool:
        """判断当前日志记录是否是日志文件中最早的记录

        Returns:
            :return 如果存在更早的日志记录，则返回true
        """
        return self.__currentpos < self.__fm.blockSize() or self.__blk.number() > 0

    def next(self) -> bytes:
        """获取块中的下一个日志记录

        如果当前日志块中没有更多的日志记录，则移动到前一个块

        Returns:
            :return rec: 下一个更早的日志记录
        """
        if self.__currentpos == self.__fm.blockSize():
            self.__blk = BlockID(self.__blk.fileName(), self.__blk.number() - 1)
            self.__moveToBlock(self.__blk)
        rec = self.__p.getBytes(self.__currentpos)
        self.__currentpos += len(rec) + 4
        return rec

    def __moveToBlock(self, blk: BlockID):
        """移动到指定的块

        移动到指定的块后，定位到该块中的第一条记录上（最近的记录）

        Args:
            :param blk: 要移动到的块
        """
        self.__fm.read(blk, self.__p)
        self.__boundary = self.__p.getInt(0)
        self.__currentpos = self.__boundary
