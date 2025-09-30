import ply.lex as lex
import ply.yacc as yacc
import sys
from collections import ChainMap

# LEXER
tokens = (
    'LPAREN','RPAREN','QUOTE',
    'NUMBER','BOOL','SYMBOL','STRING'
)

t_LPAREN = r'\('
t_RPAREN = r'\)'
t_QUOTE  = r"\'"

t_ignore = ' \t\r\n'

def t_BOOL(t):
    r'\#t|\#f'
    t.value = True if t.value == '#t' else False
    return t

def t_NUMBER(t):
    r'-?\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r'\"([^"\\]|\\.)*\"'
    t.value = t.value[1:-1]
    return t

def t_SYMBOL(t):
    r'[^()\s\'"]+'
    t.value = str(t.value)
    return t

def t_error(t):
    raise SyntaxError(f"Illegal character {t.value[0]!r}")

lexer = lex.lex()

# PARSER
def p_expr_atom(p):
    '''expr : NUMBER
            | BOOL
            | STRING
            | SYMBOL'''
    p[0] = p[1]

def p_expr_quote(p):
    'expr : QUOTE expr'
    # (quote expr) represented as ['quote', expr]
    p[0] = ['quote', p[2]]

def p_expr_list(p):
    'expr : LPAREN list RPAREN'
    p[0] = p[2]

def p_list_empty(p):
    'list : '
    p[0] = []

def p_list_multi(p):
    'list : expr list'
    p[0] = [p[1]] + p[2]

def p_error(p):
    if p:
        raise SyntaxError(f"Syntax error at '{p.value}'")
    else:
        raise SyntaxError("Syntax error at EOF")

parser = yacc.yacc()

# EVALUATOR
class LispError(Exception):
    pass

def is_symbol(x):
    return isinstance(x, str) and not (x.startswith('"') or x in ('#t','#f'))

def eval_ast(ast, env):
    """Avalia ast no ambiente env (ChainMap / dict-like)."""
    # Atoms
    if isinstance(ast, bool) or isinstance(ast, int) or isinstance(ast, str) and ast.startswith('"'):
        return ast
    if isinstance(ast, str):  # símbolo
        # look up symbol
        try:
            return env[ast]
        except KeyError:
            raise LispError(f"Unbound symbol: {ast}")

    # List handling
    if not ast:  # empty list -> Nil (represent as Python None or empty list)
        return []

    head = ast[0]
    # Special forms
    if head == 'quote':
        return ast[1]
    if head == 'if':
        # (if cond then else)
        _, cond_expr, then_expr, else_expr = ast
        cond = eval_ast(cond_expr, env)
        if cond is not False and cond != [] and cond is not None:
            return eval_ast(then_expr, env)
        else:
            return eval_ast(else_expr, env)
    if head == 'lambda':
        # (lambda (params...) body)
        _, params_list, body = ast
        params = params_list
        # return closure as a tuple ('closure', params, body, env_snapshot)
        return ('closure', params, body, env.maps[0].copy() if isinstance(env, ChainMap) else dict(env))
    if head == 'let':
        # (let ((x e1) (y e2)) body)
        _, bindings, body = ast
        # evaluate binding expressions first
        local = {}
        for bind in bindings:
            name = bind[0]
            val = eval_ast(bind[1], env)
            local[name] = val
        new_env = ChainMap(local, env)
        return eval_ast(body, new_env)
    if head == 'define':
        # (define name expr) -- top-level mutation
        _, name, expr = ast
        val = eval_ast(expr, env)
        # assume env.maps[-1] is top level? We'll use the first mapping (global at index 0)
        if isinstance(env, ChainMap):
            env.maps[0][name] = val
        else:
            env[name] = val
        return val
    # Application
    op = eval_ast(head, env)
    args = [eval_ast(arg, env) for arg in ast[1:]]
    # primitives
    if callable(op):
        return op(*args)
    # closure application
    if isinstance(op, tuple) and op[0] == 'closure':
        _, params, body, closure_env = op
        if len(params) != len(args):
            raise LispError("Incorrect number of arguments")
        # closure_env is a dict snapshot; create ChainMap with new bindings in front
        new_bindings = dict(zip(params, args))
        new_env = ChainMap(new_bindings, closure_env)
        return eval_ast(body, new_env)
    raise LispError(f"Application of non-function: {op}")


# Primitives and top-level env
import operator, functools

def lisp_add(*args):
    return sum(args)

def lisp_sub(a, *rest):
    if not rest:
        return -a
    return a - sum(rest)

def lisp_mul(*args):
    return functools.reduce(operator.mul, args, 1)

def lisp_div(a, *rest):
    if not rest:
        raise LispError("Division needs at least two args")
    result = a
    for r in rest:
        result = int(result / r)  # integer division mimic
    return result

def lisp_eq(a,b): return a == b
def lisp_lt(a,b): return a < b
def lisp_gt(a,b): return a > b
def lisp_le(a,b): return a <= b
def lisp_ge(a,b): return a >= b

def lisp_cons(a,b):
    if b == []: return [a]
    if isinstance(b, list): return [a] + b
    raise LispError("cons second arg must be list")

def lisp_car(lst):
    if not lst: raise LispError("car on empty")
    return lst[0]
def lisp_cdr(lst):
    if not lst: raise LispError("cdr on empty")
    return lst[1:]
def lisp_null(lst):
    return lst == []

# global env (ChainMap with one dict)
def initial_env():
    prims = {
        '+': lisp_add,
        '-': lisp_sub,
        '*': lisp_mul,
        '/': lisp_div,
        '=': lisp_eq,
        '<': lisp_lt,
        '>': lisp_gt,
        '<=': lisp_le,
        '>=': lisp_ge,
        'cons': lisp_cons,
        'car': lisp_car,
        'cdr': lisp_cdr,
        'null?': lisp_null,
        '#t': True,
        '#f': False,
    }
    return ChainMap(prims)

# REPL / runner
def parse(src):
    return parser.parse(src, lexer=lexer)

def repl():
    env = initial_env()
    while True:
        try:
            src = input('lisp> ')
            if not src:
                continue
            ast = parse(src)
            val = eval_ast(ast, env)
            print(repr(val))
        except (KeyboardInterrupt, EOFError):
            print("\nBye")
            break
        except Exception as e:
            print("Error:", e)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        repl()
    else:
        # evaluate file with multiple expressions
        env = initial_env()
        with open(sys.argv[1]) as f:
            src = f.read()
        # parse many top-level expressions: a quick hack: split on newlines and parse each non-empty line
        # Better: write a small loop tokenizing and parsing multiple exprs; here assume one-expression-per-line for simplicity.
        for line in src.splitlines():
            line = line.strip()
            if not line or line.startswith(';'): continue
            ast = parse(line)
            val = eval_ast(ast, env)
            print(repr(val))
