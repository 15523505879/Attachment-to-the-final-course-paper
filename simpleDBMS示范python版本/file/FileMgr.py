import io
import os
from .Page import Page
from .BlockID import BlockID


class FileMgr:
    """文件管理器。

    将磁盘内容读入缓冲区，对数据进行读取与存储。

    Attributes:
        __openFiles: 一个字典记录打开的文件。
        __dbDirectory: 一个字符串表示数据库名。
        __blocksize: 一个整数表示数据块的大小。
        __isNew: 一个布尔类型表示数据库是新的。
    """

    def __init__(self, dbDirectory: str, blocksize: int):
        self.__dbDirectory = dbDirectory
        self.__blocksize = blocksize
        self.__isNew = not os.path.exists(dbDirectory)
        self.__openFiles = {}
        # 创建目录（如果是新数据库）
        if self.__isNew:
            os.makedirs(dbDirectory)
        # 删除任何残留的临时表
        for filename in os.listdir(dbDirectory):
            if filename.startswith("temp"):
                os.remove(os.path.join(dbDirectory, filename))

    def read(self, blk: BlockID, p: Page):
        """将块的内容读入缓冲区

        Args:
            :param blk: 要读取的块
            :param p: 要读入的缓冲区

        Raises:
            :raise IOError: 无法读入缓冲区时报错
        """
        try:
            f = self.__getFile(blk.fileName())
            f.seek(blk.number() * self.__blocksize)
            f.readinto(p.contents())
        except IOError as e:
            raise RuntimeError(f"cannot read block {blk}") from e

    def write(self, blk: BlockID, p: Page):
        """将缓冲区的内容写入块

        Args:
            :param blk: 要写入的块
            :param p: 要写的缓冲区

        Raises:
            :raise IOError: 无法写入块时报错
        """
        try:
            f = self.__getFile(blk.fileName())
            f.seek(blk.number() * self.__blocksize)
            f.write(p.contents())
        except IOError as e:
            raise RuntimeError(f"cannot write block {blk}") from e

    def append(self, filename: str) -> BlockID:
        """添加一个新的块

        Args:
            :param filename: 要加入新块的文件名

        Raises:
            :raise IOError: 无法加入新块时报错

        Returns:
            :return blk: 新添加的块
        """
        newBlkNum = self.length(filename)
        blk = BlockID(filename, newBlkNum)
        b = bytearray(self.__blocksize)
        try:
            f = self.__getFile(blk.fileName())
            f.seek(blk.number() * self.__blocksize)
            f.write(b)
        except IOError as e:
            raise RuntimeError(f"cannot append block {blk}") from e
        return blk

    def length(self, filename: str) -> int:
        try:
            f = self.__getFile(filename)
            return int(os.path.getsize(f.name) / self.__blocksize)
        except IOError as e:
            raise RuntimeError(f"cannot access {filename}") from e

    def isNew(self) -> bool:
        return self.__isNew

    def blockSize(self) -> int:
        return self.__blocksize

    def __getFile(self, filename: str) -> io.BufferedRandom:
        f = self.__openFiles.get(filename)
        if f is None:
            dbTable = os.path.join(self.__dbDirectory, filename)
            if not os.path.exists(dbTable):     # 文件不存在则创建
                f = open(dbTable, 'w')
                f.close()
            f = open(dbTable, "rb+")
            self.__openFiles[filename] = f
        return f


if __name__ == "__main__":
    fm = FileMgr("filetest", 400)
    blk = BlockID("testfile", 2)
    pos1 = 88
    p1 = Page(fm.blockSize())
    p1.setString(pos1, "abcdef")
    size = Page.maxLength(len("abcdef"))
    pos2 = pos1 + size
    p1.setInt(pos2, 345)
    fm.write(blk, p1)
    p2 = Page(fm.blockSize())
    fm.read(blk, p2)
    print("offset", pos2, "contains", p2.getInt(pos2))
    print("offset", pos1, "contains", p2.getString(pos1))
