class ExecutionPlanner:
    """
    简单的执行计划生成器
    """
    def __init__(self, query_manager):
        self.query_manager = query_manager

    def generate_plan(self, sql: str):
        """
        生成简单执行计划
        :param sql: SQL 查询
        :return: 执行计划（字符串表示）
        """
        tokens = sql.strip().split()
        command = tokens[0].upper()

        if command == "SELECT":
            table_name = tokens[3]  # SELECT * FROM table_name
            return f"Execution Plan: Sequential Scan on table {table_name}"
        elif command == "INSERT":
            table_name = tokens[2]
            return f"Execution Plan: Insert into table {table_name}"
        elif command == "UPDATE":
            table_name = tokens[1]
            return f"Execution Plan: Update table {table_name}"
        elif command == "DELETE":
            table_name = tokens[2]
            return f"Execution Plan: Delete from table {table_name}"
        else:
            raise Exception(f"Unsupported SQL operation: {command}")
