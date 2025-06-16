"""
内置函数模块 - 提供玄码（xuan）编程语言的内置函数和类型
"""

import math
import random
import time
import os
import sys
from datetime import datetime

class Builtins:
    """内置函数和类型"""
    
    @staticmethod
    def register(interpreter):
        """注册所有内置函数到解释器环境"""
        env = interpreter.globals
        
        # 基本输入输出
        env.define("输出", Builtins.print_func)
        env.define("输入", input)
        
        # 类型转换
        env.define("整数", int)
        env.define("浮点数", float)
        env.define("字符串", str)
        env.define("布尔", bool)
        env.define("列表", list)
        env.define("字典", dict)
        env.define("集合", set)
        env.define("元组", tuple)
        
        # 数学函数
        env.define("绝对值", abs)
        env.define("最大值", max)
        env.define("最小值", min)
        env.define("总和", sum)
        env.define("四舍五入", round)
        env.define("向上取整", math.ceil)
        env.define("向下取整", math.floor)
        env.define("幂", pow)
        env.define("平方根", math.sqrt)
        env.define("正弦", math.sin)
        env.define("余弦", math.cos)
        env.define("正切", math.tan)
        env.define("对数", math.log)
        env.define("自然对数", math.log)
        env.define("常数_圆周率", math.pi)
        env.define("常数_自然底数", math.e)
        
        # 随机数
        env.define("随机数", random.random)
        env.define("随机整数", random.randint)
        env.define("随机选择", random.choice)
        env.define("随机打乱", random.shuffle)
        
        # 序列操作
        env.define("长度", len)
        env.define("范围", range)
        env.define("枚举", enumerate)
        env.define("排序", sorted)
        env.define("反转", reversed)
        env.define("映射", map)
        env.define("过滤", filter)
        env.define("压缩", zip)
        
        # 字符串操作
        env.define("分割", str.split)
        env.define("连接", str.join)
        env.define("替换", str.replace)
        env.define("查找", str.find)
        env.define("大写", str.upper)
        env.define("小写", str.lower)
        env.define("首字母大写", str.capitalize)
        env.define("去空格", str.strip)
        
        # 时间日期
        env.define("当前时间", time.time)
        env.define("睡眠", time.sleep)
        env.define("当前日期时间", datetime.now)
        env.define("格式化时间", datetime.strftime)
        
        # 系统操作
        env.define("退出", sys.exit)
        env.define("命令行参数", sys.argv)
        env.define("环境变量", os.environ)
        env.define("当前目录", os.getcwd)
        env.define("改变目录", os.chdir)
        env.define("列出目录", os.listdir)
        env.define("创建目录", os.mkdir)
        env.define("删除文件", os.remove)
        env.define("路径存在", os.path.exists)
        env.define("是文件", os.path.isfile)
        env.define("是目录", os.path.isdir)
        
        # 文件操作
        env.define("打开文件", open)
        env.define("读取文件", Builtins.read_file)
        env.define("写入文件", Builtins.write_file)
        env.define("追加文件", Builtins.append_file)
        
        # 其他
        env.define("帮助", help)
        env.define("类型", type)
        env.define("标识", id)
        env.define("是实例", isinstance)
        env.define("哈希值", hash)
        env.define("全局变量", globals)
        env.define("局部变量", locals)
        env.define("执行", eval)
        env.define("执行代码", exec)
    
    @staticmethod
    def print_func(interpreter, arguments):
        """输出函数"""
        print(*arguments)
        return None
    
    @staticmethod
    def read_file(interpreter, arguments):
        """读取文件函数"""
        if len(arguments) < 1:
            raise ValueError("读取文件需要至少一个参数：文件路径")
        
        filepath = arguments[0]
        encoding = arguments[1] if len(arguments) > 1 else 'utf-8'
        
        with open(filepath, 'r', encoding=encoding) as f:
            return f.read()
    
    @staticmethod
    def write_file(interpreter, arguments):
        """写入文件函数"""
        if len(arguments) < 2:
            raise ValueError("写入文件需要至少两个参数：文件路径和内容")
        
        filepath = arguments[0]
        content = arguments[1]
        encoding = arguments[2] if len(arguments) > 2 else 'utf-8'
        
        with open(filepath, 'w', encoding=encoding) as f:
            f.write(content)
        
        return None
    
    @staticmethod
    def append_file(interpreter, arguments):
        """追加文件函数"""
        if len(arguments) < 2:
            raise ValueError("追加文件需要至少两个参数：文件路径和内容")
        
        filepath = arguments[0]
        content = arguments[1]
        encoding = arguments[2] if len(arguments) > 2 else 'utf-8'
        
        with open(filepath, 'a', encoding=encoding) as f:
            f.write(content)
        
        return None
