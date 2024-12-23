from Page import Page
from FileMgr import FileMgr
from LogMgr import LogMgr
from BlockID import BlockID


class Buffer:
    """单个缓冲区

    数据缓冲区封装了一个页面

    Attributes:
        __fm: 文件管理器
        __lm: 日志管理器
        __contents: 缓冲区
        __blk: 分配给缓冲区的磁盘块
        __pins: 缓冲区被固定的次数
        __txnum: 事务号
        __lsn: 记录号
    """

    def __init__(self, fm: FileMgr, lm: LogMgr):
        self.__fm = fm
        self.__lm = lm
        self.__contents = Page(fm.blockSize())
        self.__blk = None
        self.__pins = 0
        self.__txnum = -1
        self.__lsn = -1

    def contents(self) -> Page:
        return self.__contents

    def block(self) -> BlockID:
        return self.__blk

    def setModified(self, txnum: int, lsn: int):
        self.__txnum = txnum
        if lsn >= 0:
            self.__lsn = lsn

    def isPinned(self) -> bool:
        """当前缓冲区是否已固定（固定计数非零）

        Returns:
            :return pins: 如果缓冲区已固定则返回true
        """
        return self.__pins > 0

    def modifyingTx(self) -> int:
        return self.__txnum

    def assignToBlock(self, b: BlockID):
        """将指定块的内容读入缓冲区中

        如果缓冲区是脏的，则先将缓冲区的内容写入磁盘

        Args:
            :param b: 要读取的块
        """
        self.flush()
        self.__blk = b
        self.__fm.read(self.__blk, self.__contents)
        self.__pins = 0

    def flush(self):
        """将缓冲区的内容写入对应的磁盘块"""
        if self.__txnum >= 0:
            self.__lm.flush(self.__lsn)
            self.__fm.write(self.__blk, self.__contents)
            self.__txnum = -1

    def pin(self):
        self.__pins += 1

    def unpin(self):
        self.__pins -= 1
