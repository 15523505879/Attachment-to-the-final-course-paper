class StatInfo:
    """表的统计信息

    保存关于表的三个统计信息：
    块数、记录数和每个字段不同值的数量。

    Attributes:
        __numBlocks: 表中的块数
        __numRecs: 表中的记录数
    """

    def __init__(self, numblocks: int, numrecs: int):
        self.__numBlocks = numblocks
        self.__numRecs = numrecs

    def blocksAccessed(self) -> int:
        """返回表中估计的块数。"""
        return self.__numBlocks

    def recordsOutput(self) -> int:
        """返回表中估计的记录数。"""
        return self.__numRecs

    def distinctValues(self) -> int:
        """返回指定字段的估计不同值的数量。

        该估计是完全猜测的。
        """
        return 1 + (self.__numRecs // 3)
