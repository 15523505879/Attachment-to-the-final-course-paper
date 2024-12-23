class RID:
    """文件记录中的标识符

    RID由文件中的块号和该块中记录的槽号组成。

    Attributes:
        __blknum: 记录所在的块号
        __slot: 记录在块中的槽号
    """

    def __init__(self, blknum: int, slot: int):
        self.__blknum = blknum
        self.__slot = slot

    def blockNumber(self) -> int:
        """返回与此RID关联的块号。"""
        return self.__blknum

    def slot(self) -> int:
        """返回与此RID关联的槽位。"""
        return self.__slot

    def __eq__(self, other):
        if isinstance(other, RID):
            return self.__blknum == other.__blknum and self.__slot == other.__slot
        return False

    def __str__(self):
        return f"[{str(self.__blknum)}, {str(self.__slot)}]"
