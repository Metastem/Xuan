"""
玄语言语法分析器

这个模块实现了玄语言的语法分析器，负责将标记序列转换为抽象语法树。
使用递归下降解析方法实现。
"""

from .lexer import TokenType
from .ast import *
from .exceptions import ParserError, SyntaxError

class Parser:
    """语法分析器类"""
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.current_token = self.tokens[0] if self.tokens else None
    
    def error(self, message):
        """抛出语法错误"""
        raise SyntaxError(
            message,
            self.current_token.line if self.current_token else 0,
            self.current_token.column if self.current_token else 0
        )
    
    def _advance(self):
        """前进一个标记"""
        self.current += 1
        if self.current < len(self.tokens):
            self.current_token = self.tokens[self.current]
        return self.previous()
    
    def _check(self, token_type):
        """检查当前标记是否为指定类型"""
        if self.is_at_end():
            return False
        return self.current_token.type == token_type
    
    def _match(self, *token_types):
        """检查当前标记是否匹配指定的类型之一，如果匹配则前进"""
        for token_type in token_types:
            if self._check(token_type):
                self._advance()
                return True
        return False
    
    def _consume(self, token_type, message):
        """消费一个指定类型的标记，如果不匹配则抛出错误"""
        if self._check(token_type):
            return self._advance()
        self.error(message)
    
    def is_at_end(self):
        """检查是否到达标记序列末尾"""
        return self.current_token.type == TokenType.EOF
    
    def previous(self):
        """获取前一个标记"""
        return self.tokens[self.current - 1]
    
    def peek(self):
        """查看当前标记但不前进"""
        return self.current_token
    
    def peek_next(self):
        """查看下一个标记但不前进"""
        if self.current + 1 >= len(self.tokens):
            return None
        return self.tokens[self.current + 1]
    
    def parse(self):
        """解析程序"""
        statements = []
        
        while not self.is_at_end():
            if self._match(TokenType.NEWLINE):
                continue
            
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        
        return Program(statements)
    
    def _parse_expression(self):
        """解析表达式"""
        return self._parse_assignment()
    
    def _parse_assignment(self):
        """解析赋值表达式"""
        expr = self._parse_or()
        
        if self._match(TokenType.ASSIGN):
            line = self.previous().line
            column = self.previous().column
            value = self._parse_assignment()
            
            if isinstance(expr, Identifier):
                return Assignment(expr.name, value, line, column)
            elif isinstance(expr, GetAttribute):
                return SetAttribute(expr.object, expr.name, value, line, column)
            elif isinstance(expr, GetItem):
                return SetItem(expr.object, expr.key, value, line, column)
            
            self.error("无效的赋值目标")
        
        return expr
    
    def _parse_or(self):
        """解析逻辑或表达式"""
        expr = self._parse_and()
        
        while self._match(TokenType.OR):
            line = self.previous().line
            column = self.previous().column
            right = self._parse_and()
            expr = LogicalOr(expr, right, line, column)
        
        return expr
    
    def _parse_and(self):
        """解析逻辑与表达式"""
        expr = self._parse_equality()
        
        while self._match(TokenType.AND):
            line = self.previous().line
            column = self.previous().column
            right = self._parse_equality()
            expr = LogicalAnd(expr, right, line, column)
        
        return expr
    
    def _parse_equality(self):
        """解析相等性表达式"""
        expr = self._parse_comparison()
        
        while self._match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            operator = self.previous().type
            line = self.previous().line
            column = self.previous().column
            right = self._parse_comparison()
            expr = BinaryOp(expr, operator, right, line, column)
        
        return expr
    
    def _parse_comparison(self):
        """解析比较表达式"""
        expr = self._parse_term()
        
        while self._match(
            TokenType.LESS, TokenType.LESS_EQUAL,
            TokenType.GREATER, TokenType.GREATER_EQUAL,
            TokenType.IN, TokenType.NOT_IN,
            TokenType.IS, TokenType.IS_NOT
        ):
            operator = self.previous().type
            line = self.previous().line
            column = self.previous().column
            right = self._parse_term()
            expr = BinaryOp(expr, operator, right, line, column)
        
        return expr
    
    def _parse_term(self):
        """解析加减表达式"""
        expr = self._parse_factor()
        
        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous().type
            line = self.previous().line
            column = self.previous().column
            right = self._parse_factor()
            expr = BinaryOp(expr, operator, right, line, column)
        
        return expr
    
    def _parse_factor(self):
        """解析乘除表达式"""
        expr = self._parse_unary()
        
        while self._match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            operator = self.previous().type
            line = self.previous().line
            column = self.previous().column
            right = self._parse_unary()
            expr = BinaryOp(expr, operator, right, line, column)
        
        return expr
    
    def _parse_unary(self):
        """解析一元表达式"""
        if self._match(TokenType.NOT, TokenType.MINUS):
            operator = self.previous().type
            line = self.previous().line
            column = self.previous().column
            right = self._parse_unary()
            return UnaryOp(operator, right, line, column)
        
        return self._parse_call()
    
    def _parse_call(self):
        """解析函数调用"""
        expr = self._parse_primary()
        
        while True:
            if self._match(TokenType.LPAREN):
                expr = self._finish_call(expr)
            elif self._match(TokenType.DOT):
                name_token = self._consume(TokenType.IDENTIFIER, "属性访问需要一个名称")
                expr = GetAttribute(expr, name_token.value, name_token.line, name_token.column)
            elif self._match(TokenType.LBRACKET):
                key = self._parse_expression()
                self._consume(TokenType.RBRACKET, "索引访问需要右方括号")
                expr = GetItem(expr, key, self.previous().line, self.previous().column)
            else:
                break
        
        return expr
    
    def _finish_call(self, callee):
        """完成函数调用的解析"""
        args = []
        
        if not self._check(TokenType.RPAREN):
            while True:
                args.append(self._parse_expression())
                
                if not self._match(TokenType.COMMA):
                    break
        
        self._consume(TokenType.RPAREN, "函数调用需要右括号")
        
        return Call(callee, args, self.previous().line, self.previous().column)
    
    def _parse_primary(self):
        """解析基本表达式"""
        if self._match(TokenType.FALSE):
            return Literal(False, self.previous().line, self.previous().column)
        elif self._match(TokenType.TRUE):
            return Literal(True, self.previous().line, self.previous().column)
        elif self._match(TokenType.NONE):
            return Literal(None, self.previous().line, self.previous().column)
        elif self._match(TokenType.NUMBER):
            return Literal(float(self.previous().value), self.previous().line, self.previous().column)
        elif self._match(TokenType.STRING):
            return Literal(self.previous().value, self.previous().line, self.previous().column)
        elif self._match(TokenType.IDENTIFIER):
            return Identifier(self.previous().value, self.previous().line, self.previous().column)
        elif self._match(TokenType.LPAREN):
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN, "表达式需要右括号")
            return expr
        elif self._match(TokenType.LBRACKET):
            return self._parse_list()
        elif self._match(TokenType.LBRACE):
            return self._parse_dict()
        
        self.error("期望一个表达式")
    
    def _parse_list(self):
        """解析列表字面量"""
        line = self.previous().line
        column = self.previous().column
        items = []
        
        if not self._check(TokenType.RBRACKET):
            while True:
                items.append(self._parse_expression())
                
                if not self._match(TokenType.COMMA):
                    break
        
        self._consume(TokenType.RBRACKET, "列表字面量需要右方括号")
        
        return List(items, line, column)
    
    def _parse_dict(self):
        """解析字典字面量"""
        line = self.previous().line
        column = self.previous().column
        items = []
        
        if not self._check(TokenType.RBRACE):
            while True:
                key = self._parse_expression()
                self._consume(TokenType.COLON, "字典键值对需要冒号")
                value = self._parse_expression()
                items.append((key, value))
                
                if not self._match(TokenType.COMMA):
                    break
        
        self._consume(TokenType.RBRACE, "字典字面量需要右花括号")
        
        return Dict(items, line, column)
