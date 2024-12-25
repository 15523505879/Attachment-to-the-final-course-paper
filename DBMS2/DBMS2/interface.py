
class EmbeddedDBInterface:
    """
    数据库接口类，提供简单的接口执行 SQL
    """
    def __init__(self, file_mgr, sql_parser, execution_planner):
        self.file_mgr = file_mgr
        self.sql_parser = sql_parser
        self.execution_planner = execution_planner

    def execute_sql(self, sql: str):
        print(f"[DEBUG] EmbeddedDBInterface received SQL: {sql}")
        return self.sql_parser.execute(self.file_mgr, sql)
