import re

class SQLParser:
    """
    解析 SQL 语句并调用 QueryManager 执行
    """
    def __init__(self, query_manager):
        self.query_manager = query_manager

    def execute(self, file_mgr, sql: str, tx_id: int):
        """执行SQL语句"""
        try:
            # 去除注释
            sql_lines = []
            for line in sql.split('\n'):
                line = line.strip()
                if line and not line.startswith('--'):
                    sql_lines.append(line)
            
            sql = ' '.join(sql_lines)
            if not sql:
                return
            
            # 解析SQL
            command = sql.strip().split()[0].upper()
            
            if command == "CREATE":
                return self._execute_create(file_mgr, sql, tx_id)
            elif command == "INSERT":
                return self._execute_insert(file_mgr, sql, tx_id)
            elif command == "SELECT":
                return self._execute_select(file_mgr, sql, tx_id)
            elif command == "UPDATE":
                return self._execute_update(file_mgr, sql, tx_id)
            elif command == "DELETE":
                return self._execute_delete(file_mgr, sql, tx_id)
            else:
                raise Exception(f"不支持的SQL命令: {command}")
            
        except Exception as e:
            print(f"错误: {str(e)}")
            raise e

    def _execute_create(self, file_mgr, sql: str, tx):
        """执行创建表语句"""
        sql = sql.strip()
        
        if sql.upper().startswith("CREATE TABLE"):
            # 解析创建表语句
            match = re.match(r"CREATE TABLE (\w+) \((.*)\)", sql)
            if not match:
                raise ValueError("Invalid CREATE TABLE syntax")
            
            table_name = match.group(1)
            fields_str = match.group(2)
            fields = []
            types = []
            
            for field_def in fields_str.split(","):
                field_def = field_def.strip()
                field_name, field_type = field_def.split()
                fields.append(field_name)
                types.append(field_type)
            
            return self.query_manager.create_table(table_name, fields, types)
            
    def _execute_insert(self, file_mgr, sql: str, tx):
        """执行插入语句"""
        sql = sql.strip()
        
        if sql.upper().startswith("INSERT INTO"):
            # 解析插入语句
            match = re.match(r"INSERT INTO (\w+) VALUES \((.*)\)", sql)
            if not match:
                raise ValueError("Invalid INSERT syntax")
            
            table_name = match.group(1)
            values = match.group(2)
            return self.query_manager.insert_query(file_mgr, table_name, values.encode('utf-8'), tx)
            
    def _create_condition_func(self, table_name, where_clause):
        """创建统一的条件判断函数"""
        def condition_func(record):
            if isinstance(record, bytes):
                record_str = record.decode('utf-8').strip()
            else:
                record_str = str(record).strip()
                
            # 解析记录
            record_parts = [p.strip().strip("'") for p in record_str.split(",")]
            fields = self.query_manager.table_metadata.get_table_fields(table_name)
            field_names = [f[0] for f in fields]
            
            # 解析 WHERE 条件
            field, op, value = re.match(r"(\w+)\s*([=><])\s*(.*)", where_clause).groups()
            field_idx = field_names.index(field)
            record_value = record_parts[field_idx]
            value = value.strip("'")  # 移除引号
            
            # 根据字段类型行比较
            field_type = fields[field_idx][1]
            if field_type == "INT":
                record_value = int(record_value)
                value = int(value)
            elif field_type == "FLOAT":
                record_value = float(record_value)
                value = float(value)
                
            # 执行比较
            if op == "=":
                return record_value == value
            elif op == ">":
                return record_value > value
            elif op == "<":
                return record_value < value
            return False
            
        return condition_func

    def _execute_select(self, file_mgr, sql: str, tx):
        """执行查询语句"""
        # 解析查询语句
        match = re.match(r"SELECT \* FROM (\w+)(?:\s+WHERE\s+(.*))?", sql)
        if not match:
            raise ValueError("Invalid SELECT syntax")
        
        table_name = match.group(1)
        where_clause = match.group(2)
        
        # 创建条件函数
        condition_func = None
        if where_clause:
            condition_func = self._create_condition_func(table_name, where_clause)
        
        # 执行查询
        return self.query_manager.select_query(table_name, condition_func)
            
    def _execute_update(self, file_mgr, sql: str, tx):
        """执行更新语句"""
        # 解析更新语句
        match = re.match(r"UPDATE (\w+) SET (.*) WHERE (.*)", sql)
        if not match:
            raise ValueError("Invalid UPDATE syntax")
        
        table_name = match.group(1)
        set_clause = match.group(2)
        where_clause = match.group(3)
        
        # 解析 SET 子句
        set_values = {}
        for item in set_clause.split(","):
            field, expr = item.strip().split("=")
            field = field.strip()
            expr = expr.strip()
            
            # 检查是否是计算表达式
            if re.match(r'(\w+)\s*[\+\-]\s*\d+', expr):
                # 匹配形如 "field + number" 或 "field - number" 的表达式
                if '+' in expr:
                    field_name, amount = expr.split('+')
                    set_values[field] = {
                        'type': 'add',
                        'amount': int(amount.strip())
                    }
                elif '-' in expr:
                    field_name, amount = expr.split('-')
                    set_values[field] = {
                        'type': 'subtract',
                        'amount': int(amount.strip())
                    }
            else:
                # 直接赋值
                set_values[field] = {
                    'type': 'direct',
                    'value': expr.strip("'")
                }
        
        # 创建条件函数
        condition_func = self._create_condition_func(table_name, where_clause)
        
        return self.query_manager.update_query(file_mgr, table_name, set_values, condition_func, tx)
            
    def _execute_delete(self, file_mgr, sql: str, tx):
        """执行删除语句"""
        sql = sql.strip()
        
        if sql.upper().startswith("DELETE"):
            # 解析删除语句
            match = re.match(r"DELETE FROM (\w+) WHERE (.*)", sql)
            if not match:
                raise ValueError("Invalid DELETE syntax")
            
            table_name = match.group(1)
            where_clause = match.group(2)
            
            # 创建条件函数
            def condition_func(record):
                if isinstance(record, bytes):
                    record_str = record.decode('utf-8').strip()
                else:
                    record_str = str(record).strip()
                    
                # 解析记录
                record_parts = [p.strip().strip("'") for p in record_str.split(",")]
                fields = self.query_manager.table_metadata.get_table_fields(table_name)
                field_names = [f[0] for f in fields]
                
                # 解析 WHERE 条件
                field, op, value = re.match(r"(\w+)\s*([=><])\s*(.*)", where_clause).groups()
                field_idx = field_names.index(field)
                record_value = record_parts[field_idx]
                
                # 比较值
                if op == "=":
                    return record_value == value.strip("'")
                elif op == ">":
                    return float(record_value) > float(value)
                elif op == "<":
                    return float(record_value) < float(value)
                return False
            
            return self.query_manager.delete_query(file_mgr, table_name, condition_func, tx)
