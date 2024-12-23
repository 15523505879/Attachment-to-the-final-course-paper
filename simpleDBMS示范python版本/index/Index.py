from abc import ABC, abstractmethod
from Constant import Constant
from RID import RID


class Index(ABC):
    """该接口包含遍历索引的方法"""

    @abstractmethod
    def beforeFirst(self, searchkey: Constant):
        """将索引定位到具有指定搜索键的第一条记录之前。

        Args:
            :param searchkey: 搜索键值。
        """
        pass

    @abstractmethod
    def next(self) -> bool:
        """将索引移动到在beforeFirst方法中指定的搜索键的下一条记录。

        如果没有更多具有该搜索键的索引记录，则返回False。
        """
        pass

    @abstractmethod
    def getDataRid(self) -> RID:
        """返回存储在当前索引记录中的 dataRID值。"""
        pass

    @abstractmethod
    def insert(self, dataval: Constant, datarid: RID):
        """插入具有指定dataval和datarid值的索引记录。

        Args:
            :param dataval: 新索引记录中的dataval。
            :param datarid: 新索引记录中的datarid。
        """
        pass

    @abstractmethod
    def delete(self, dataval: Constant, datarid: RID):
        """删除具有指定dataval和datarid值的索引记录。

        Args:
            :param dataval: 被删除的索引记录的dataval。
            :param datarid: 被删除的索引记录的datarid。
        """
        pass

    @abstractmethod
    def close(self):
        """关闭索引"""
        pass
