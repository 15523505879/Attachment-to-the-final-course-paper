import mysql.connector
from cmd import Cmd
import subprocess
import os

# 初始化数据库，创建必要的表并插入示例数据
def initialize_database():
    try:
        # 连接到MySQL服务器
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='152152'
        )
        cursor = conn.cursor()

        # 创建名为library_management的数据库（如果不存在）
        cursor.execute("CREATE DATABASE IF NOT EXISTS library_management;")
        print("数据库 'library_management' 创建成功。")

        # 使用library_management数据库
        cursor.execute("USE library_management;")
        print("正在使用数据库 'library_management'。")

        # 创建books表（如果不存在），包含书ID、书名、作者、ISBN号和是否可用字段
        create_books_table_query = """
        CREATE TABLE IF NOT EXISTS books (
            book_id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            author VARCHAR(255) NOT NULL,
            isbn VARCHAR(20),
            available BOOLEAN DEFAULT TRUE
        );
        """
        cursor.execute(create_books_table_query)
        print("表 'books' 创建成功。")

        # 创建members表（如果不存在），包含成员ID、姓名和电子邮件字段
        create_members_table_query = """
        CREATE TABLE IF NOT EXISTS members (
            member_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL
        );
        """
        cursor.execute(create_members_table_query)
        print("表 'members' 创建成功。")

        # 创建borrowed_books表（如果不存在），包含借阅ID、书ID、成员ID、借阅日期和归还日期字段
        create_borrowed_books_table_query = """
        CREATE TABLE IF NOT EXISTS borrowed_books (
            borrow_id INT AUTO_INCREMENT PRIMARY KEY,
            book_id INT,
            member_id INT,
            borrow_date DATE DEFAULT (CURRENT_DATE),
            return_date DATE,
            FOREIGN KEY (book_id) REFERENCES books(book_id),
            FOREIGN KEY (member_id) REFERENCES members(member_id)
        );
        """
        cursor.execute(create_borrowed_books_table_query)
        print("表 'borrowed_books' 创建成功。")

        # 删除现有数据以避免重复键错误
        drop_existing_data_queries = [
            "DELETE FROM borrowed_books;",
            "DELETE FROM books;",
            "DELETE FROM members;"
        ]

        for query in drop_existing_data_queries:
            cursor.execute(query)

        # 插入示例数据到books表中
        insert_books_data_queries = [
            "INSERT INTO books (title, author, isbn) VALUES ('西游记', '吴承恩', '9780743273565');",
            "INSERT INTO books (title, author, isbn) VALUES ('三国演义', '罗贯中', '9780060935467');",
            "INSERT INTO books (title, author, isbn) VALUES ('红楼梦', '曹雪芹', '9780451524935');",
            "INSERT INTO books (title, author, isbn) VALUES ('水浒传', '施耐庵', '9780141439518');"
        ]

        for query in insert_books_data_queries:
            cursor.execute(query)

        # 插入示例数据到members表中
        insert_members_data_queries = [
            "INSERT INTO members (name, email) VALUES ('刘权林', 'liuquanlin@example.com');",
            "INSERT INTO members (name, email) VALUES ('徐昌盛', 'xuchangsheng@example.com');",
            "INSERT INTO members (name, email) VALUES ('沈鑫', 'shenxin@example.com');",
            "INSERT INTO members (name, email) VALUES ('李浩', 'lihao@example.com');"
        ]

        for query in insert_members_data_queries:
            cursor.execute(query)

        # 创建触发器，在书籍归还时自动更新书籍状态为可用
        create_trigger_query = """
        CREATE TRIGGER after_book_return
        AFTER UPDATE ON borrowed_books
        FOR EACH ROW
        BEGIN
            IF NEW.return_date IS NOT NULL THEN
                UPDATE books SET available = TRUE WHERE book_id = NEW.book_id;
            END IF;
        END;
        """
        cursor.execute(create_trigger_query)

        conn.commit()
        print("触发器 'after_book_return' 创建成功。")
        print("示例数据插入成功。")
    except mysql.connector.Error as err:
        print(f"错误: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# 定义一个继承自Cmd类的SQLShell类，用于处理SQL命令行操作
class SQLShell(Cmd):
    intro = '欢迎来到SQL命令行工具。输入help或?列出可用命令。\n'
    prompt = '(sql) '

    def __init__(self, host, user, password, database):
        super().__init__()
        # 连接到指定的MySQL数据库
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

    def do_execute(self, line):
        """执行一条SQL语句。"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(line)
            # 如果是SELECT查询，则打印结果；否则提交更改
            if line.strip().lower().startswith('select'):
                results = cursor.fetchall()
                for row in results:
                    print(row)
            else:
                self.conn.commit()
                print("查询执行成功。")
        except mysql.connector.Error as err:
            print(f"错误: {err}")
        finally:
            cursor.close()

    def default(self, line):
        """假设未知命令为SQL语句并尝试执行。"""
        self.do_execute(line)

    def do_borrow(self, line):
        """借阅一本书。用法：borrow <书ID> <成员ID>"""
        args = line.split()
        if len(args) != 2:
            print("用法：borrow <书ID> <成员ID>")
            return

        book_id = int(args[0])
        member_id = int(args[1])

        try:
            cursor = self.conn.cursor()

            # 检查书籍是否可借阅
            check_availability_query = """
            SELECT available FROM books WHERE book_id = %s;
            """
            cursor.execute(check_availability_query, (book_id,))
            result = cursor.fetchone()

            if not result or not result[0]:
                print(f"书ID {book_id} 当前不可借阅。")
                return

            # 更新书籍状态为不可借阅
            update_book_query = """
            UPDATE books SET available = FALSE WHERE book_id = %s;
            """
            cursor.execute(update_book_query, (book_id,))

            # 插入借阅记录
            insert_borrow_record_query = """
            INSERT INTO borrowed_books (book_id, member_id) VALUES (%s, %s);
            """
            cursor.execute(insert_borrow_record_query, (book_id, member_id))

            self.conn.commit()
            print(f"书ID {book_id} 已被成员ID {member_id} 借阅。")
        except mysql.connector.Error as err:
            print(f"错误: {err}")
        finally:
            cursor.close()

    def do_return_book(self, line):
        """归还一本书。用法：return_book <书ID> <成员ID>"""
        args = line.split()
        if len(args) != 2:
            print("用法：return_book <书ID> <成员ID>")
            return

        book_id = int(args[0])
        member_id = int(args[1])

        try:
            cursor = self.conn.cursor()

            # 检查该书籍是否由该成员借出且未归还
            check_borrow_query = """
            SELECT borrow_id FROM borrowed_books WHERE book_id = %s AND member_id = %s AND return_date IS NULL;
            """
            cursor.execute(check_borrow_query, (book_id, member_id))
            result = cursor.fetchone()

            if not result:
                print(f"书ID {book_id} 当前未被成员ID {member_id} 借出。")
                return

            # 更新借阅记录以标记归还日期
            update_borrow_record_query = """
            UPDATE borrowed_books SET return_date = CURDATE() WHERE borrow_id = %s;
            """
            cursor.execute(update_borrow_record_query, (result[0],))

            self.conn.commit()
            print(f"书ID {book_id} 已被成员ID {member_id} 归还。")
        except mysql.connector.Error as err:
            print(f"错误: {err}")
        finally:
            cursor.close()

    def do_backup(self, filename):
        """备份数据库到文件。用法：backup <filename.sql>"""
        try:
            # mysqldump路径
            mysql_dump_path = r"C:\Program Files\MySQL\mysql-8.0.40-winx64\bin\mysqldump.exe"
            print(f"尝试使用mysqldump路径: {mysql_dump_path}")

            # 检查mysqldump是否存在
            if not os.path.isfile(mysql_dump_path):
                print(f"错误: 文件 {mysql_dump_path} 不存在。")
                return

            # 执行备份命令
            subprocess.run([
                mysql_dump_path,
                "-h", "localhost",
                "-u", "root",
                "-p152152",
                "library_management"
            ], stdout=open(filename, 'w'), check=True)
            print(f"数据库已备份到 {filename} 成功。")
        except subprocess.CalledProcessError as err:
            print(f"备份过程中发生错误: {err}")

    def do_restore(self, filename):
        """从文件恢复数据库。用法：restore <filename.sql>"""
        try:
            # mysql路径
            mysql_path = r"C:\Program Files\MySQL\mysql-8.0.40-winx64\bin\mysql.exe"

            # 调试信息：打印路径以验证
            print(f"尝试使用mysql路径: {mysql_path}")

            # 检查mysql是否存在
            if not os.path.isfile(mysql_path):
                print(f"错误: 文件 {mysql_path} 不存在。")
                return

            # 检查备份文件是否存在
            if not os.path.isfile(filename):
                print(f"文件 {filename} 不存在。")
                return

            # 执行恢复命令
            subprocess.run([
                mysql_path,
                "-h", "localhost",
                "-u", "root",
                "-p152152",
                "library_management"
            ], stdin=open(filename), check=True)
            print(f"数据库已从 {filename} 恢复成功。")
        except subprocess.CalledProcessError as err:
            print(f"恢复过程中发生错误: {err}")

    def do_exit(self, line):
        """退出SQL shell。"""
        print("正在退出...")
        return True

    def do_EOF(self, line):
        """在EOF（Ctrl+D）时退出。"""
        return self.do_exit(line)

    def close(self):
        if self.conn.is_connected():
            self.conn.close()

if __name__ == '__main__':
    initialize_database()
    sql_shell = SQLShell(host='localhost', user='root', password='152152', database='library_management')
    try:
        sql_shell.cmdloop()
    finally:
        sql_shell.close()
