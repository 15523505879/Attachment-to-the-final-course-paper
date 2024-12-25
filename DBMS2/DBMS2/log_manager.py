import os
import time
import json
from datetime import datetime

class LogManager:
    # 定义日志级别
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4

    def __init__(self, log_file: str, log_level: int = INFO):
        """
        初始化日志管理器
        :param log_file: 日志文件路径
        :param log_level: 日志级别(DEBUG=1, INFO=2, WARNING=3, ERROR=4)
        """
        self.log_file = log_file
        self.log_level = log_level
        # 确保日志文件存在
        open(log_file, 'a').close()

    def _log_message(self, level: int, message: str):
        """
        根据日志级别输出消息
        """
        if level >= self.log_level:
            level_str = {
                self.DEBUG: "DEBUG",
                self.INFO: "INFO",
                self.WARNING: "WARNING",
                self.ERROR: "ERROR"
            }.get(level, "INFO")
            print(f"[{level_str}] {message}")

    def write_log(self, tx_id: int, operation: str, message: str):
        """写入日志"""
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] TX {tx_id} - {operation}: {message}\n"
            
            # 使用 utf-8 编码写入日志
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
        except Exception as e:
            print(f"[ERROR] 写入日志失败: {str(e)}")
            
    def write_lock_log(self, tx_id: int, operation: str, resource: str, lock_type: str):
        """写入锁相关的日志"""
        message = f"{operation} {lock_type} lock on {resource}"
        self.write_log(tx_id, "LOCK", message)

    def write_checkpoint(self, checkpoint_data: dict):
        """写入检查点日志"""
        try:
            timestamp = checkpoint_data['timestamp']
            active_txs = ','.join(map(str, checkpoint_data['active_transactions']))
            tables = ','.join(checkpoint_data['tables'])
            
            checkpoint_log = (
                f"=== CHECKPOINT START [{timestamp}] ===\n"
                f"Active Transactions: {active_txs}\n"
                f"Tables: {tables}\n"
                f"=== CHECKPOINT END ===\n"
            )
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(checkpoint_log)
        except Exception as e:
            print(f"[ERROR] 写入检查点失败: {str(e)}")

    def read_logs(self) -> list:
        """
        读取日志文件
        :return: 包含所有日志的列表
        """
        try:
            with open(self.log_file, "r", encoding="utf-8") as file:
                logs = file.readlines()
            self._log_message(self.DEBUG, "Logs read successfully.")
            return [log.strip() for log in logs]  # 去除每行的换行符
        except IOError as e:
            self._log_message(self.ERROR, f"Failed to read logs: {e}")
            return []

    def iterator(self):
        """
        提供日志迭代器
        :return: 逐行返回日志内容
        """
        try:
            with open(self.log_file, "r", encoding="utf-8") as file:
                for line in file:
                    yield line.strip()  # 已经是字符串，不需要decode
        except IOError as e:
            self._log_message(self.ERROR, f"Failed to iterate logs: {e}")

    def get_last_checkpoint(self) -> dict:
        """获取最后一个检查点"""
        try:
            checkpoint_data = None
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i in range(len(lines)-1, -1, -1):
                    if "=== CHECKPOINT START" in lines[i]:
                        # 解析检查点数据
                        timestamp = lines[i].split('[')[1].split(']')[0]
                        active_txs = lines[i+1].split(':')[1].strip().split(',')
                        tables = lines[i+2].split(':')[1].strip().split(',')
                        
                        checkpoint_data = {
                            'timestamp': timestamp,
                            'active_transactions': [int(tx) for tx in active_txs if tx],
                            'tables': [t.strip() for t in tables if t.strip()]
                        }
                        break
            return checkpoint_data
        except Exception as e:
            print(f"[ERROR] 获取检查点失败: {str(e)}")
            return None

    def read_logs_after(self, timestamp: str = None) -> list:
        """读取指定时间戳之后的日志"""
        try:
            logs = []
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if not timestamp:
                        logs.append(line.strip())
                        continue
                        
                    # 解析日志时间戳
                    if '[' in line and ']' in line:
                        log_time = line.split(']')[0].strip('[')
                        if log_time > timestamp:
                            logs.append(line.strip())
                            
            return logs
            
        except Exception as e:
            print(f"[ERROR] Failed to read logs after {timestamp}: {str(e)}")
            return []

    def _extract_tx_id(self, log_line: str) -> int:
        """从日志行提取事务ID"""
        try:
            # 格式: [timestamp] TX {tx_id} - {operation}: {message}
            parts = log_line.split('TX')
            if len(parts) > 1:
                tx_part = parts[1].split('-')[0].strip()
                return int(tx_part)
        except Exception:
            pass
        return None
