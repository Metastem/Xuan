"""
玄语言抽象语法树(AST)模块

这个模块定义了玄语言的抽象语法树节点类型。
"""

class ASTNode:
    """AST节点基类"""
    def __init__(self, line, column):
        self.line = line
        self.column = column
    
    def accept(self, visitor):
        """接受访问者"""
        method_name = f"visit_{type(self).__name__}"
        method = getattr(visitor, method_name, visitor.visit_default)
        return method(self)

class Program(ASTNode):
    """程序节点，表示整个程序"""
    def __init__(self, statements, line=0, column=0):
        super().__init__(line, column)
        self.statements = statements  # 语句列表

class Block(ASTNode):
    """代码块节点，表示一组语句"""
    def __init__(self, statements, line, column):
        super().__init__(line, column)
        self.statements = statements  # 语句列表

class Literal(ASTNode):
    """字面量节点基类"""
    def __init__(self, value, line, column):
        super().__init__(line, column)
        self.value = value

class IntegerLiteral(Literal):
    """整数字面量节点"""
    pass

class FloatLiteral(Literal):
    """浮点数字面量节点"""
    pass

class StringLiteral(Literal):
    """字符串字面量节点"""
    pass

class BooleanLiteral(Literal):
    """布尔字面量节点"""
    pass

class NoneLiteral(Literal):
    """空值字面量节点"""
    def __init__(self, line, column):
        super().__init__(None, line, column)

class Identifier(ASTNode):
    """标识符节点"""
    def __init__(self, name, line, column):
        super().__init__(line, column)
        self.name = name

class BinaryOperation(ASTNode):
    """二元操作节点"""
    def __init__(self, left, operator, right, line, column):
        super().__init__(line, column)
        self.left = left
        self.operator = operator
        self.right = right

class UnaryOperation(ASTNode):
    """一元操作节点"""
    def __init__(self, operator, operand, line, column):
        super().__init__(line, column)
        self.operator = operator
        self.operand = operand

class Assignment(ASTNode):
    """赋值节点"""
    def __init__(self, name, value, line, column):
        super().__init__(line, column)
        self.name = name
        self.value = value

class GetAttribute(ASTNode):
    """属性获取节点"""
    def __init__(self, object, name, line, column):
        super().__init__(line, column)
        self.object = object
        self.name = name

class SetAttribute(ASTNode):
    """属性设置节点"""
    def __init__(self, object, name, value, line, column):
        super().__init__(line, column)
        self.object = object
        self.name = name
        self.value = value

class GetItem(ASTNode):
    """项获取节点"""
    def __init__(self, object, key, line, column):
        super().__init__(line, column)
        self.object = object
        self.key = key

class SetItem(ASTNode):
    """项设置节点"""
    def __init__(self, object, key, value, line, column):
        super().__init__(line, column)
        self.object = object
        self.key = key
        self.value = value

class VariableDeclaration(ASTNode):
    """变量声明节点"""
    def __init__(self, name, value, line, column):
        super().__init__(line, column)
        self.name = name
        self.value = value

class FunctionDefinition(ASTNode):
    """函数定义节点"""
    def __init__(self, name, params, body, decorators=None, line=0, column=0):
        super().__init__(line, column)
        self.name = name
        self.params = params
        self.body = body
        self.decorators = decorators or []

class ClassDefinition(ASTNode):
    """类定义节点"""
    def __init__(self, name, bases, body, decorators=None, line=0, column=0):
        super().__init__(line, column)
        self.name = name
        self.bases = bases
        self.body = body
        self.decorators = decorators or []

class FunctionCall(ASTNode):
    """函数调用节点"""
    def __init__(self, function, args, kwargs, line, column):
        super().__init__(line, column)
        self.function = function
        self.args = args
        self.kwargs = kwargs

class Return(ASTNode):
    """返回语句节点"""
    def __init__(self, value, line, column):
        super().__init__(line, column)
        self.value = value

class If(ASTNode):
    """if语句节点"""
    def __init__(self, condition, then_block, else_block, line, column):
        super().__init__(line, column)
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

class While(ASTNode):
    """while循环节点"""
    def __init__(self, condition, body, line, column):
        super().__init__(line, column)
        self.condition = condition
        self.body = body

class For(ASTNode):
    """for循环节点"""
    def __init__(self, target, iterable, body, line, column):
        super().__init__(line, column)
        self.target = target
        self.iterable = iterable
        self.body = body

class Break(ASTNode):
    """break语句节点"""
    pass

class Continue(ASTNode):
    """continue语句节点"""
    pass

class Pass(ASTNode):
    """pass语句节点"""
    pass

class Import(ASTNode):
    """import语句节点"""
    def __init__(self, module, alias, line, column):
        super().__init__(line, column)
        self.module = module
        self.alias = alias

class FromImport(ASTNode):
    """from import语句节点"""
    def __init__(self, module, names, line, column):
        super().__init__(line, column)
        self.module = module
        self.names = names  # [(name, alias), ...]

class Try(ASTNode):
    """try语句节点"""
    def __init__(self, try_block, except_blocks, finally_block, line, column):
        super().__init__(line, column)
        self.try_block = try_block
        self.except_blocks = except_blocks  # [(exception_type, exception_name, block), ...]
        self.finally_block = finally_block

class Raise(ASTNode):
    """raise语句节点"""
    def __init__(self, exception, line, column):
        super().__init__(line, column)
        self.exception = exception

class Assert(ASTNode):
    """assert语句节点"""
    def __init__(self, condition, message, line, column):
        super().__init__(line, column)
        self.condition = condition
        self.message = message

class With(ASTNode):
    """with语句节点"""
    def __init__(self, context_expr, optional_vars, body, line, column):
        super().__init__(line, column)
        self.context_expr = context_expr
        self.optional_vars = optional_vars
        self.body = body

class Attribute(ASTNode):
    """属性访问节点"""
    def __init__(self, value, attr, line, column):
        super().__init__(line, column)
        self.value = value
        self.attr = attr

class Subscript(ASTNode):
    """下标访问节点"""
    def __init__(self, value, index, line, column):
        super().__init__(line, column)
        self.value = value
        self.index = index

class List(ASTNode):
    """列表字面量节点"""
    def __init__(self, elements, line, column):
        super().__init__(line, column)
        self.elements = elements

class Tuple(ASTNode):
    """元组字面量节点"""
    def __init__(self, elements, line, column):
        super().__init__(line, column)
        self.elements = elements

class Dict(ASTNode):
    """字典字面量节点"""
    def __init__(self, keys, values, line, column):
        super().__init__(line, column)
        self.keys = keys
        self.values = values

class Set(ASTNode):
    """集合字面量节点"""
    def __init__(self, elements, line, column):
        super().__init__(line, column)
        self.elements = elements

class ListComprehension(ASTNode):
    """列表推导式节点"""
    def __init__(self, expression, target, iterable, conditions, line, column):
        super().__init__(line, column)
        self.expression = expression
        self.target = target
        self.iterable = iterable
        self.conditions = conditions

class DictComprehension(ASTNode):
    """字典推导式节点"""
    def __init__(self, key_expr, value_expr, target, iterable, conditions, line, column):
        super().__init__(line, column)
        self.key_expr = key_expr
        self.value_expr = value_expr
        self.target = target
        self.iterable = iterable
        self.conditions = conditions

class SetComprehension(ASTNode):
    """集合推导式节点"""
    def __init__(self, expression, target, iterable, conditions, line, column):
        super().__init__(line, column)
        self.expression = expression
        self.target = target
        self.iterable = iterable
        self.conditions = conditions

class Lambda(ASTNode):
    """lambda表达式节点"""
    def __init__(self, params, body, line, column):
        super().__init__(line, column)
        self.params = params
        self.body = body

class Decorator(ASTNode):
    """装饰器节点"""
    def __init__(self, name, args, line, column):
        super().__init__(line, column)
        self.name = name
        self.args = args

class Async(ASTNode):
    """异步函数定义节点"""
    def __init__(self, function, line, column):
        super().__init__(line, column)
        self.function = function

class Await(ASTNode):
    """await表达式节点"""
    def __init__(self, value, line, column):
        super().__init__(line, column)
        self.value = value

class Yield(ASTNode):
    """yield表达式节点"""
    def __init__(self, value, line, column):
        super().__init__(line, column)
        self.value = value

class YieldFrom(ASTNode):
    """yield from表达式节点"""
    def __init__(self, value, line, column):
        super().__init__(line, column)
        self.value = value

class Global(ASTNode):
    """global语句节点"""
    def __init__(self, names, line, column):
        super().__init__(line, column)
        self.names = names

class Nonlocal(ASTNode):
    """nonlocal语句节点"""
    def __init__(self, names, line, column):
        super().__init__(line, column)
        self.names = names

class Delete(ASTNode):
    """del语句节点"""
    def __init__(self, targets, line, column):
        super().__init__(line, column)
        self.targets = targets

# 添加表达式语句节点
class ExpressionStatement(ASTNode):
    """表达式语句节点"""
    def __init__(self, expression, line, column):
        super().__init__(line, column)
        self.expression = expression
