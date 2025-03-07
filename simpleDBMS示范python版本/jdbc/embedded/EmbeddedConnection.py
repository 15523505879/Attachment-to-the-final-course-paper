from tx.Transaction import Transaction
from SimpleDB import SimpleDB


class EmbeddedConnection:
    """Connection的嵌入式实现

    Attributes:
        __db: 数据库引擎
        __currentTx: 事务
        __planner: SQL语句执行对象
    """

    def __init__(self, db: SimpleDB):
        self.__db = db
        self.__currentTx = db.newTx()
        self.__planner = db.planner()

    def createStatement(self):
        """为连接创建一个新的Statement"""
        from EmbeddedStatement import EmbeddedStatement

        return EmbeddedStatement(self, self.__planner)

    def close(self):
        """通过提交当前事务来关闭连接"""
        self.__currentTx.commit()

    def commit(self):
        """提交当前事务并启动新事务"""
        self.__currentTx.commit()
        self.__currentTx = self.__db.newTx()

    def rollback(self):
        """回滚当前事务并启动新事务"""
        self.__currentTx.rollback()
        self.__currentTx = self.__db.newTx()

    def getTransaction(self) -> Transaction:
        """返回当前与此连接关联的事务"""
        return self.__currentTx

