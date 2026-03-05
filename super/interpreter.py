"""
SuperStaticLanguage - Interpreter
"""

def run(code: str, args: dict = {}):
    from .lexer import tokenize
    from .parser import Parser
    from .evaluator import Interpreter

    tokens      = tokenize(code)
    ast         = Parser(tokens).parse()
    interpreter = Interpreter(extra=args)
    interpreter.run(ast)
