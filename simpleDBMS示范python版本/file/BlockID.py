class BlockID:
    """块。

    记录块所在的文件、块号。

    Attributes:
        __filename: 块所在的文件。
        __blknum: 块号。
    """

    def __init__(self, filename: str, blknum: int):
        self.__filename = filename
        self.__blknum = blknum

    def fileName(self) -> str:
        """获取块所在的文件。"""
        return self.__filename

    def number(self) -> int:
        """获取块号。"""
        return self.__blknum

    def __eq__(self, other):
        if isinstance(other, BlockID):
            return self.__filename == other.__filename and self.__blknum == other.__blknum
        return False

    def __str__(self):
        return f"[file {self.__filename}, block {self.__blknum}]"

    def __hash__(self):
        return hash(str(self))


if __name__ == "__main__":
    block_id1 = BlockID("example.txt", 1)
    block_id2 = BlockID("example.txt", 1)
    print(block_id2 == block_id1)
    print(block_id1)
