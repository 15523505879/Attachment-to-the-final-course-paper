from BadSyntaxException import BadSyntaxException
from Tokenizer import Tokenizer


class Lexer:
    """词法分析器"""

    def __init__(self, s: str):
        self.__keywords = self.__initKeywords()
        self.__tok = Tokenizer(s)
        self.__nextToken()

    def matchDelim(self, d: str) -> bool:
        """判断当前标记是否是指定的分隔符字符"""
        return d == self.__tok.ttype

    def matchIntConstant(self) -> bool:
        """判断当前标记是否是整数"""
        return self.__tok.ttype == Tokenizer.TT_NUMBER

    # 如果当前标记是字符串，则返回true。
    def matchStringConstant(self):
        """判断当前标记是否是字符串"""
        return self.__tok.ttype == '\'' or self.__tok.ttype == '\"'

    def matchKeyword(self, w: str) -> bool:
        """判断当前标记是否是指定的关键字"""
        return self.__tok.ttype == Tokenizer.TT_WORD and self.__tok.sval == w

    def matchId(self) -> bool:
        """判断当前标记是否是合法的标识符"""
        return self.__tok.ttype == Tokenizer.TT_WORD and self.__tok.sval not in self.__keywords

    def eatDelim(self, d: str):
        """如果当前标记不是指定的分隔符，则抛出异常

        否则移动到下一个标记
        """
        if not self.matchDelim(d):
            raise BadSyntaxException
        self.__nextToken()

    def eatIntConstant(self) -> int:
        """如果当前标记不是整数，则抛出异常

        否则返回该整数值并移动到下一个标记
        """
        if not self.matchIntConstant():
            raise BadSyntaxException
        i = self.__tok.nval
        self.__nextToken()
        return i

    def eatStringConstant(self) -> str:
        """如果当前标记不是字符串，则抛出异常。

        否则，返回该字符串并移动到下一个标记。
        """
        if not self.matchStringConstant():
            raise BadSyntaxException
        s = self.__tok.sval
        self.__nextToken()
        return s

    def eatKeyword(self, w: str):
        """如果当前标记不是指定的关键字，则抛出异常。

        否则，移动到下一个标记。
        """
        if not self.matchKeyword(w):
            raise BadSyntaxException
        self.__nextToken()

    def eatId(self) -> str:
        """如果当前标记不是标识符，则抛出异常。

        否则，返回标识符字符串并移动到下一个标记。
        """
        if not self.matchId():
            raise BadSyntaxException
        s = self.__tok.sval
        self.__nextToken()
        return s

    def __nextToken(self):
        try:
            self.__tok.nextToken()
        except RuntimeError:
            raise BadSyntaxException

    def __initKeywords(self):
        return ["select", "from", "where", "and",
                "insert", "into", "values", "delete", "update", "set",
                "create", "table", "int", "varchar", "view", "as", "index", "on", "tables", "show"]
