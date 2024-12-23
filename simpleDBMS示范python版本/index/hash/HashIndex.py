from Index import Index
from Layout import Layout
from Constant import Constant
from TableScan import TableScan
from RID import RID
from Transaction import Transaction


class HashIndex(Index):
    """Index接口的静态哈希实现

    分配了固定的桶数为100，
    每个桶都实现为一个索引记录的文件。
    """

    NUM_BUCKETS = 100

    def __init__(self, tx: Transaction, idxname: str, layout: Layout):
        self.__tx = tx
        self.__idxname = idxname
        self.__layout = layout
        self.__searchkey = None
        self.__ts = None

    def beforeFirst(self, searchkey: Constant):
        """将索引定位到具有指定搜索键的第一条索引记录之前。

        该方法哈希搜索键以确定桶，然后在与桶对应的文件上打开表扫描。
        关闭先前桶（如果有的话）的表扫描。
        """
        self.close()
        self.__searchkey = searchkey
        bucket = hash(searchkey) % self.NUM_BUCKETS
        tblname = f"{self.__idxname}{bucket}"
        self.__ts = TableScan(self.__tx, tblname, self.__layout)

    def next(self) -> bool:
        """移动到具有搜索键的下一条记录。

        该方法循环遍历桶的表扫描，查找匹配的记录，
        如果没有更多这样的记录，则返回False。
        """
        while self.__ts.next():
            if self.__ts.getVal("dataval") == self.__searchkey:
                return True
        return False

    def getDataRid(self) -> RID:
        """从桶的表扫描的当前记录中检索 dataRID"""
        blknum = self.__ts.getInt("block")
        id = self.__ts.getInt("id")
        return RID(blknum, id)

    def insert(self, val: Constant, rid: RID):
        """将新记录插入到桶的表扫描中。"""
        self.beforeFirst(val)
        self.__ts.insert()
        self.__ts.setInt("block", rid.blockNumber())
        self.__ts.setInt("id", rid.slot())
        self.__ts.setVal("dataval", val)

    def delete(self, val: Constant, rid: RID):
        """从桶的表扫描中删除指定的记录。

        该方法从扫描的开始处开始，并循环遍历记录，直到找到指定的记录为止。
        """
        self.beforeFirst(val)
        while self.next():
            if self.getDataRid() == rid:
                self.__ts.delete()
                return

    def close(self):
        """关闭索引，关闭当前的表扫描。"""
        if self.__ts is not None:
            self.__ts.close()

    @staticmethod
    def searchCost(numblocks: int) -> int:
        """获取搜索具有指定块数的索引文件的成本。

        该方法假设所有桶的大小大致相同，因此成本只是桶的大小。

        Args:
            :param numblocks: 索引记录的块数

        Returns:
            :return: 遍历索引的成本
        """
        return numblocks // HashIndex.NUM_BUCKETS
