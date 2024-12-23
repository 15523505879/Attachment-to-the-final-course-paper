from Plan import Plan
from Schema import Schema
from ProjectScan import ProjectScan


class ProjectPlan(Plan):
    """与<i>project</i>关系代数运算符相对应的查询计划类"""

    def __init__(self, p: Plan, fieldlist: list):
        self.__p = p
        self.__schema = Schema()
        for fldname in fieldlist:
            self.__schema.add(fldname, p.schema())

    def open(self) -> ProjectScan:
        """为此查询创建一个投影扫描"""
        s = self.__p.open()
        return ProjectScan(s, self.__schema.fields())

    def blocksAccessed(self) -> int:
        """估计投影中的块访问次数"""
        return self.__p.blocksAccessed()

    def recordsOutput(self) -> int:
        """估计投影中的输出记录数"""
        return self.__p.recordsOutput()

    def distinctValues(self, fldname: str) -> int:
        """估计投影中的不同字段值的数量"""
        return self.__p.distinctValues(fldname)

    def schema(self) -> Schema:
        """返回投影的模式"""
        return self.__schema
