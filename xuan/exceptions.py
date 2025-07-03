"""
玄语言异常类定义模块

这个模块定义了玄语言中使用的所有异常类。
"""

class XUANError(Exception):
    """玄语言基础异常类"""
    def __init__(self, message="", line=None, column=None):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self._format_message())
    
    def _format_message(self):
        if self.line is not None and self.column is not None:
            return f"第{self.line}行，第{self.column}列: {self.message}"
        return self.message

class LexerError(XUANError):
    """词法分析错误"""
    def __init__(self, message="", line=None, column=None, error_code="LEX001", context=None):
        """
        Args:
            message (str): 错误描述
            line (int): 错误所在行号
            column (int): 错误所在列号
            error_code (str): 错误代码
            context (str): 错误上下文内容
        """
        self.error_code = error_code
        self.context = context
        super().__init__(message, line, column)
    
    def _format_message(self):
        msg = f"[{self.error_code}] {self.message}"
        if self.line is not None and self.column is not None:
            msg = f"第{self.line}行，第{self.column}列: {msg}"
        if self.context:
            msg += f"\n上下文: {self.context}"
        return msg

# 词法分析常见错误代码
LEXER_ERROR_CODES = {
    "LEX001": "未识别的字符",
    "LEX002": "未闭合的字符串",
    "LEX003": "无效的数字格式",
    "LEX004": "无效的转义序列",
    "LEX005": "缩进错误",
    "LEX006": "未闭合的f-string表达式",
    "LEX007": "未匹配的大括号",
    "LEX008": "无效的Unicode转义序列",
    "LEX009": "无效的标识符",
}

class ParserError(XUANError):
    """语法分析错误"""
    pass

class InterpreterError(XUANError):
    """解释器错误"""
    pass

class NameError(XUANError):
    """名称错误：使用未定义的变量或函数"""
    pass

class TypeError(XUANError):
    """类型错误：操作或函数应用于不适当类型的对象"""
    pass

class ValueError(XUANError):
    """值错误：操作或函数使用了类型正确但值不适当的参数"""
    pass

class AttributeError(XUANError):
    """属性错误：访问对象不存在的属性"""
    pass

class IndexError(XUANError):
    """索引错误：序列下标超出范围"""
    pass

class KeyError(XUANError):
    """键错误：映射中不存在的键"""
    pass

class ImportError(XUANError):
    """导入错误：导入模块失败"""
    pass

class ZeroDivisionError(XUANError):
    """零除错误：除数为零"""
    pass

class RecursionError(XUANError):
    """递归错误：递归深度超过最大限制"""
    pass

class FileNotFoundError(XUANError):
    """文件未找到错误：试图打开不存在的文件"""
    pass

class PermissionError(XUANError):
    """权限错误：没有足够的权限执行操作"""
    pass

class SyntaxError(XUANError):
    """语法错误：代码不符合语言语法"""
    pass

class IndentationError(SyntaxError):
    """缩进错误：代码缩进不正确"""
    pass

class RuntimeError(XUANError):
    """运行时错误：一般的运行时错误"""
    pass

class NotImplementedError(XUANError):
    """未实现错误：调用了未实现的功能"""
    pass

class AssertionError(XUANError):
    """断言错误：断言语句失败"""
    pass

class StopIteration(XUANError):
    """停止迭代：迭代器没有更多的值"""
    pass

class SystemExit(XUANError):
    """系统退出：请求终止解释器"""
    pass
