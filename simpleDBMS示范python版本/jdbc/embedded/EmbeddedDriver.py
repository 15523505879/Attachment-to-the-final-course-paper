from SimpleDB import SimpleDB
from EmbeddedConnection import EmbeddedConnection


class EmbeddedDriver:
    """服务器的实现"""

    def connect(self, databaseName: str) -> EmbeddedConnection:
        """创建服务器连接并返回"""
        db = SimpleDB(databaseName)
        return EmbeddedConnection(db)
