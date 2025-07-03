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
    F_STRING = auto()         # 格式化字符串
    F_STRING_START = auto()   # 格式化字符串开始
    F_STRING_EXPR = auto()    # 格式化字符串中的表达式
    
    # 运算符
    PLUS = auto()         # +
    MINUS = auto()        # -
    MULTIPLY = auto()     # *
    DIVIDE = auto()       # /
    MODULO = auto()       # %
    POWER = auto()        # **
    FLOOR_DIVIDE = auto() # //
    
    # 中文运算符
    PLUS_CN = auto()      # 加
    MINUS_CN = auto()     # 减
    MULTIPLY_CN = auto()  # 乘
    DIVIDE_CN = auto()    # 除
    MODULO_CN = auto()    # 余
    POWER_CN = auto()     # 幂
    FLOOR_DIVIDE_CN = auto() # 整除
    
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
    def __init__(self, type, value, line=None, column=None):
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
        
        # 中文算术运算符
        '加': TokenType.PLUS_CN,
        '减': TokenType.MINUS_CN,
        '乘': TokenType.MULTIPLY_CN,
        '除': TokenType.DIVIDE_CN,
        '余': TokenType.MODULO_CN,
        '幂': TokenType.POWER_CN,
        '整除': TokenType.FLOOR_DIVIDE_CN,
        
        # 中文比较运算符
        '大于': TokenType.GREATER_CN,
        '小于': TokenType.LESS_CN,
        '等于': TokenType.EQUAL_CN,
        '不等于': TokenType.NOT_EQUAL_CN,
        '大于等于': TokenType.GREATER_EQUAL_CN,
        '小于等于': TokenType.LESS_EQUAL_CN,
    }
    
    def __init__(self, text, filename="<stdin>"):
        self.text = text
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.text[0] if text else None
        self.indent_stack = [0]  # 缩进栈，初始为0
    
    def error(self, message, error_code="LEX001"):
        """抛出词法错误
        
        Args:
            message (str): 错误描述
            error_code (str): 错误代码
        """
        context = self._get_error_context()
        raise LexerError(
            message=message,
            line=self.line,
            column=self.column,
            error_code=error_code,
            context=context
        )
    
    def _get_error_context(self):
        """获取错误位置附近的代码上下文"""
        if not hasattr(self, 'text') or not self.text:
            return None
        
        start = max(0, self.pos - 20)
        end = min(len(self.text), self.pos + 20)
        context = self.text[start:end]
        
        # 标记错误位置
        marker = ' ' * (self.pos - start) + '^'
        return f"{context}\n{marker}"
    
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
        dot_count = 0
        
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                dot_count += 1
                if dot_count > 1:
                    self.error("无效的数字格式: 多个小数点", "LEX003")
            result += self.current_char
            self.advance()
        
        # 检查数字是否以小数点结尾
        if result.endswith('.'):
            self.error("无效的数字格式: 小数点后缺少数字", "LEX003")
        
        try:
            if '.' in result:
                return Token(TokenType.FLOAT, float(result), self.line, start_column)
            else:
                return Token(TokenType.INTEGER, int(result), self.line, start_column)
        except ValueError:
            self.error("无效的数字格式", "LEX003")
    
    def string(self):
        """处理字符串和f-string"""
        is_f_string = False
        start_column = self.column
        
        # 检查是否是f-string
        if self.pos > 0 and self.text[self.pos - 1].lower() == 'f':
            is_f_string = True
            start_column -= 1
        
        quote = self.current_char
        self.advance()  # 跳过引号
        
        if is_f_string:
            return self.process_f_string(quote, start_column)
        else:
            return self.process_normal_string(quote, start_column)
    
    def process_normal_string(self, quote, start_column):
        """处理普通字符串"""
        result = []
        while self.current_char is not None and self.current_char != quote:
            if self.current_char == '\\':
                self.advance()
                if self.current_char == 'n':
                    result.append('\n')
                elif self.current_char == 't':
                    result.append('\t')
                elif self.current_char == 'r':
                    result.append('\r')
                elif self.current_char == '\\':
                    result.append('\\')
                elif self.current_char == quote:
                    result.append(quote)
                elif self.current_char == 'u':  # Unicode转义
                    self.advance()
                    hex_str = self.text[self.pos:self.pos+4]
                    if len(hex_str) != 4 or not all(c in '0123456789abcdefABCDEF' for c in hex_str):
                        self.error("无效的Unicode转义序列", "LEX008")
                    result.append(chr(int(hex_str, 16)))
                    self.advance(3)  # 已经前进1个字符，再前进3个
                else:
                    result.append('\\' + self.current_char)
            else:
                result.append(self.current_char)
            self.advance()
        
        if self.current_char is None:
            self.error("未闭合的字符串", "LEX002")
        
        self.advance()  # 跳过结束引号
        return Token(TokenType.STRING, ''.join(result), self.line, start_column)
    
    def process_f_string(self, quote, start_column):
        """处理f-string"""
        parts = []
        current_part = []
        brace_level = 0
        
        while self.current_char is not None and self.current_char != quote:
            if self.current_char == '{':
                if self.peek() == '{':  # 转义{
                    current_part.append('{')
                    self.advance(2)
                    continue
                
                if brace_level == 0 and current_part:
                    parts.append(('text', ''.join(current_part)))
                    current_part = []
                
                brace_level += 1
                self.advance()
                
                if brace_level == 1:
                    # 开始处理表达式
                    expr_start = self.pos
                    while self.current_char is not None and (brace_level > 0 or self.current_char != '}'):
                        if self.current_char == '{':
                            brace_level += 1
                        elif self.current_char == '}':
                            brace_level -= 1
                        self.advance()
                    
                    if brace_level > 0:
                        self.error("未闭合的f-string表达式", "LEX006")
                    
                    expr = self.text[expr_start:self.pos-1].strip()
                    if expr:
                        parts.append(('expr', expr))
                    continue
            
            elif self.current_char == '}':
                if self.peek() == '}':  # 转义}
                    current_part.append('}')
                    self.advance(2)
                    continue
                
                self.error("未匹配的'}'")
            
            elif self.current_char == '\\':
                self.advance()
                if self.current_char == 'n':
                    current_part.append('\n')
                elif self.current_char == 't':
                    current_part.append('\t')
                elif self.current_char == 'r':
                    current_part.append('\r')
                elif self.current_char == '\\':
                    current_part.append('\\')
                elif self.current_char == quote:
                    current_part.append(quote)
                else:
                    current_part.append('\\' + self.current_char)
                self.advance()
                continue
            
            current_part.append(self.current_char)
            self.advance()
        
        if self.current_char is None:
            self.error("未闭合的f-string")
        
        if current_part:
            parts.append(('text', ''.join(current_part)))
        
        self.advance()  # 跳过结束引号
        
        # 生成f-string标记
        return Token(TokenType.F_STRING, parts, self.line, start_column)
    
    def identifier(self):
        """处理标识符和关键字"""
        result = ''
        start_column = self.column
        
        # 检查首字符是否有效
        if self.current_char is not None and not (
            '\u4e00' <= self.current_char <= '\u9fff' or  # 中文字符
            self.current_char.isalpha() or 
            self.current_char == '_'
        ):
            self.error("无效的标识符: 必须以中文、字母或下划线开头", "LEX004")
        
        # 标识符可以包含中文字符、字母、数字和下划线
        while self.current_char is not None and (
            '\u4e00' <= self.current_char <= '\u9fff' or  # 中文字符范围
            self.current_char.isalnum() or 
            self.current_char == '_'
        ):
            result += self.current_char
            self.advance()
        
        # 检查标识符长度
        if len(result) > 255:
            self.error("无效的标识符: 长度超过255个字符", "LEX004")
        
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
                # 检查缩进是否一致
                if self.current_char == ' ':
                    spaces = 0
                    while self.current_char == ' ':
                        spaces += 1
                        self.advance()
                    if spaces % 4 != 0:
                        self.error("缩进错误: 必须使用4个空格的倍数", "LEX007")
                return Token(TokenType.NEWLINE, '\n', self.line - 1, self.column)
            
            # 处理标识符和关键字
            if self.current_char.isalpha() or self.current_char == '_' or '\u4e00' <= self.current_char <= '\u9fff':
                return self.identifier()
            
            # 处理数字
            if self.current_char.isdigit():
                return self.number()
            
            # 处理字符串
            if self.current_char in ('"', "'"):
                return self.string()
            
            # 处理格式化字符串
            if self.current_char.lower() == 'f' and self.peek() in ('"', "'"):
                self.advance()  # 跳过'f'
                return self.string()
            
            # 处理运算符和分隔符
            if self.current_char == '+':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.PLUS_ASSIGN, '+=', self.line, self.column - 2)
                return Token(TokenType.PLUS, '+', self.line, self.column - 1)
            
            if self.current_char == '-':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.MINUS_ASSIGN, '-=', self.line, self.column - 2)
                elif self.current_char == '>':
                    self.advance()
                    return Token(TokenType.ARROW, '->', self.line, self.column - 2)
                return Token(TokenType.MINUS, '-', self.line, self.column - 1)
            
            if self.current_char == '*':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.MULTIPLY_ASSIGN, '*=', self.line, self.column - 2)
                elif self.current_char == '*':
                    self.advance()
                    return Token(TokenType.POWER, '**', self.line, self.column - 2)
                return Token(TokenType.MULTIPLY, '*', self.line, self.column - 1)
            
            if self.current_char == '/':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.DIVIDE_ASSIGN, '/=', self.line, self.column - 2)
                elif self.current_char == '/':
                    self.advance()
                    return Token(TokenType.FLOOR_DIVIDE, '//', self.line, self.column - 2)
                return Token(TokenType.DIVIDE, '/', self.line, self.column - 1)
            
            if self.current_char == '%':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.MODULO_ASSIGN, '%=', self.line, self.column - 2)
                return Token(TokenType.MODULO, '%', self.line, self.column - 1)
            
            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.EQUAL, '==', self.line, self.column - 2)
                return Token(TokenType.ASSIGN, '=', self.line, self.column - 1)
            
            if self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.NOT_EQUAL, '!=', self.line, self.column - 2)
                self.error("无效的运算符: '!'", "LEX005")
            
            if self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.LESS_EQUAL, '<=', self.line, self.column - 2)
                return Token(TokenType.LESS, '<', self.line, self.column - 1)
            
            if self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.GREATER_EQUAL, '>=', self.line, self.column - 2)
                return Token(TokenType.GREATER, '>', self.line, self.column - 1)
            
            # 处理分隔符
            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(', self.line, self.column - 1)
            
            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN, ')', self.line, self.column - 1)
            
            if self.current_char == '[':
                self.advance()
                return Token(TokenType.LBRACKET, '[', self.line, self.column - 1)
            
            if self.current_char == ']':
                self.advance()
                return Token(TokenType.RBRACKET, ']', self.line, self.column - 1)
            
            if self.current_char == '{':
                self.advance()
                return Token(TokenType.LBRACE, '{', self.line, self.column - 1)
            
            if self.current_char == '}':
                self.advance()
                return Token(TokenType.RBRACE, '}', self.line, self.column - 1)
            
            if self.current_char == ',':
                self.advance()
                return Token(TokenType.COMMA, ',', self.line, self.column - 1)
            
            if self.current_char == '.':
                self.advance()
                if self.current_char == '.' and self.peek() == '.':
                    self.advance()
                    self.advance()
                    return Token(TokenType.ELLIPSIS, '...', self.line, self.column - 3)
                return Token(TokenType.DOT, '.', self.line, self.column - 1)
            
            if self.current_char == ':':
                self.advance()
                return Token(TokenType.COLON, ':', self.line, self.column - 1)
            
            if self.current_char == ';':
                self.advance()
                return Token(TokenType.SEMICOLON, ';', self.line, self.column - 1)
            
            if self.current_char == '@':
                self.advance()
                return Token(TokenType.AT, '@', self.line, self.column - 1)
            
            # 如果到达这里，说明遇到了无法识别的字符
            self.error(f"无法识别的字符: '{self.current_char}'")
        
        # 如果到达文件末尾，返回EOF标记
        return Token(TokenType.EOF, '', self.line, self.column)
    
    def tokenize(self):
        """将整个源代码转换为标记序列"""
        tokens = []
        
        # 处理源代码中的每一行
        lines = self.text.splitlines()
        if not lines:
            return [Token(TokenType.EOF, '', 1, 1)]
        
        for i, line in enumerate(lines):
            self.line = i + 1
            self.column = 1
            
            # 跳过空行
            if not line.strip():
                tokens.append(Token(TokenType.NEWLINE, '\n', self.line, self.column))
                continue
            
            # 处理缩进
            indent_tokens = self.handle_indent(line)
            tokens.extend(indent_tokens)
            
            # 设置当前行的起始位置
            self.pos = sum(len(l) + 1 for l in lines[:i])  # +1 是为了换行符
            if self.pos < len(self.text):
                self.current_char = self.text[self.pos]
            else:
                self.current_char = None
            
            # 跳过行首空白
            self.column = 1
            while self.current_char is not None and self.current_char.isspace() and self.current_char != '\n':
                self.advance()
            
            # 处理行内标记
            while self.current_char is not None and self.current_char != '\n':
                token = self.get_next_token()
                if token.type != TokenType.NEWLINE:  # 避免重复添加换行标记
                    tokens.append(token)
            
            # 添加换行标记
            tokens.append(Token(TokenType.NEWLINE, '\n', self.line, self.column))
        
        # 处理文件末尾的缩进
        while self.indent_stack[-1] > 0:
            self.indent_stack.pop()
            tokens.append(Token(TokenType.DEDENT, 0, self.line, self.column))
        
        # 添加EOF标记
        tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        
        return tokens
