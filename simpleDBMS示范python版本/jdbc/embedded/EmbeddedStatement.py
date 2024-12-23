from sqlite3 import Error
from EmbeddedConnection import EmbeddedConnection
from Planner import Planner
from EmbeddedResultSet import EmbeddedResultSet
from BadSyntaxException import BadSyntaxException


class EmbeddedStatement:
    """Statement的嵌入式实现

    Attributes:
        __conn: 服务器连接
        __planner: SQL语句执行对象
    """

    def __init__(self, conn: EmbeddedConnection, planner: Planner):
        self.__conn = conn
        self.__planner = planner

    def executeQuery(self, qry: str) -> EmbeddedResultSet:
        """执行指定的SQL查询字符串

        调用查询规划器创建查询的计划
        并将计划发送到ResultSet构造函数进行处理
        如果无法创建计划，则回滚并抛出异常

        Args:
            :param qry: 查询语句

        Returns:
            :return 结果集
        """
        try:
            tx = self.__conn.getTransaction()
            pln = self.__planner.createQueryPlan(qry, tx)
            return EmbeddedResultSet(pln, self.__conn)
        except (RuntimeError, BadSyntaxException) as e:
            self.__conn.rollback()
            raise Error(e)

    def executeUpdate(self, cmd: str) -> int:
        """通过将命令发送到更新规划器，然后提交

        执行指定的SQL更新命令。
        在出现错误时回滚并抛出异常

        Args:
            :param cmd: 更新命令

        Returns:
            :return 受影响的记录数
        """
        try:
            tx = self.__conn.getTransaction()
            result = self.__planner.executeUpdate(cmd, tx)
            self.__conn.commit()
            return result
        except (RuntimeError, BadSyntaxException) as e:
            self.__conn.rollback()
            raise Error(e)

    def close(self):
        pass
