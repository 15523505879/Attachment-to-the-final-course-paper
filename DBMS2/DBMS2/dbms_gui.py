import os
import time
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading

from storage_manager import FileMgr
from metadata_manager import TableMetadata
from query_manager import QueryManager
from sql_parser import SQLParser
from execution_planner import ExecutionPlanner
from interface import EmbeddedDBInterface
from record_manager import TableScan
from log_manager import LogManager
from recovery_manager import RecoveryManager
from transaction_manager import Transaction  # 导入事务管理器
from concurrency_manager import ConcurrencyMgr  # 并发管理器
from buffer_manager import Buffer  # 导入缓冲区管理器+


class DBMSGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("数据库管理系统")
        
        # 初始化组件
        self.db_directory = "database"
        self.log_file = "db.log"
        
        # 清理旧文件
        if os.path.exists(self.db_directory):
            import shutil
            shutil.rmtree(self.db_directory)
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        
        # 初始化其他组件    
        self.file_mgr = FileMgr(self.db_directory)
        self.log_mgr = LogManager(self.log_file)
        self.table_metadata = TableMetadata(self.file_mgr)
        self.concurrency_mgr = ConcurrencyMgr()
        self.concurrency_mgr.set_log_manager(self.log_mgr)
        self.query_manager = QueryManager(self.table_metadata, TableScan, self.log_mgr)
        self.sql_parser = SQLParser(self.query_manager)
        
        # 设置相互引用
        self.query_manager.set_sql_parser(self.sql_parser)
        
        # 事务管理
        self.transactions = {}
        self.current_tx_id = None
        
        self.last_log_position = 0  # 添加日志位置记录
        
        self._init_gui()
        self.start_new_transaction()
        
    def _init_gui(self):
        # 左侧面板 - SQL输入和执行
        left_frame = ttk.Frame(self.root, padding="5")
        left_frame.grid(row=0, column=0, sticky="nsew")
        
        # 事务选择下拉框
        tx_select_frame = ttk.Frame(left_frame)
        tx_select_frame.pack(fill="x", pady=5)
        ttk.Label(tx_select_frame, text="当前事务:").pack(side="left")
        self.tx_combobox = ttk.Combobox(tx_select_frame, state="readonly")
        self.tx_combobox.pack(side="left", fill="x", expand=True, padx=5)
        self.tx_combobox.bind('<<ComboboxSelected>>', self.on_transaction_selected)
        
        ttk.Label(left_frame, text="SQL命令").pack(anchor="w")
        self.sql_text = tk.Text(left_frame, width=50, height=5)
        self.sql_text.pack(fill="both", expand=True, pady=5)
        
        # 执行按钮
        ttk.Button(left_frame, text="执行", command=self.execute_sql).pack(pady=5)
        
        # 事务按钮
        tx_frame = ttk.Frame(left_frame)
        tx_frame.pack(fill="x", pady=5)
        ttk.Button(tx_frame, text="新建事务", command=self.start_new_transaction).pack(side="left", padx=2)
        ttk.Button(tx_frame, text="提交", command=self.commit_transaction).pack(side="left", padx=2)
        ttk.Button(tx_frame, text="回滚", command=self.rollback_transaction).pack(side="left", padx=2)
        ttk.Button(tx_frame, text="系统恢复", command=self.recover_system).pack(side="left", padx=2)
        
        # 添加检查点按钮
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill="x", pady=5)
        self.checkpoint_button = tk.Button(
            button_frame, 
            text="创建检查点",
            command=self.create_checkpoint
        )
        self.checkpoint_button.pack(side=tk.LEFT, padx=5)
        
        # 添加清空数据库按钮
        ttk.Button(tx_frame, text="清空数据库", 
            command=self.clear_database,
            style="Danger.TButton"  # 使用红色样式提醒危险操作
        ).pack(side="left", padx=2)
        
        # 添加危险操作的样式
        style = ttk.Style()
        style.configure("Danger.TButton", 
            foreground="red",
            font=('Helvetica', '10', 'bold')
        )
        
        # 右侧面板 - 日志和并发状态
        right_frame = ttk.Frame(self.root, padding="5")
        right_frame.grid(row=0, column=1, sticky="nsew")
        
        # 并发状态显示
        ttk.Label(right_frame, text="并发状态").pack(anchor="w")
        self.concurrency_text = tk.Text(right_frame, width=50, height=10)
        self.concurrency_text.pack(fill="both", expand=True, pady=5)
        
        # 日志显示区域添加滚动条
        log_frame = ttk.Frame(right_frame)
        log_frame.pack(fill="both", expand=True, pady=5)
        
        ttk.Label(log_frame, text="系统日志").pack(anchor="w")
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side="right", fill="y")
        
        # 创建文本框并关联滚动条
        self.log_text = tk.Text(log_frame, width=50, height=10, 
                               yscrollcommand=scrollbar.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.log_text.yview)
        
        # 状态栏
        self.status_var = tk.StringVar()
        ttk.Label(self.root, textvariable=self.status_var, relief="sunken").grid(row=1, column=0, columnspan=2, sticky="ew")
        
        # 配置网格权重
        self.root.grid_columnconfigure((0,1), weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # 启动定时更新
        self.update_display()
        
    def update_display(self):
        """定时更新显示"""
        # 更新事务下拉框
        current_transactions = [str(tx_id) for tx_id in self.transactions.keys()]
        self.tx_combobox['values'] = current_transactions
        if self.current_tx_id and str(self.current_tx_id) not in self.tx_combobox.get():
            self.tx_combobox.set(str(self.current_tx_id))
            
        # 更新并发状态
        self.concurrency_text.delete(1.0, tk.END)
        self.concurrency_text.insert(tk.END, "活跃事务:\n")
        for tx_id, tx in self.transactions.items():
            status = "当前活跃" if tx_id == self.current_tx_id else tx.status
            self.concurrency_text.insert(tk.END, f"事务 {tx_id}: {status}\n")
            
        self.concurrency_text.insert(tk.END, "\n锁状态:\n")
        for resource, locks in self.concurrency_mgr.locks.items():
            lock_types = [f"TX{tx_id}({lock_type})" for tx_id, lock_type in locks.items()]
            self.concurrency_text.insert(tk.END, f"{resource}: {', '.join(lock_types)}\n")
            
        # 更新日志显示 - 只追加新内容
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                # 移动到上次读取的位置
                f.seek(self.last_log_position)
                new_logs = f.readlines()
                if new_logs:
                    # 追加新日志
                    for log in new_logs:
                        # 使用新的日志显示方法
                        if "执行结果" in log:
                            self.log_text.tag_configure("result", foreground="green")
                            self.log_text.insert(tk.END, log, "result")
                        else:
                            self.log_text.insert(tk.END, log)
                    # 保持最新的日志可见
                    self.log_text.see(tk.END)
                    # 更新位置
                    self.last_log_position = f.tell()
                    
                    # 限制显示的行数
                    if int(self.log_text.index('end-1c').split('.')[0]) > 100:
                        # 保留最后100行
                        self.log_text.delete('1.0', 'end-100c')
        except Exception as e:
            print(f"日志更新错误: {str(e)}")
            
        # 更新状态栏
        tx_count = len(self.transactions)
        self.status_var.set(f"当前事务: {self.current_tx_id} | 活跃事务数: {tx_count}")
        
        # 每秒更新一次
        self.root.after(1000, self.update_display)
        
    def execute_sql(self):
        if not self.current_tx_id:
            self.log_text.insert(tk.END, "\n请开始一个事务\n")
            self.log_text.see(tk.END)
            return
            
        sql_text = self.sql_text.get(1.0, tk.END).strip()
        # 按分号分割多条SQL语句
        sql_statements = [stmt.strip() for stmt in sql_text.split(';') if stmt.strip()]
        
        try:
            for sql in sql_statements:
                result = self.sql_parser.execute(self.file_mgr, sql, self.current_tx_id)
                self.log_text.insert(tk.END, f"执行结果: {result}\n")
                self.log_text.see(tk.END)
                
        except Exception as e:
            self.log_text.insert(tk.END, f"\n执行错误: {str(e)}\n")
            self.log_text.see(tk.END)
            
    def on_transaction_selected(self, event):
        """当用户选择事务时触发"""
        selected_tx = self.tx_combobox.get()
        if selected_tx:
            tx_id = int(selected_tx)
            if tx_id in self.transactions:
                self.current_tx_id = tx_id
                self.query_manager.current_transaction = self.transactions[tx_id]
                self.log_text.insert(tk.END, f"\n切换到事务 {tx_id}\n")
                
    def start_new_transaction(self):
        """开始新事务"""
        tx_id = int(time.time() * 1000)
        transaction = Transaction(tx_id, self.concurrency_mgr)
        
        # 设置事务的query_manager
        transaction.query_manager = self.query_manager
        
        # 不再需要设置recovery_manager，因为回滚操作直接使用RecoveryManager
        self.transactions[tx_id] = transaction
        self.current_tx_id = tx_id
        self.query_manager.current_transaction = transaction
        self.tx_combobox.set(str(tx_id))
        self.log_text.insert(tk.END, f"\n开始新事务 {tx_id}\n")
        self.log_text.see(tk.END)
        
    def commit_transaction(self):
        """提交当前事务"""
        if self.current_tx_id:
            try:
                self.transactions[self.current_tx_id].commit()
                self.log_text.insert(tk.END, f"\n事务 {self.current_tx_id} 提交成功\n")
                del self.transactions[self.current_tx_id]
                self.current_tx_id = None
                
                # 自动选择下一个可用事务
                if self.transactions:
                    next_tx_id = list(self.transactions.keys())[0]
                    self.current_tx_id = next_tx_id
                    self.query_manager.current_transaction = self.transactions[next_tx_id]
                    self.tx_combobox.set(str(next_tx_id))
                else:
                    self.start_new_transaction()
                    
            except Exception as e:
                self.log_text.insert(tk.END, f"\n提交失败: {str(e)}\n")
                
    def rollback_transaction(self):
        """回滚当前事务"""
        try:
            if not self.current_tx_id:
                messagebox.showwarning("警告", "没有活跃的事务！")
                return
            
            tx = self.transactions[self.current_tx_id]
            
            # 使用恢复管理器执行回滚
            recovery_mgr = RecoveryManager(self.log_mgr, self.query_manager)
            recovery_mgr.rollback_transaction(self.current_tx_id, tx.operations)
            
            # 释放锁并更新状态
            tx.release_all_locks()
            
            # 清理事务状态
            del self.transactions[self.current_tx_id]
            self.current_tx_id = None
            
            self.log_text.insert(tk.END, "\n事务已回滚\n")
            self.log_text.see(tk.END)
            
            # 开始新事务
            self.start_new_transaction()
            
        except Exception as e:
            self.log_text.insert(tk.END, f"\n事务回滚失败: {str(e)}\n")
            self.log_text.see(tk.END)
            messagebox.showerror("错误", f"事务回滚失败：{str(e)}")

    def recover_system(self):
        """系统恢复功能"""
        try:
            self.log_text.insert(tk.END, "\n=== 开始系统恢复 ===\n")
            
            # 1. 找到最近的检查点
            checkpoint = self.log_mgr.get_last_checkpoint()
            if not checkpoint:
                self.log_text.insert(tk.END, "未找到检查点，无法恢复\n")
                return
            
            self.log_text.insert(tk.END, f"找到检查点: {checkpoint['timestamp']}\n")
            
            # 2. 清空当前状态
            self._clear_current_state()
            
            # 3. 使用恢复管理器执行恢复
            recovery_mgr = RecoveryManager(self.log_mgr, self.query_manager)
            recovery_mgr.recover(checkpoint)
            
            # 4. 重置事务状态
            self.start_new_transaction()
            
            self.log_text.insert(tk.END, "\n=== 系统恢复完成 ===\n")
            self.log_text.see(tk.END)
            
        except Exception as e:
            self.log_text.insert(tk.END, f"\n系统恢复失败: {str(e)}\n")
            self.log_text.see(tk.END)
            # 确保即使恢复失败也创建新事务
            self.start_new_transaction()

    def _find_create_statement(self, table_name: str) -> str:
        """从日志中找到表的创建语句"""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if 'CREATE' in line and table_name in line and 'fields' in line:
                        # 从日志消息中提取字段信息
                        fields_str = line.split('fields: ')[1].strip('[]')
                        fields = [f.strip().strip("'") for f in fields_str.split(',')]
                        # 构造CREATE TABLE语句
                        if table_name == 'student':
                            return "CREATE TABLE student (id INT, name STRING, age INT)"
                        elif table_name == 'account':
                            return "CREATE TABLE account (id INT, name STRING, balance INT)"
            return None
        except Exception as e:
            print(f"Error finding create statement: {e}")
            return None

    def _find_inserts_before_checkpoint(self, table_name: str, checkpoint_time: str) -> list:
        """找到检查点之前的所有插入语句"""
        inserts = []
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # 从头开始读取直到检查点
                for line in lines:
                    # 如果到达检查点，停止读取
                    if f"=== CHECKPOINT START [{checkpoint_time}]" in line:
                        break
                    
                    # 解析INSERT记录
                    if 'INSERT' in line and 'Record inserted' in line and table_name in line:
                        try:
                            # 示例日志行：[时间] TX id - INSERT: Record inserted into student: 1, '张三', 20
                            # 提取表名和值
                            parts = line.split('Record inserted into ')
                            if len(parts) > 1:
                                data_part = parts[1]  # student: 1, '张三', 20
                                table, values = data_part.split(': ', 1)
                                if table.strip() == table_name:
                                    insert_stmt = f"INSERT INTO {table} VALUES ({values.strip()})"
                                    self.log_text.insert(tk.END, f"找到插入记录: {insert_stmt}\n")
                                    inserts.append(insert_stmt)
                        except Exception as e:
                            self.log_text.insert(tk.END, f"解析插入记录失败: {str(e)}\n")
                            continue
                        
            self.log_text.insert(tk.END, f"共找到 {len(inserts)} 条插入记录\n")
            return inserts
        except Exception as e:
            self.log_text.insert(tk.END, f"读取日志失败: {str(e)}\n")
            return []

    def _clear_current_state(self):
        """清空当前状态"""
        # 1. 结束所有活跃事务
        for tx_id, tx in list(self.transactions.items()):
            tx.rollback()
            del self.transactions[tx_id]
        self.current_tx_id = None
        
        # 2. 清空并发管理器中的锁
        self.concurrency_mgr.clear_all_locks()
        
        # 3. 删除数据文件
        if os.path.exists(self.db_directory):
            import shutil
            shutil.rmtree(self.db_directory)
            os.makedirs(self.db_directory)
        
        # 4. 重新初始化系统组件
        self.file_mgr = FileMgr(self.db_directory)
        self.table_metadata = TableMetadata(self.file_mgr)
        self.query_manager = QueryManager(self.table_metadata, TableScan, self.log_mgr)
        self.sql_parser = SQLParser(self.query_manager)
        
        # 5. 设置相互引用
        self.query_manager.set_sql_parser(self.sql_parser)

    def create_checkpoint(self):
        """创建检查点"""
        try:
            self.log_text.insert(tk.END, "\n=== 创建检查点 ===\n")
            
            # 收集当前状态
            checkpoint_data = {
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                'active_transactions': list(self.transactions.keys()),
                'tables': self.table_metadata.list_tables(),
                'dirty_pages': []  # 从缓冲区管理器获取
            }
            
            # 写入检查点日志
            self.log_mgr.write_checkpoint(checkpoint_data)
            
            # 刷新缓冲区
            self.file_mgr.flush_all()
            
            self.log_text.insert(tk.END, "检查点创建成功\n")
            self.log_text.see(tk.END)
            
        except Exception as e:
            self.log_text.insert(tk.END, f"\n创建检查点失败: {str(e)}\n")
            self.log_text.see(tk.END)

    def clear_database(self):
        """清空数据库"""
        try:
            # 弹出确认对话框
            if not messagebox.askyesno("确认操作", 
                "此操作将清空所有数据！\n是否继续？",
                icon='warning'):
                return
            
            self.log_text.insert(tk.END, "\n=== 开始清空数据库 ===\n")
            
            # 1. 结束所有活跃事务
            for tx_id, tx in list(self.transactions.items()):
                try:
                    tx.release_all_locks()  # 只释放锁，不执行完整回滚
                    del self.transactions[tx_id]
                except Exception as e:
                    print(f"[WARNING] Failed to clean up transaction {tx_id}: {e}")
                    
            self.current_tx_id = None
            
            # 2. 清空并发管理器中的锁
            self.concurrency_mgr.clear_all_locks()
            
            # 3. 删除数据文件
            if os.path.exists(self.db_directory):
                import shutil
                shutil.rmtree(self.db_directory)
                os.makedirs(self.db_directory)
            
            # 4. 清空日志文件
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write('')
            self.last_log_position = 0
            
            # 5. 重新初始化���统组件
            self.file_mgr = FileMgr(self.db_directory)
            self.table_metadata = TableMetadata(self.file_mgr)
            self.query_manager = QueryManager(self.table_metadata, TableScan, self.log_mgr)
            self.sql_parser = SQLParser(self.query_manager)
            self.query_manager.set_sql_parser(self.sql_parser)
            
            # 6. 开始新事务
            self.start_new_transaction()
            
            self.log_text.insert(tk.END, "数据库已清空\n")
            self.log_text.insert(tk.END, "=== 清空操作完成 ===\n")
            self.log_text.see(tk.END)
            
            # 提示用户
            messagebox.showinfo("操作完成", "数据库已清空！")
            
        except Exception as e:
            self.log_text.insert(tk.END, f"\n清空数据库失败: {str(e)}\n")
            self.log_text.see(tk.END)
            messagebox.showerror("错误", f"清空数据库失败：{str(e)}")

    def run(self):
        """运行GUI程序"""
        self.root.mainloop()

    def _write_log(self, message):
        """向GUI日志区域写入消息"""
        # 如果是执行结果，使用不同的标签颜色
        if "执行结果" in message:
            # 使用tag来设置文本颜色
            self.log_text.tag_configure("result", foreground="green")
            self.log_text.insert(tk.END, message + "\n", "result")
        else:
            # 普通日志使用默认颜色
            self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

if __name__ == "__main__":
    gui = DBMSGUI()
    gui.run()
