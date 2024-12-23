import re


class Tokenizer:
    """自实现的一个Tokenizer包

    Attributes:
        TT_NUMBER: 数字标识符
        TT_WORD: 字符串标识符
        TT_EOF: 表示结束
        __tokens: 被非字符(除了下划线)分开后的字符串
        __index: 列表的索引
        nval: 整数值
        sval: 字符串值
        ttype: 类型
    """

    TT_NUMBER = -2
    TT_WORD = -3
    TT_EOF = -1

    def __init__(self, inputString: str):
        # 匹配字符串中的字母、数字和下划线
        self.__tokens = re.findall(r"\w+|[^\w\s]", inputString)
        self.__index = 0
        self.nval = 0
        self.sval = None
        self.ttype = None

    def nextToken(self) -> int:
        if self.__index < len(self.__tokens):
            token = self.__tokens[self.__index]
            self.__index += 1
            if token.isdigit():
                self.ttype = self.TT_NUMBER
                self.nval = int(token)
                self.sval = None
            elif self.__judgeAlpha(token.replace('_', '')):
                self.ttype = self.TT_WORD
                self.sval = token
                self.nval = 0
            elif token == '\'' or token == '\"':
                self.__handleQuotation(token)
            else:
                self.nval = 0
                self.sval = None
                self.ttype = token
            return self.ttype
        else:
            self.ttype = -1
            self.sval = None
            self.nval = 0
            return self.TT_EOF

    def __judgeAlpha(self, token: str) -> bool:
        """判断是否为字符串

        这里的字符串可以包含数字
        """
        flag = 0
        for i in token:
            if not i.isalpha() and not i.isdigit():
                return False
            if i.isdigit():
                flag += 1
        if flag == len(token):
            return False
        return True

    def __handleQuotation(self, token: str):
        if token == '\'':
            self.__updateSval('\'')
        elif token == '\"':
            self.__updateSval('\"')
        self.ttype = token

    def __updateSval(self, quotation: str):
        """获取引号中的内容"""
        tempStr = ""
        for i in range(self.__index, len(self.__tokens)):
            tokenValue = self.__tokens[i]
            if tokenValue != quotation:
                tempStr += tokenValue
            else:
                self.__index = i + 1
                break
            if i == len(self.__tokens) - 1:
                self.__index = i + 1
        self.sval = tempStr
        self.nval = 0
