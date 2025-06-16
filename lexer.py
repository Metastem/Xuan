"""
玄语言词法分析器

这个模块实现了玄语言的词法分析器，负责将源代码文本转换为标记(tokens)序列。
"""

import re
from enum import Enum, auto
from xuan.exceptions import LexerError

class TokenType(Enum):
    """标记类型枚举"""
    # 关键字
    DEFINE = auto()       # 定义
    CLASS = auto()        # 类
    IF = auto()           # 如果
    ELSE = auto()         # 否则
    ELIF = auto()         # 否则如果
    WHILE = auto()        # 当
    FOR = auto()          # 对于
    IN = auto()           # 在
    RETURN = auto()       # 返回
    TRY = auto()          # 尝试
    EXCEPT = auto()       # 捕获
    FINALLY = auto()      # 最后
    IMPORT = auto()       # 导入
    FROM = auto()         # 从
    TRUE = auto()         # 真
    FALSE = auto()        # 假
    NONE = auto()         # 空
    SELF = auto()         # 自身
    SUPER = auto()        # 父类
    NONLOCAL = auto()     # 非局部
    GLOBAL = auto()       # 全局
    ASSERT = auto()       # 断言
    BREAK = auto()        # 中断
    CONTINUE = auto()     # 继续
    PASS = auto()         # 传递
    DEL = auto()          # 删除
    RAISE = auto()        # 提升
    WITH = auto()         # 使用
    AS = auto()           # 作为
    ASYNC = auto()        # 异步
    AWAIT = auto()        # 等待
    
    # 标识符和字面量
    IDENTIFIER = auto()   # 标识符
    INTEGER = auto()      # 整数
    FLOAT = auto()        # 浮点数
    STRING = auto()       # 字符串
    F_STRING = auto()     # 格式化字符串
    F_STRING_START = auto() # 格式化字符串开始
    
    # 运算符
    PLUS = auto()         # +
    MINUS = auto()        # -
    MULTIPLY = auto()     # *
    DIVIDE = auto()       # /
    MODULO = auto()       # %
    POWER = auto()        # **
    FLOOR_DIVIDE = auto() # //
    
    # 比较运算符
    EQUAL = auto()        # ==
    NOT_EQUAL = auto()    # !=
    LESS = auto()         # <
    LESS_EQUAL = auto()   # <=
    GREATER = auto()      # >
    GREATER_EQUAL = auto() # >=
    
    # 逻辑运算符
    AND = auto()          # 且
    OR = auto()           # 或
    NOT = auto()          # 非
    
    # 赋值运算符
    ASSIGN = auto()       # =
    PLUS_ASSIGN = auto()  # +=
    MINUS_ASSIGN = auto() # -=
    MULTIPLY_ASSIGN = auto() # *=
    DIVIDE_ASSIGN = auto() # /=
    MODULO_ASSIGN = auto() # %=
    
    # 分隔符
    LPAREN = auto()       # (
    RPAREN = auto()       # )
    LBRACKET = auto()     # [
    RBRACKET = auto()     # ]
    LBRACE = auto()       # {
    RBRACE = auto()       # }
    COMMA = auto()        # ,
    DOT = auto()          # .
    COLON = auto()        # :
    SEMICOLON = auto()    # ;
    
    # 其他
    NEWLINE = auto()      # 换行
    INDENT = auto()       # 缩进
    DEDENT = auto()       # 减少缩进
    EOF = auto()          # 文件结束
    
    # 特殊运算符
    AT = auto()           # @
    ARROW = auto()        # ->
    ELLIPSIS = auto()     # ...

class Token:
    """标记类"""
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"Token({self.type}, '{self.value}', line={self.line}, column={self.column})"

class Lexer:
    """词法分析器类"""
    
    # 关键字映射
    KEYWORDS = {
        '定义': TokenType.DEFINE,
        '类': TokenType.CLASS,
        '如果': TokenType.IF,
        '否则': TokenType.ELSE,
        '否则如果': TokenType.ELIF,
        '当': TokenType.WHILE,
        '对于': TokenType.FOR,
        '在': TokenType.IN,
        '返回': TokenType.RETURN,
        '尝试': TokenType.TRY,
        '捕获': TokenType.EXCEPT,
        '最后': TokenType.FINALLY,
        '导入': TokenType.IMPORT,
        '从': TokenType.FROM,
        '真': TokenType.TRUE,
        '假': TokenType.FALSE,
        '空': TokenType.NONE,
        '自身': TokenType.SELF,
        '父类': TokenType.SUPER,
        '非局部': TokenType.NONLOCAL,
        '全局': TokenType.GLOBAL,
        '断言': TokenType.ASSERT,
        '中断': TokenType.BREAK,
        '继续': TokenType.CONTINUE,
        '传递': TokenType.PASS,
        '删除': TokenType.DEL,
        '提升': TokenType.RAISE,
        '使用': TokenType.WITH,
        '作为': TokenType.AS,
        '异步': TokenType.ASYNC,
        '等待': TokenType.AWAIT,
        '且': TokenType.AND,
        '或': TokenType.OR,
        '非': TokenType.NOT,
    }
    
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.text[0] if text else None
        self.indent_stack = [0]  # 缩进栈，初始为0
    
    def error(self, message):
        """抛出词法错误"""
        raise LexerError(message, self.line, self.column)
    
    def advance(self):
        """前进一个字符"""
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
            self.column += 1
    
    def peek(self, n=1):
        """查看前方n个字符，但不前进"""
        peek_pos = self.pos + n
        if peek_pos >= len(self.text):
            return None
        return self.text[peek_pos]
    
    def skip_whitespace(self):
        """跳过空白字符（不包括换行）"""
        while self.current_char is not None and self.current_char.isspace() and self.current_char != '\n':
            self.advance()
    
    def skip_comment(self):
        """跳过注释"""
        while self.current_char is not None and self.current_char != '\n':
            self.advance()
    
    def number(self):
        """处理数字"""
        result = ''
        start_column = self.column
        
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            result += self.current_char
            self.advance()
        
        if '.' in result:
            return Token(TokenType.FLOAT, float(result), self.line, start_column)
        else:
            return Token(TokenType.INTEGER, int(result), self.line, start_column)
    
    def string(self):
        """处理字符串"""
        # 检查是否是格式化字符串
        is_f_string = False
        start_column = self.column
        
        # 检查前一个字符是否是'f'或'F'
        if self.pos > 0 and self.text[self.pos - 1].lower() == 'f':
            is_f_string = True
            # 调整列位置，因为'f'已经被处理过了
            start_column -= 1
        
        quote = self.current_char  # 引号类型（单引号或双引号）
        self.advance()  # 跳过开始的引号
        
        result = ''
        while self.current_char is not None and self.current_char != quote:
            if self.current_char == '\\':  # 处理转义字符
                self.advance()
                if self.current_char == 'n':
                    result += '\n'
                elif self.current_char == 't':
                    result += '\t'
                elif self.current_char == 'r':
                    result += '\r'
                elif self.current_char == '\\':
                    result += '\\'
                elif self.current_char == quote:
                    result += quote
                else:
                    result += '\\' + self.current_char
            else:
                result += self.current_char
            
            self.advance()
        
        if self.current_char is None:
            self.error("未闭合的字符串")
        
        self.advance()  # 跳过结束的引号
        
        # 根据是否是格式化字符串返回不同的标记类型
        if is_f_string:
            return Token(TokenType.F_STRING, result, self.line, start_column)
        else:
            return Token(TokenType.STRING, result, self.line, start_column)
    
    def identifier(self):
        """处理标识符和关键字"""
        result = ''
        start_column = self.column
        
        # 标识符可以包含中文字符、字母、数字和下划线，但不能以数字开头
        while self.current_char is not None and (
            '\u4e00' <= self.current_char <= '\u9fff' or  # 中文字符范围
            self.current_char.isalnum() or 
            self.current_char == '_'
        ):
            result += self.current_char
            self.advance()
        
        # 检查是否是关键字
        token_type = self.KEYWORDS.get(result, TokenType.IDENTIFIER)
        return Token(token_type, result, self.line, start_column)
    
    def handle_indent(self, line):
        """处理缩进"""
        indent_level = len(line) - len(line.lstrip())
        tokens = []
        
        if indent_level > self.indent_stack[-1]:
            # 增加缩进
            self.indent_stack.append(indent_level)
            tokens.append(Token(TokenType.INDENT, indent_level, self.line, 1))
        elif indent_level < self.indent_stack[-1]:
            # 减少缩进
            while indent_level < self.indent_stack[-1]:
                self.indent_stack.pop()
                tokens.append(Token(TokenType.DEDENT, indent_level, self.line, 1))
            
            if indent_level != self.indent_stack[-1]:
                self.error(f"缩进错误：当前缩进级别 {indent_level} 不匹配任何外层缩进")
        
        return tokens
    
    def get_next_token(self):
        """获取下一个标记"""
        while self.current_char is not None:
            
            # 处理空白字符
            if self.current_char.isspace() and self.current_char != '\n':
                self.skip_whitespace()
                continue
            
            # 处理注释
            if self.current_char == '#':
                self.skip_comment()
                continue
            
            # 处理换行
            if self.current_char == '\n':
                self.advance()
                self.line += 1
                self.column = 1
                
                # 跳过空行
                line = ''
                while self.current_char is not None and self.current_char.isspace():
                    if self.current_char == '\n':
                        self.line += 1
                        self.column = 1
                        line = ''
                    else:
                        line += self.current_char
                    self.advance()
                
                # 如果不是空行，处理缩进
                if self.current_char is not None:
                    indent_tokens = self.handle_indent(line)
                    if indent_tokens:
                        return indent_tokens[0]
                
                return Token(TokenType.NEWLINE, '\n', self.line - 1, self.column)
            
            # 处理数字
            if self.current_char.isdigit():
                return self.number()
            
            # 处理格式化字符串和普通字符串
            if self.current_char in ('"', "'") or (
                self.current_char.lower() == 'f' and 
                self.peek() in ('"', "'")
            ):
                # 如果是f-string
                if self.current_char.lower() == 'f':
                    self.advance()  # 跳过'f'字符
                return self.string()
            
            # 处理标识符和关键字
            if self.current_char.isalpha() or self.current_char == '_' or '\u4e00' <= self.current_char <= '\u9fff':
                # 如果是单个'f'后面不跟引号，当作普通标识符处理
                if self.current_char.lower() == 'f' and self.peek() not in ('"', "'"):
                    return self.identifier()
                # 其他情况当作标识符处理
                return self.identifier()
            
            # 处理运算符和分隔符
            if self.current_char == '+':
                start_column = self.column
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.PLUS_ASSIGN, '+=', self.line, start_column)
                return Token(TokenType.PLUS, '+', self.line, start_column)
            
            if self.current_char == '-':
                start_column = self.column
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.MINUS_ASSIGN, '-=', self.line, start_column)
                if self.current_char == '>':
                    self.advance()
                    return Token(TokenType.ARROW, '->', self.line, start_column)
                return Token(TokenType.MINUS, '-', self.line, start_column)
            
            if self.current_char == '*':
                start_column = self.column
                self.advance()
                if self.current_char == '*':
                    self.advance()
                    return Token(TokenType.POWER, '**', self.line, start_column)
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.MULTIPLY_ASSIGN, '*=', self.line, start_column)
                return Token(TokenType.MULTIPLY, '*', self.line, start_column)
            
            if self.current_char == '/':
                start_column = self.column
                self.advance()
                if self.current_char == '/':
                    self.advance()
                    return Token(TokenType.FLOOR_DIVIDE, '//', self.line, start_column)
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.DIVIDE_ASSIGN, '/=', self.line, start_column)
                return Token(TokenType.DIVIDE, '/', self.line, start_column)
            
            if self.current_char == '%':
                start_column = self.column
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.MODULO_ASSIGN, '%=', self.line, start_column)
                return Token(TokenType.MODULO, '%', self.line, start_column)
            
            if self.current_char == '=':
                start_column = self.column
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.EQUAL, '==', self.line, start_column)
                return Token(TokenType.ASSIGN, '=', self.line, start_column)
            
            if self.current_char == '!':
                start_column = self.column
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.NOT_EQUAL, '!=', self.line, start_column)
                self.error("无效的字符: '!'")
            
            if self.current_char == '<':
                start_column = self.column
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.LESS_EQUAL, '<=', self.line, start_column)
                return Token(TokenType.LESS, '<', self.line, start_column)
            
            if self.current_char == '>':
                start_column = self.column
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.GREATER_EQUAL, '>=', self.line, start_column)
                return Token(TokenType.GREATER, '>', self.line, start_column)
            
            if self.current_char == '(':
                start_column = self.column
                self.advance()
                return Token(TokenType.LPAREN, '(', self.line, start_column)
            
            if self.current_char == ')':
                start_column = self.column
                self.advance()
                return Token(TokenType.RPAREN, ')', self.line, start_column)
            
            if self.current_char == '[':
                start_column = self.column
                self.advance()
                return Token(TokenType.LBRACKET, '[', self.line, start_column)
            
            if self.current_char == ']':
                start_column = self.column
                self.advance()
                return Token(TokenType.RBRACKET, ']', self.line, start_column)
            
            if self.current_char == '{':
                start_column = self.column
                self.advance()
                return Token(TokenType.LBRACE, '{', self.line, start_column)
            
            if self.current_char == '}':
                start_column = self.column
                self.advance()
                return Token(TokenType.RBRACE, '}', self.line, start_column)
            
            if self.current_char == ',':
                start_column = self.column
                self.advance()
                return Token(TokenType.COMMA, ',', self.line, start_column)
            
            if self.current_char == '.':
                start_column = self.column
                self.advance()
                if self.current_char == '.' and self.peek() == '.':
                    self.advance()
                    self.advance()
                    return Token(TokenType.ELLIPSIS, '...', self.line, start_column)
                return Token(TokenType.DOT, '.', self.line, start_column)
            
            if self.current_char == ':':
                start_column = self.column
                self.advance()
                return Token(TokenType.COLON, ':', self.line, start_column)
            
            if self.current_char == ';':
                start_column = self.column
                self.advance()
                return Token(TokenType.SEMICOLON, ';', self.line, start_column)
            
            if self.current_char == '@':
                start_column = self.column
                self.advance()
                return Token(TokenType.AT, '@', self.line, start_column)
            
            # 如果到这里还没有返回，说明遇到了无效字符
            self.error(f"无效的字符: '{self.current_char}'")
        
        # 处理文件结束
        if self.pos >= len(self.text):
            # 处理剩余的DEDENT
            if len(self.indent_stack) > 1:
                self.indent_stack.pop()
                return Token(TokenType.DEDENT, 0, self.line, self.column)
            
            return Token(TokenType.EOF, None, self.line, self.column)
    
    def tokenize(self):
        """将整个源代码转换为标记序列"""
        tokens = []
        token = self.get_next_token()
        
        while token.type != TokenType.EOF:
            tokens.append(token)
            token = self.get_next_token()
        
        tokens.append(token)  # 添加EOF标记
        return tokens
            
