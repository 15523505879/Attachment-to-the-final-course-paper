from abc import ABC, abstractmethod
from typing import Optional
from Page import Page


class LogRecord(ABC):
    """由每种类型的日志记录实现的接口"""

    CHECKPOINT = 0
    START = 1
    COMMIT = 2
    ROLLBACK = 3
    SET_INT = 4
    SET_STRING = 5

    @abstractmethod
    def op(self):
        """日志记录的类型"""
        pass

    @abstractmethod
    def txNumber(self):
        """日志记录存储的事务ID"""
        pass

    @abstractmethod
    def undo(self, tx):
        """撤销由此日志纪录编码的操作。"""
        pass

    @staticmethod
    def createLogRecord(bytes: bytes) -> Optional['LogRecord']:
        """解释日志迭代器返回的字节

        Args:
            :param bytes: 日志迭代器返回的字节

        Returns:
            :return 相应的日志记录
        """

        from CheckPointRecord import CheckPointRecord   # 这里用于避免循环引用报错。
        from StartRecord import StartRecord
        from CommitRecord import CommitRecord
        from RollbackRecord import RollbackRecord
        from SetIntRecord import SetIntRecord
        from SetStringRecord import SetStringRecord

        p = Page(bytes)
        op_code = p.getInt(0)
        if op_code == LogRecord.CHECKPOINT:
            return CheckPointRecord()
        elif op_code == LogRecord.START:
            return StartRecord(p)
        elif op_code == LogRecord.COMMIT:
            return CommitRecord(p)
        elif op_code == LogRecord.ROLLBACK:
            return RollbackRecord(p)
        elif op_code == LogRecord.SET_INT:
            return SetIntRecord(p)
        elif op_code == LogRecord.SET_STRING:
            return SetStringRecord(p)
        else:
            return None
