from BlockID import BlockID
from Page import Page
from FileMgr import FileMgr
from LogIterator import LogIterator


class LogMgr:
    """日志管理器

    负责将日志记录写入日志文件，日志的尾部保存在字节缓冲区中，需要时刷新到磁盘

    Attributes:
        __latestLSN: int型，表示最新的日志序列号
        __lastSavedLSN: int型，表示最后一个保存的日志序列号
        __fm: FileMgr型，日志文件的文件管理器
        __logfile: str型，日志文件名
        __logpage: Page型，日志缓冲区
        __currentblk: BlockID型，当前所在日志块
    """

    def __init__(self, fm: FileMgr, logfile: str):
        self.__fm = fm
        self.__logfile = logfile
        b = bytes(fm.blockSize())
        self.__logpage = Page(b)
        logsize = fm.length(logfile)
        if logsize == 0:    # 日志文件中没有日志块
            self.__currentblk = self.appendNewBlock()
        else:
            self.__currentblk = BlockID(logfile, logsize - 1)
            fm.read(self.__currentblk, self.__logpage)
        self.__latestLSN = 0
        self.__lastSavedLSN = 0

    def flush(self, lsn: int):
        """将指定日志号对应的日志记录写入磁盘

        所有更早的日志记录也将写入磁盘

        Args:
            :param lsn: 指定的日志号
        """
        if lsn >= self.__lastSavedLSN:
            self.__flush()

    def iterator(self) -> LogIterator:
        self.__flush()
        return LogIterator(self.__fm, self.__currentblk)

    def append(self, logrec: bytes) -> int:
        """将日志记录加入日志缓冲区

        日志记录从右到左写入缓冲区，记录的大小在字节之前写入。
        缓冲区的开头记录最后写入记录的位置（"boundary"）

        Args:
            :param logrec: 日志记录

        Returns:
            :return 最新的日志号
        """
        boundary = self.__logpage.getInt(0)
        recsize = len(logrec)
        bytesneeded = recsize + 4
        if boundary - bytesneeded < 4:  # 缓冲区空间不足
            self.__flush()
            self.__currentblk = self.appendNewBlock()
            boundary = self.__logpage.getInt(0)
        recpos = boundary - bytesneeded
        self.__logpage.setBytes(recpos, logrec)
        self.__logpage.setInt(0, recpos)    # 更新最新记录的位置
        self.__latestLSN += 1
        return self.__latestLSN

    def appendNewBlock(self) -> BlockID:
        """初始化字节缓冲区并附加到日志文件

        Returns:
            :return blk: 新添加的块
        """
        blk = self.__fm.append(self.__logfile)
        self.__logpage.setInt(0, self.__fm.blockSize())
        self.__fm.write(blk, self.__logpage)
        return blk

    def __flush(self):
        """将缓冲区写入日志文件"""
        self.__fm.write(self.__currentblk, self.__logpage)
        self.__lastSavedLSN = self.__latestLSN
