from Schema import Schema
from Transaction import Transaction
from StatInfo import StatInfo
from Layout import Layout
from Index import Index
from HashIndex import HashIndex


class IndexInfo:
    """关于索引的信息

    此信息可用于估算使用索引的成本。

    Attributes:
        __idxname: 索引的名称
        __fldname: 索引字段的名称
        __tx: 调用事务
        __tblSchema: 表的模式
        __idxLayout: 索引记录的布局
        __si: 表的统计信息
    """

    def __init__(self, idxname: str, fldname: str, tblSchema: Schema, tx: Transaction, si: StatInfo):
        self.__idxname = idxname
        self.__fldname = fldname
        self.__tx = tx
        self.__tblSchema = tblSchema
        self.__idxLayout = self.__createIdxLayout()
        self.__si = si

    def open(self) -> Index:
        """打开此对象描述的索引"""
        return HashIndex(self.__tx, self.__idxname, self.__idxLayout)

    def blocksAccessed(self) -> int:
        """估算查找具有特定搜索键的所有索引记录所需的块访问次数。

        该方法使用表的元数据来估算索引文件的大小和每个块的索引记录数。
        然后将此信息传递给适当索引类型的traversalCost方法，该方法提供估算。

        Returns:
            :return: 遍历索引所需的块访问次数
        """
        rpb = self.__tx.blockSize() // self.__idxLayout.slotSize()
        numblocks = self.__si.recordsOutput() // rpb
        return HashIndex.searchCost(numblocks)

    def recordsOutput(self) -> int:
        """返回具有搜索键的估计记录数"""
        return self.__si.recordsOutput() // self.__si.distinctValues()

    def distinctValues(self, fname: str) -> int:
        """获取底层表中指定字段的不同值，

        或者对于索引字段来说，返回1。
        """
        return 1 if self.__fldname == fname else self.__si.distinctValues()

    def __createIdxLayout(self) -> Layout:
        """返回索引记录的布局。

        模式包括 dataRID（表示为两个整数，块号和记录ID）和 dataval（它是索引字段）。
        关于索引字段的模式信息通过表的模式获得。

        Returns:
            :return 索引记录的布局
        """
        sch = Schema()
        sch.addIntField("block")
        sch.addIntField("id")
        if self.__tblSchema.type(self.__fldname) == 4:
            sch.addIntField("dataval")
        else:
            fldlen = self.__tblSchema.length(self.__fldname)
            sch.addStringField("dataval", fldlen)
        return Layout(sch)
