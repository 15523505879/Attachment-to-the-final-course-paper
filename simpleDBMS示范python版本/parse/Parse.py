from typing import List, Collection
from Lexer import Lexer
from Constant import Constant
from Schema import Schema
from Expression import Expression
from Predicate import Predicate
from Term import Term
from QueryData import QueryData
from InsertData import InsertData
from DeleteData import DeleteData
from ModifyData import ModifyData
from CreateTableData import CreateTableData
from CreateViewData import CreateViewData
from CreateIndexData import CreateIndexData


class Parser:
    """解析器

    Attributes:
        __lex: 词法分析器
    """

    def __init__(self, s: str):
        self.__lex = Lexer(s)

    # 解析谓词、术语、表达式、常量和字段的方法
    def field(self) -> str:
        return self.__lex.eatId()

    def constant(self) -> Constant:
        if self.__lex.matchStringConstant():
            return Constant(self.__lex.eatStringConstant())
        else:
            return Constant(self.__lex.eatIntConstant())

    def expression(self) -> Expression:
        if self.__lex.matchId():
            return Expression(self.field())
        else:
            return Expression(self.constant())

    def term(self) -> Term:
        lhs = self.expression()
        self.__lex.eatDelim('=')
        rhs = self.expression()
        return Term(lhs, rhs)

    def predicate(self) -> Predicate:
        pred = Predicate(self.term())
        if self.__lex.matchKeyword("and"):
            self.__lex.eatKeyword("and")
            pred.conjoinWith(self.predicate())
        return pred

    def query(self) -> QueryData:
        """解析查询命令"""
        self.__lex.eatKeyword("select")
        fields = self.__selectList()
        self.__lex.eatKeyword("from")
        tables = self.__tableList()
        pred = Predicate()
        if self.__lex.matchKeyword("where"):
            self.__lex.eatKeyword("where")
            pred = self.predicate()
        return QueryData(fields, tables, pred)

    # # 解析查询数据库中的表
    # def queryTable(self):
    #     self.__lex.eatKeyword("show")
    #     self.__lex.eatKeyword("tables")

    def __selectList(self) -> List[str]:
        L = [self.field()]
        if self.__lex.matchDelim(','):
            self.__lex.eatDelim(',')
            L.extend(self.__selectList())
        return L

    def __tableList(self) -> Collection[str]:
        L = [self.__lex.eatId()]
        if self.__lex.matchDelim(','):
            self.__lex.eatDelim(',')
            L.extend(self.__tableList())
        return L

    def updateCmd(self):
        """解析更新命令，包括插入、删除和更新"""
        if self.__lex.matchKeyword("insert"):
            return self.insert()
        elif self.__lex.matchKeyword("delete"):
            return self.delete()
        elif self.__lex.matchKeyword("update"):
            return self.modify()
        else:
            return self.__create()

    def __create(self):
        self.__lex.eatKeyword("create")
        if self.__lex.matchKeyword("table"):
            return self.createTable()
        elif self.__lex.matchKeyword("view"):
            return self.createView()
        else:
            return self.createIndex()

    def delete(self) -> DeleteData:
        """解析删除命令"""
        self.__lex.eatKeyword("delete")
        self.__lex.eatKeyword("from")
        tblname = self.__lex.eatId()
        pred = Predicate()
        if self.__lex.matchKeyword("where"):
            self.__lex.eatKeyword("where")
            pred = self.predicate()
        return DeleteData(tblname, pred)

    def insert(self) -> InsertData:
        """解析插入命令"""
        self.__lex.eatKeyword("insert")
        self.__lex.eatKeyword("into")
        tblname = self.__lex.eatId()
        self.__lex.eatDelim('(')
        flds = self.__fieldList()
        self.__lex.eatDelim(')')
        self.__lex.eatKeyword("values")
        self.__lex.eatDelim('(')
        vals = self.__constList()
        self.__lex.eatDelim(')')
        return InsertData(tblname, flds, vals)

    def __fieldList(self) -> List[str]:
        L = [self.field()]
        if self.__lex.matchDelim(','):
            self.__lex.eatDelim(',')
            L.extend(self.__fieldList())
        return L

    def __constList(self) -> List[Constant]:
        L = [self.constant()]
        if self.__lex.matchDelim(','):
            self.__lex.eatDelim(',')
            L.extend(self.__constList())
        return L

    def modify(self) -> ModifyData:
        """解析修改命令"""
        self.__lex.eatKeyword("update")
        tblname = self.__lex.eatId()
        self.__lex.eatKeyword("set")
        fldname = self.field()
        self.__lex.eatDelim('=')
        newval = self.expression()
        pred = Predicate()
        if self.__lex.matchKeyword("where"):
            self.__lex.eatKeyword("where")
            pred = self.predicate()
        return ModifyData(tblname, fldname, newval, pred)

    def createTable(self) -> CreateTableData:
        """解析创建表命令"""
        self.__lex.eatKeyword("table")
        tblname = self.__lex.eatId()
        self.__lex.eatDelim('(')
        sch = self.__fieldDefs()
        self.__lex.eatDelim(')')
        return CreateTableData(tblname, sch)

    def __fieldDefs(self) -> Schema:
        schema = self.__fieldDef()
        if self.__lex.matchDelim(','):
            self.__lex.eatDelim(',')
            schema2 = self.__fieldDefs()
            schema.addAll(schema2)
        return schema

    def __fieldDef(self) -> Schema:
        fldname = self.field()
        return self.__fieldType(fldname)

    def __fieldType(self, fldname: str) -> Schema:
        schema = Schema()
        if self.__lex.matchKeyword("int"):
            self.__lex.eatKeyword("int")
            schema.addIntField(fldname)
        else:
            self.__lex.eatKeyword("varchar")
            self.__lex.eatDelim('(')
            strLen = self.__lex.eatIntConstant()
            self.__lex.eatDelim(')')
            schema.addStringField(fldname, strLen)
        return schema

    def createView(self) -> CreateViewData:
        """解析创建视图命令"""
        self.__lex.eatKeyword("view")
        viewname = self.__lex.eatId()
        self.__lex.eatKeyword("as")
        qd = self.query()
        return CreateViewData(viewname, qd)

    def createIndex(self) -> CreateIndexData:
        """解析创建索引命令"""
        self.__lex.eatKeyword("index")
        idxname = self.__lex.eatId()
        self.__lex.eatKeyword("on")
        tblname = self.__lex.eatId()
        self.__lex.eatDelim('(')
        fldname = self.field()
        self.__lex.eatDelim(')')
        return CreateIndexData(idxname, tblname, fldname)
