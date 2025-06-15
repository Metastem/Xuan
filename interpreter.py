"""
解释器模块 - 遍历和执行抽象语法树
"""

from .ast import *
from .exceptions import *

class Environment:
    """环境类，用于存储变量"""
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing
    
    def define(self, name, value):
        """定义变量"""
        self.values[name] = value
    
    def get(self, name):
        """获取变量值"""
        if name in self.values:
            return self.values[name]
        if self.enclosing:
            return self.enclosing.get(name)
        raise NameError(f"未定义的变量: '{name}'")
    
    def assign(self, name, value):
        """赋值变量"""
        if name in self.values:
            self.values[name] = value
            return
        if self.enclosing:
            self.enclosing.assign(name, value)
            return
        raise NameError(f"未定义的变量: '{name}'")

class XUANFunction:
    """函数类"""
    def __init__(self, declaration, closure, is_initializer=False):
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer
    
    def __call__(self, interpreter, arguments):
        environment = Environment(self.closure)
        
        for param, arg in zip(self.declaration.params, arguments):
            environment.define(param, arg)
        
        try:
            interpreter.execute_block(self.declaration.body.statements, environment)
        except ReturnValue as return_value:
            if self.is_initializer:
                return self.closure.get("自身")
            return return_value.value
        
        if self.is_initializer:
            return self.closure.get("自身")
        return None

class XUANClass:
    """类"""
    def __init__(self, name, superclass, methods):
        self.name = name
        self.superclass = superclass
        self.methods = methods
    
    def __str__(self):
        return self.name
    
    def find_method(self, name):
        """查找方法"""
        if name in self.methods:
            return self.methods[name]
        if self.superclass:
            return self.superclass.find_method(name)
        return None

class XUANInstance:
    """类实例"""
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}
    
    def __str__(self):
        return f"{self.klass.name} 实例"
    
    def get(self, name):
        """获取属性"""
        if name in self.fields:
            return self.fields[name]
        
        method = self.klass.find_method(name)
        if method:
            return method.bind(self)
        
        raise AttributeError(f"{str(self)}没有属性'{name}'")
    
    def set(self, name, value):
        """设置属性"""
        self.fields[name] = value

class ReturnValue(Exception):
    """用于处理返回语句的特殊异常"""
    def __init__(self, value):
        self.value = value

class Interpreter:
    """解释器类"""
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.locals = {}
        
        # 添加内置函数
        self.globals.define("输出", print)
        self.globals.define("输入", input)
        self.globals.define("整数", int)
        self.globals.define("浮点数", float)
        self.globals.define("字符串", str)
        self.globals.define("列表", list)
        self.globals.define("字典", dict)
        self.globals.define("长度", len)
    
    def interpret(self, program):
        """解释执行程序"""
        try:
            for statement in program.statements:
                self.execute(statement)
        except XUANError as error:
            raise error
        except Exception as e:
            raise RuntimeError(str(e))
    
    def execute(self, statement):
        """执行语句"""
        return statement.accept(self)
    
    def evaluate(self, expression):
        """求值表达式"""
        return expression.accept(self)
    
    def execute_block(self, statements, environment):
        """执行代码块"""
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous
    
    # 访问者模式方法
    def visit_Program(self, program):
        """访问程序节点"""
        for statement in program.statements:
            self.execute(statement)
    
    def visit_Block(self, block):
        """访问代码块节点"""
        self.execute_block(block.statements, Environment(self.environment))
    
    def visit_ExpressionStatement(self, stmt):
        """访问表达式语句"""
        self.evaluate(stmt.expression)
    
    def visit_FunctionDefinition(self, stmt):
        """访问函数声明"""
        function = XUANFunction(stmt, self.environment)
        self.environment.define(stmt.name, function)
    
    def visit_ClassDefinition(self, stmt):
        """访问类声明"""
        superclass = None
        if stmt.bases:
            superclass = self.evaluate(stmt.bases[0])
            if not isinstance(superclass, XUANClass):
                raise TypeError("父类必须是一个类")
        
        self.environment.define(stmt.name, None)
        
        if superclass:
            self.environment = Environment(self.environment)
            self.environment.define("父类", superclass)
        
        methods = {}
        for method in stmt.body.statements:
            if isinstance(method, FunctionDefinition):
                function = XUANFunction(
                    method,
                    self.environment,
                    method.name == "初始化"
                )
                methods[method.name] = function
        
        klass = XUANClass(stmt.name, superclass, methods)
        
        if superclass:
            self.environment = self.environment.enclosing
        
        self.environment.assign(stmt.name, klass)
    
    def visit_Return(self, stmt):
        """访问返回语句"""
        value = None
        if stmt.value:
            value = self.evaluate(stmt.value)
        raise ReturnValue(value)
    
    def visit_If(self, stmt):
        """访问if语句"""
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_block)
        elif stmt.else_block:
            self.execute(stmt.else_block)
    
    def visit_While(self, stmt):
        """访问while语句"""
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)
    
    def visit_For(self, stmt):
        """访问for语句"""
        iterable = self.evaluate(stmt.iterable)
        for item in iterable:
            environment = Environment(self.environment)
            environment.define(stmt.target.name, item)
            self.execute_block(stmt.body.statements, environment)
    
    def visit_Break(self, stmt):
        """访问break语句"""
        raise StopIteration()
    
    def visit_Continue(self, stmt):
        """访问continue语句"""
        raise RuntimeError("Continue not implemented")
    
    def visit_Pass(self, stmt):
        """访问pass语句"""
        pass
    
    def visit_Try(self, stmt):
        """访问try语句"""
        try:
            self.execute(stmt.try_block)
        except Exception as e:
            for except_block in stmt.except_blocks:
                exception_type, exception_name, block = except_block
                # TODO: 实现异常类型匹配
                if exception_name:
                    self.environment.define(exception_name, e)
                self.execute(block)
                return
            raise
        finally:
            if stmt.finally_block:
                self.execute(stmt.finally_block)
    
    def visit_Import(self, stmt):
        """访问导入语句"""
        # TODO: 实现模块导入
        pass
    
    def visit_FromImport(self, stmt):
        """访问from import语句"""
        # TODO: 实现模块导入
        pass
    
    def visit_BinaryOperation(self, expr):
        """访问二元表达式"""
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        
        op_type = expr.operator.type
        
        if op_type == "加":
            return left + right
        if op_type == "减":
            return left - right
        if op_type == "乘":
            return left * right
        if op_type == "除":
            if right == 0:
                raise ZeroDivisionError("除数不能为零")
            return left / right
        if op_type == "等于":
            return left == right
        if op_type == "不等于":
            return left != right
        if op_type == "小于":
            return left < right
        if op_type == "小于等于":
            return left <= right
        if op_type == "大于":
            return left > right
        if op_type == "大于等于":
            return left >= right
        
        return None
    
    def visit_UnaryOperation(self, expr):
        """访问一元表达式"""
        operand = self.evaluate(expr.operand)
        
        op_type = expr.operator.type
        
        if op_type == "负":
            return -operand
        if op_type == "非":
            return not self.is_truthy(operand)
        
        return None
    
    def visit_FunctionCall(self, expr):
        """访问调用表达式"""
        callee = self.evaluate(expr.function)
        args = [self.evaluate(arg) for arg in expr.args]
        kwargs = {k: self.evaluate(v) for k, v in expr.kwargs.items()}
        
        if not callable(callee):
            raise TypeError(f"{callee} 不是可调用的")
        
        return callee(self, args, **kwargs)
    
    def visit_Attribute(self, expr):
        """访问属性访问表达式"""
        obj = self.evaluate(expr.value)
        
        if isinstance(obj, XUANInstance):
            return obj.get(expr.attr)
        
        raise TypeError("只能从实例获取属性")
    
    def visit_Assignment(self, expr):
        """访问赋值表达式"""
        value = self.evaluate(expr.right)
        
        if isinstance(expr.left, Identifier):
            self.environment.assign(expr.left.name, value)
        elif isinstance(expr.left, Attribute):
            obj = self.evaluate(expr.left.value)
            if isinstance(obj, XUANInstance):
                obj.set(expr.left.attr, value)
            else:
                raise TypeError("只能在实例上设置属性")
        elif isinstance(expr.left, Subscript):
            obj = self.evaluate(expr.left.value)
            index = self.evaluate(expr.left.index)
            obj[index] = value
        else:
            raise SyntaxError("无效的赋值目标")
        
        return value
    
    def visit_List(self, expr):
        """访问列表表达式"""
        elements = [self.evaluate(element) for element in expr.elements]
        return elements
    
    def visit_Dict(self, expr):
        """访问字典表达式"""
        keys = [self.evaluate(key) for key in expr.keys]
        values = [self.evaluate(value) for value in expr.values]
        return dict(zip(keys, values))
    
    def visit_Subscript(self, expr):
        """访问索引表达式"""
        obj = self.evaluate(expr.value)
        index = self.evaluate(expr.index)
        
        try:
            return obj[index]
        except (IndexError, KeyError) as e:
            raise IndexError(f"索引错误: {index}")
    
    def visit_VariableDeclaration(self, expr):
        """访问变量声明"""
        value = None
        if expr.value:
            value = self.evaluate(expr.value)
        self.environment.define(expr.name, value)
        return value
    
    def visit_Identifier(self, expr):
        """访问变量表达式"""
        return self.environment.get(expr.name)
    
    def visit_IntegerLiteral(self, expr):
        """访问整数字面量"""
        return expr.value
    
    def visit_FloatLiteral(self, expr):
        """访问浮点数字面量"""
        return expr.value
    
    def visit_StringLiteral(self, expr):
        """访问字符串字面量"""
        return expr.value
    
    def visit_BooleanLiteral(self, expr):
        """访问布尔字面量"""
        return expr.value
    
    def visit_NoneLiteral(self, expr):
        """访问空值字面量"""
        return None
    
    def visit_default(self, node):
        """默认访问方法"""
        raise NotImplementedError(f"未实现的访问方法: {type(node).__name__}")
    
    def is_truthy(self, value):
        """判断值的真假"""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, (str, list, dict)):
            return len(value) > 0
        return True
