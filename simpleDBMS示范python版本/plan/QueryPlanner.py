from abc import ABC, abstractmethod
from QueryData import QueryData
from Transaction import Transaction


class QueryPlanner(ABC):
    """SQL select语句的计划器实现的接口"""

    @abstractmethod
    def createPlan(self, data: QueryData, tx: Transaction):
        """为解析的查询创建一个计划"""
        pass
