"""
玄语言主程序入口 - 提供命令行接口和REPL环境
"""

import os
import sys
import argparse
from xuan.lexer import Lexer
from xuan.parser import Parser
from xuan.interpreter import Interpreter
from xuan.exceptions import XUANError

def run_file(filename):
    """执行玄语言源文件"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
        
        run(source, filename)
    except FileNotFoundError:
        print(f"错误: 找不到文件 '{filename}'")
        sys.exit(1)
    except XUANError as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print(f"内部错误: {e}")
        sys.exit(1)

def run_repl():
    """运行交互式解释器"""
    interpreter = Interpreter()
    
    print("玄语言解释器 v0.1.0")
    print("输入 '退出()' 或按 Ctrl+D (Unix) / Ctrl+Z (Windows) 退出")
    
    while True:
        try:
            lines = []
            line = input(">>> ")
            if line.strip() == "退出()":
                break
            
            # 收集多行输入直到语句块完成
            while True:
                lines.append(line)
                source = "\n".join(lines)
                
                # 尝试解析，如果成功则执行，否则继续收集
                try:
                    lexer = Lexer(source)
                    tokens = lexer.tokenize()
                    parser = Parser(tokens)
                    program = parser.parse()
                    break  # 解析成功，退出收集循环
                except XUANError as e:
                    # 如果是未完成语句的错误，继续收集
                    if "未完成" in str(e) or "期望" in str(e):
                        line = input("... ")
                        continue
                    raise  # 其他错误直接抛出
            
            # 执行完整的程序
            try:
                result = interpreter.interpret(program)
                if result is not None:
                    print(result)
            except XUANError as e:
                print(e)
            except Exception as e:
                print(f"内部错误: {e}")
        except EOFError:
            print("\n再见!")
            break
        except KeyboardInterrupt:
            print("\n操作被中断")
            continue

def run(source, filename="<stdin>"):
    """执行玄语言代码"""
    lexer = Lexer(source, filename)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    interpreter = Interpreter()
    
    program = parser.parse()
    return interpreter.interpret(program)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="玄语言解释器")
    parser.add_argument('file', nargs='?', help='要执行的玄语言源文件')
    parser.add_argument('-v', '--version', action='version', version='玄语言 v0.1.0')
    
    args = parser.parse_args()
    
    if args.file:
        run_file(args.file)
    else:
        run_repl()

if __name__ == "__main__":
    main()
