from QueryData import QueryData


class CreateViewData:
    """SQL <i>create view</i> 语句的数据表示。

    Attributes:
        __viewname: 视图名
        __qrydata: 视图定义
    """

    def __init__(self, viewname: str, qrydata: QueryData):
        self.__viewname = viewname
        self.__qrydata = qrydata

    def viewName(self) -> str:
        """返回新视图的名称"""
        return self.__viewname

    def viewDef(self) -> str:
        """返回新视图的定义"""
        return str(self.__qrydata)
