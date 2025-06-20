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
    
    def _parse_statement(self):
        """解析语句"""
        if self._match(TokenType.DEFINE):
            return self._parse_function_definition()
        elif self._match(TokenType.CLASS):
            return self._parse_class_definition()
        elif self._match(TokenType.IF):
            return self._parse_if_statement()
        elif self._match(TokenType.WHILE):
            return self._parse_while_statement()
        elif self._match(TokenType.FOR):
            return self._parse_for_statement()
        elif self._match(TokenType.TRY):
            return self._parse_try_statement()
        elif self._match(TokenType.RETURN):
            return self._parse_return_statement()
        elif self._match(TokenType.BREAK):
            return self._parse_break_statement()
        elif self._match(TokenType.CONTINUE):
            return self._parse_continue_statement()
        elif self._match(TokenType.PASS):
            return self._parse_pass_statement()
        elif self._match(TokenType.IMPORT):
            return self._parse_import_statement()
        elif self._match(TokenType.FROM):
            return self._parse_from_import_statement()
        elif self._match(TokenType.RAISE):
            return self._parse_raise_statement()
        elif self._match(TokenType.ASSERT):
            return self._parse_assert_statement()
        elif self._match(TokenType.WITH):
            return self._parse_with_statement()
        elif self._match(TokenType.ASYNC):
            return self._parse_async_statement()
        elif self._match(TokenType.GLOBAL):
            return self._parse_global_statement()
        elif self._match(TokenType.NONLOCAL):
            return self._parse_nonlocal_statement()
        elif self._match(TokenType.DEL):
            return self._parse_delete_statement()
        else:
            return self._parse_expression_statement()
    
    def _parse_block(self):
        """解析代码块"""
        statements = []
        line = self.current_token.line
        column = self.current_token.column
    
        # 检查冒号
        if not self._check(TokenType.COLON):
            # 对于if/else等语句，可能已经消费了冒号
            if not (self._check(TokenType.NEWLINE) or self._check(TokenType.INDENT)):
                self._consume(TokenType.COLON, "代码块需要以冒号开始")
    
        # 处理单行模式
        if not self._check(TokenType.NEWLINE) and not self._check(TokenType.EOF):
            # 单行模式：冒号后直接跟语句
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
            return Block(statements, line, column)
    
        # 多行模式处理
        # 跳过所有换行符
        while self._check(TokenType.NEWLINE):
            self._advance()
        
        # 检查缩进
        if not self._check(TokenType.INDENT):
            # 如果没有缩进，可能是空代码块
            return Block([], line, column)
        else:
            self._advance()  # 消费缩进符
    
        # 解析代码块内的语句
        while not self._check(TokenType.DEDENT) and not self.is_at_end():
            if self._check(TokenType.NEWLINE):
                self._advance()  # 消费换行符
                continue
        
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
    
        # 检查代码块结束
        if not self._check(TokenType.DEDENT):
            self.error("代码块需要减少缩进来结束")
        else:
            self._advance()  # 消费减缩进符
        
        return Block(statements, line, column)
    
    def _parse_function_definition(self):
        """解析函数定义"""
        line = self.previous().line
        column = self.previous().column
        
        # 解析装饰器
        decorators = []
        
        # 解析函数名
        name_token = self._consume(TokenType.IDENTIFIER, "函数定义需要一个名称")
        name = name_token.value
        
        # 解析参数列表
        self._consume(TokenType.LPAREN, "函数定义需要左括号")
        params = []
        
        if not self._check(TokenType.RPAREN):
            while True:
                param_token = self._consume(TokenType.IDENTIFIER, "参数必须是标识符")
                params.append(param_token.value)
                
                if not self._match(TokenType.COMMA):
                    break
        
        self._consume(TokenType.RPAREN, "函数定义需要右括号")
        
        # 解析函数体
        body = self._parse_block()
        
        return FunctionDefinition(name, params, body, decorators, line, column)
    
    def _parse_class_definition(self):
        """解析类定义"""
        line = self.previous().line
        column = self.previous().column
        
        # 解析装饰器
        decorators = []
        
        # 解析类名
        name_token = self._consume(TokenType.IDENTIFIER, "类定义需要一个名称")
        name = name_token.value
        
        # 解析基类
        bases = []
        if self._match(TokenType.LPAREN):
            if not self._check(TokenType.RPAREN):
                while True:
                    base_token = self._consume(TokenType.IDENTIFIER, "基类必须是标识符")
                    base = Identifier(base_token.value, base_token.line, base_token.column)
                    bases.append(base)
                    
                    if not self._match(TokenType.COMMA):
                        break
            
            self._consume(TokenType.RPAREN, "类定义需要右括号")
        
        # 解析类体
        body = self._parse_block()
        
        return ClassDefinition(name, bases, body, decorators, line, column)
    
    def _parse_if_statement(self):
        """解析if语句"""
        line = self.previous().line
        column = self.previous().column
        
        # 解析初始if条件
        condition = self._parse_expression()
        then_block = self._parse_block()
        
        # 收集所有elif分支
        elif_branches = []
        while self._match(TokenType.ELIF):
            elif_condition = self._parse_expression()
            elif_then_block = self._parse_block()
            elif_branches.append((elif_condition, elif_then_block))
        
        # 解析else分支
        else_block = None
        if self._match(TokenType.ELSE):
            else_block = self._parse_block()
        
        # 从最后一个elif开始构建AST
        result = None
        for condition, block in reversed(elif_branches):
            result = If(condition, block, result, condition.line, condition.column)
        
        # 构建完整的if语句
        return If(condition, then_block, result if elif_branches else else_block, line, column)
    
    def _parse_while_statement(self):
        """解析while语句"""
        line = self.previous().line
        column = self.previous().column
        
        condition = self._parse_expression()
        body = self._parse_block()
        
        return While(condition, body, line, column)
    
    def _parse_for_statement(self):
        """解析for语句"""
        line = self.previous().line
        column = self.previous().column
        
        target_token = self._consume(TokenType.IDENTIFIER, "for循环需要一个迭代变量")
        target = Identifier(target_token.value, target_token.line, target_token.column)
        
        self._consume(TokenType.IN, "for循环需要关键字'在'")
        iterable = self._parse_expression()
        body = self._parse_block()
        
        return For(target, iterable, body, line, column)
    
    def _parse_try_statement(self):
        """解析try语句"""
        line = self.previous().line
        column = self.previous().column
        
        try_block = self._parse_block()
        
        except_blocks = []
        while self._match(TokenType.EXCEPT):
            except_line = self.previous().line
            except_column = self.previous().column
            
            exception_type = None
            if self._check(TokenType.IDENTIFIER):
                exception_type_token = self._advance()
                exception_type = Identifier(
                    exception_type_token.value,
                    exception_type_token.line,
                    exception_type_token.column
                )
            
            exception_name = None
            if self._match(TokenType.AS):
                exception_name_token = self._consume(TokenType.IDENTIFIER, "except as 后需要一个标识符")
                exception_name = exception_name_token.value
            
            except_block = self._parse_block()
            except_blocks.append((exception_type, exception_name, except_block))
        
        finally_block = None
        if self._match(TokenType.FINALLY):
            finally_block = self._parse_block()
        
        return Try(try_block, except_blocks, finally_block, line, column)
    
    def _parse_return_statement(self):
        """解析return语句"""
        line = self.previous().line
        column = self.previous().column
        
        value = None
        if not self._check(TokenType.NEWLINE):
            value = self._parse_expression()
        
        self._match(TokenType.NEWLINE)  # 可选的换行
        
        return Return(value, line, column)
    
    def _parse_break_statement(self):
        """解析break语句"""
        line = self.previous().line
        column = self.previous().column
        
        self._match(TokenType.NEWLINE)  # 可选的换行
        
        return Break(line, column)
    
    def _parse_continue_statement(self):
        """解析continue语句"""
        line = self.previous().line
        column = self.previous().column
        
        self._match(TokenType.NEWLINE)  # 可选的换行
        
        return Continue(line, column)
    
    def _parse_pass_statement(self):
        """解析pass语句"""
        line = self.previous().line
        column = self.previous().column
        
        self._match(TokenType.NEWLINE)  # 可选的换行
        
        return Pass(line, column)
    
    def _parse_import_statement(self):
        """解析import语句"""
        line = self.previous().line
        column = self.previous().column
        
        module_token = self._consume(TokenType.IDENTIFIER, "import语句需要一个模块名")
        module = module_token.value
        
        alias = None
        if self._match(TokenType.AS):
            alias_token = self._consume(TokenType.IDENTIFIER, "as后需要一个标识符")
            alias = alias_token.value
        
        self._match(TokenType.NEWLINE)  # 可选的换行
        
        return Import(module, alias, line, column)
    
    def _parse_from_import_statement(self):
        """解析from import语句"""
        line = self.previous().line
        column = self.previous().column
        
        module_token = self._consume(TokenType.IDENTIFIER, "from语句需要一个模块名")
        module = module_token.value
        
        self._consume(TokenType.IMPORT, "from语句需要关键字'导入'")
        
        names = []
        if self._match(TokenType.MULTIPLY):
            # from module import *
            names.append(("*", None))
        else:
            # from module import name1 [as alias1], name2 [as alias2], ...
            while True:
                name_token = self._consume(TokenType.IDENTIFIER, "import语句需要至少一个名称")
                name = name_token.value
                
                alias = None
                if self._match(TokenType.AS):
                    alias_token = self._consume(TokenType.IDENTIFIER, "as后需要一个标识符")
                    alias = alias_token.value
                
                names.append((name, alias))
                
                # 如果有逗号，继续解析下一个导入名称
                if not self._match(TokenType.COMMA):
                    break
        
        self._match(TokenType.NEWLINE)  # 可选的换行
        
        return FromImport(module, names, line, column)
    
    def _parse_raise_statement(self):
        """解析raise语句"""
        line = self.previous().line
        column = self.previous().column
        
        exception = None
        if not self._check(TokenType.NEWLINE):
            exception = self._parse_expression()
            
            # 处理 raise exception from cause
            if self._match(TokenType.FROM):
                cause = self._parse_expression()
                # 在这里，我们将 from cause 作为异常的一部分处理
                # 可以创建一个BinaryOperation节点，表示 exception from cause
                exception = BinaryOperation(exception, "from", cause, exception.line, exception.column)
        
        self._match(TokenType.NEWLINE)  # 可选的换行
        
        return Raise(exception, line, column)
    
    def _parse_assert_statement(self):
        """解析assert语句"""
        line = self.previous().line
        column = self.previous().column
        
        condition = self._parse_expression()
        
        message = None
        if self._match(TokenType.COMMA):
            message = self._parse_expression()
        
        self._match(TokenType.NEWLINE)  # 可选的换行
        
        return Assert(condition, message, line, column)
    
    def _parse_with_statement(self):
        """解析with语句"""
        line = self.previous().line
        column = self.previous().column
        
        context_expr = self._parse_expression()
        
        optional_vars = None
        if self._match(TokenType.AS):
            var_token = self._consume(TokenType.IDENTIFIER, "as后需要一个标识符")
            optional_vars = Identifier(var_token.value, var_token.line, var_token.column)
        
        # 处理多个上下文管理器
        items = [(context_expr, optional_vars)]
        while self._match(TokenType.COMMA):
            context_expr = self._parse_expression()
            optional_vars = None
            if self._match(TokenType.AS):
                var_token = self._consume(TokenType.IDENTIFIER, "as后需要一个标识符")
                optional_vars = Identifier(var_token.value, var_token.line, var_token.column)
            items.append((context_expr, optional_vars))
        
        body = self._parse_block()
        
        # 如果有多个上下文管理器，我们需要创建嵌套的With节点
        if len(items) == 1:
            return With(items[0][0], items[0][1], body, line, column)
        else:
            # 从最后一个上下文管理器开始，创建嵌套的With节点
            result = With(items[-1][0], items[-1][1], body, items[-1][0].line, items[-1][0].column)
            for i in range(len(items) - 2, -1, -1):
                context_expr, optional_vars = items[i]
                result = With(context_expr, optional_vars, Block([result], result.line, result.column), context_expr.line, context_expr.column)
            return result
    
    def _parse_async_statement(self):
        """解析async语句"""
        line = self.previous().line
        column = self.previous().column
        
        # 目前只支持async def和async with
        if self._match(TokenType.DEFINE):
            function = self._parse_function_definition()
            return Async(function, line, column)
        elif self._match(TokenType.WITH):
            with_stmt = self._parse_with_statement()
            return Async(with_stmt, line, column)
        else:
            self.error("async后只能跟def或with")
    
    def _parse_global_statement(self):
        """解析global语句"""
        line = self.previous().line
        column = self.previous().column
        
        names = []
        while True:
            name_token = self._consume(TokenType.IDENTIFIER, "global语句需要至少一个标识符")
            names.append(name_token.value)
            
            if not self._match(TokenType.COMMA):
                break
        
        self._match(TokenType.NEWLINE)  # 可选的换行
        
        return Global(names, line, column)
    
    def _parse_nonlocal_statement(self):
        """解析nonlocal语句"""
        line = self.previous().line
        column = self.previous().column
        
        names = []
        while True:
            name_token = self._consume(TokenType.IDENTIFIER, "nonlocal语句需要至少一个标识符")
            names.append(name_token.value)
            
            if not self._match(TokenType.COMMA):
                break
        
        self._match(TokenType.NEWLINE)  # 可选的换行
        
        return Nonlocal(names, line, column)
    
    def _parse_delete_statement(self):
        """解析del语句"""
        line = self.previous().line
        column = self.previous().column
        
        targets = []
        while True:
            target = self._parse_expression()
            targets.append(target)
            
            if not self._match(TokenType.COMMA):
                break
        
        self._match(TokenType.NEWLINE)  # 可选的换行
        
        return Delete(targets, line, column)
    
    def _parse_expression_statement(self):
        """解析表达式语句"""
        line = self.current_token.line
        column = self.current_token.column
        
        expr = self._parse_expression()
        
        self._match(TokenType.NEWLINE)  # 可选的换行
        
        return ExpressionStatement(expr, line, column)
    
    def _parse_expression(self):
        """解析表达式"""
        return self._parse_assignment()
    
    def _parse_assignment(self):
        """解析赋值表达式"""
        expr = self._parse_or()
        
        if self._match(TokenType.ASSIGN):
            line = self.previous().line
            column = self.previous().column
            value = self._parse_assignment()  # 右结合
            
            if isinstance(expr, Identifier):
                # 创建变量声明而不是赋值
                return VariableDeclaration(expr.name, value, line, column)
            elif isinstance(expr, GetAttribute):
                return SetAttribute(expr.object, expr.name, value, line, column)
            elif isinstance(expr, GetItem):
                return SetItem(expr.object, expr.key, value, line, column)
            else:
                self.error("无效的赋值目标")
        
        return expr
    
    def _parse_or(self):
        """解析逻辑或表达式"""
        expr = self._parse_and()
        
        while self._match(TokenType.OR):
            operator = "or"  # 使用统一的操作符字符串
            line = self.previous().line
            column = self.previous().column
            right = self._parse_and()
            expr = LogicalOperation(expr, operator, right, line, column)
        
        return expr
    
    def _parse_and(self):
        """解析逻辑与表达式"""
        expr = self._parse_comparison()
        
        while self._match(TokenType.AND):
            operator = "and"  # 使用统一的操作符字符串
            line = self.previous().line
            column = self.previous().column
            right = self._parse_comparison()
            expr = LogicalOperation(expr, operator, right, line, column)
        
        return expr
    
    def _parse_comparison(self):
        """解析比较表达式"""
        expr = self._parse_term()
        
        # 中文比较运算符到符号的映射
        operator_map = {
            "大于": ">",
            "小于": "<",
            "等于": "==",
            "不等于": "!=",
            "大于等于": ">=",
            "小于等于": "<=",
            "在": "in"
        }
        
        while self._match(TokenType.EQUAL, TokenType.NOT_EQUAL,
                         TokenType.LESS, TokenType.LESS_EQUAL,
                         TokenType.GREATER, TokenType.GREATER_EQUAL,
                         TokenType.IN):
            token_value = self.previous().value
            # 如果是中文比较运算符，转换为对应的符号
            operator = operator_map.get(token_value, token_value)
            line = self.previous().line
            column = self.previous().column
            right = self._parse_term()
            expr = BinaryOperation(expr, operator, right, line, column)
        
        return expr
    
    def _parse_term(self):
        """解析加减法表达式"""
        expr = self._parse_factor()
        
        while self._match(TokenType.PLUS, TokenType.MINUS, TokenType.PLUS_CN, TokenType.MINUS_CN):
            operator = self.previous().value
            line = self.previous().line
            column = self.previous().column
            right = self._parse_factor()
            expr = BinaryOperation(expr, operator, right, line, column)
        
        return expr
    
    def _parse_factor(self):
        """解析乘除法表达式"""
        expr = self._parse_unary()
        
        while self._match(TokenType.MULTIPLY, TokenType.DIVIDE,
                         TokenType.MODULO, TokenType.POWER,
                         TokenType.MULTIPLY_CN, TokenType.DIVIDE_CN,
                         TokenType.MODULO_CN, TokenType.POWER_CN,
                         TokenType.FLOOR_DIVIDE, TokenType.FLOOR_DIVIDE_CN):
            operator = self.previous().value
            line = self.previous().line
            column = self.previous().column
            right = self._parse_unary()
            expr = BinaryOperation(expr, operator, right, line, column)
        
        return expr
    
    def _parse_unary(self):
        """解析一元表达式"""
        if self._match(TokenType.NOT, TokenType.MINUS):
            operator = self.previous().value
            line = self.previous().line
            column = self.previous().column
            # 对于NOT运算符，我们需要确保它应用于整个比较表达式
            if operator == "非":
                right = self._parse_comparison()
            else:
                right = self._parse_unary()
            return UnaryOperation(operator, right, line, column)
        
        return self._parse_primary()
    
    def _parse_primary(self):
        """解析基本表达式"""
        if self._match(TokenType.FALSE):
            return BooleanLiteral(False, self.previous().line, self.previous().column)
        elif self._match(TokenType.TRUE):
            return BooleanLiteral(True, self.previous().line, self.previous().column)
        elif self._match(TokenType.NONE):
            return NoneLiteral(self.previous().line, self.previous().column)
        elif self._match(TokenType.INTEGER):
            return IntegerLiteral(self.previous().value, self.previous().line, self.previous().column)
        elif self._match(TokenType.FLOAT):
            return FloatLiteral(self.previous().value, self.previous().line, self.previous().column)
        elif self._match(TokenType.STRING, TokenType.F_STRING):
            return StringLiteral(self.previous().value, self.previous().line, self.previous().column)
        elif self._match(TokenType.IDENTIFIER):
            identifier = Identifier(self.previous().value, self.previous().line, self.previous().column)
            return self._parse_call_or_access(identifier)
        elif self._match(TokenType.LPAREN):
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN, "期望右括号')'")
            return self._parse_call_or_access(expr)
        elif self._match(TokenType.LBRACKET):
            # 列表字面量
            elements = []
            if not self._check(TokenType.RBRACKET):
                while True:
                    elements.append(self._parse_expression())
                    if not self._match(TokenType.COMMA):
                        break
            self._consume(TokenType.RBRACKET, "期望右方括号']'")
            list_expr = List(elements, self.previous().line, self.previous().column)
            return self._parse_call_or_access(list_expr)
        elif self._match(TokenType.LBRACE):
            # 字典字面量
            pairs = []
            if not self._check(TokenType.RBRACE):
                while True:
                    key = self._parse_expression()
                    self._consume(TokenType.COLON, "期望冒号':'")
                    value = self._parse_expression()
                    pairs.append((key, value))
                    if not self._match(TokenType.COMMA):
                        break
            self._consume(TokenType.RBRACE, "期望右花括号'}'")
            dict_expr = Dict(pairs, self.previous().line, self.previous().column)
            return self._parse_call_or_access(dict_expr)
        
        self.error("期望表达式")
    
    def _parse_call_or_access(self, expr):
        """解析函数调用、属性访问或索引访问"""
        while True:
            if self._match(TokenType.LPAREN):
                # 函数调用
                args = []
                if not self._check(TokenType.RPAREN):
                    while True:
                        args.append(self._parse_expression())
                        if not self._match(TokenType.COMMA):
                            break
                self._consume(TokenType.RPAREN, "期望右括号')'")
                expr = FunctionCall(expr, args, {}, self.previous().line, self.previous().column)
            elif self._match(TokenType.DOT):
                # 属性访问
                name_token = self._consume(TokenType.IDENTIFIER, "期望属性名")
                expr = GetAttribute(expr, name_token.value, name_token.line, name_token.column)
            elif self._match(TokenType.LBRACKET):
                # 索引访问
                key = self._parse_expression()
                self._consume(TokenType.RBRACKET, "期望右方括号']'")
                expr = GetItem(expr, key, self.previous().line, self.previous().column)
            else:
                break
        
        return expr
