"""
命令行接口模块 - 处理命令行参数并运行解释器
"""

import sys
import argparse
import traceback
from pathlib import Path

from .lexer import Lexer
from .parser import Parser
from .interpreter import Interpreter
from .exceptions import XUANError

def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description='玄语言解释器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  xuan                 # 启动交互式解释器
  xuan 文件.xuan       # 运行玄语言文件
  xuan -v             # 显示版本信息
  xuan -h             # 显示帮助信息
""")
    
    parser.add_argument(
        'file',
        nargs='?',
        type=str,
        help='要运行的玄语言文件'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='玄语言 0.1.0',
        help='显示版本信息'
    )
    
    return parser

def run_file(file_path):
    """运行玄语言文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        interpreter.interpret(ast)
        
    except FileNotFoundError:
        print(f"错误：找不到文件 '{file_path}'")
        sys.exit(1)
    except XUANError as e:
        print(f"错误：{str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"内部错误：{str(e)}")
        traceback.print_exc()
        sys.exit(1)

def run_repl():
    """运行交互式解释器"""
    print("玄语言 0.1.0 交互式解释器")
    print('输入 "退出()" 或按 Ctrl+D (Unix) / Ctrl+Z (Windows) 退出')
    print()
    
    interpreter = Interpreter()
    
    while True:
        try:
            line = input('>>> ')
            if line.strip() == '退出()':
                break
            
            lexer = Lexer(line)
            tokens = lexer.tokenize()
            
            parser = Parser(tokens)
            ast = parser.parse()
            
            result = interpreter.interpret(ast)
            if result is not None:
                print(result)
                
        except KeyboardInterrupt:
            print()
            continue
        except EOFError:
            print()
            break
        except XUANError as e:
            print(f"错误：{str(e)}")
        except Exception as e:
            print(f"内部错误：{str(e)}")
            traceback.print_exc()

def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.file:
        run_file(args.file)
    else:
        run_repl()

if __name__ == '__main__':
    main()
