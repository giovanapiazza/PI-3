import ply.lex as lex
import ply.yacc as yacc

# Lexer
tokens = (
    'PLUS', 'MINUS', 'TIMES', 'DIV', 'DIVINT', 'MOD', 'EXP',
    'LT', 'GT', 'LE', 'GE', 'EQ', 'NE',
    'LPAREN', 'RPAREN',
    'ID', 'NUMBER'
)

t_PLUS   = r'\+'
t_MINUS  = r'-'
t_TIMES  = r'\*'
t_DIV    = r'/'
t_DIVINT = r'div'
t_MOD    = r'mod'
t_EXP    = r'exp'

t_LT = r'<'
t_GT = r'>'
t_LE = r'<='
t_GE = r'>='
t_EQ = r'='
t_NE = r'!='

t_LPAREN = r'\('
t_RPAREN = r'\)'

t_ignore = ' \t\n'

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t

def t_error(t):
    print(f"Caractere inválido: {t.value[0]}")
    t.lexer.skip(1)

lexer = lex.lex()

# Parser
def p_expression_number(p):
    'expression : NUMBER'
    p[0] = ('number', p[1])

def p_expression_id(p):
    'expression : ID'
    p[0] = ('id', p[1])

def p_expression_binop(p):
    '''expression : LPAREN PLUS expression expression RPAREN
                  | LPAREN MINUS expression expression RPAREN
                  | LPAREN TIMES expression expression RPAREN
                  | LPAREN DIV expression expression RPAREN
                  | LPAREN DIVINT expression expression RPAREN
                  | LPAREN MOD expression expression RPAREN
                  | LPAREN EXP expression expression RPAREN
                  | LPAREN LT expression expression RPAREN
                  | LPAREN GT expression expression RPAREN
                  | LPAREN LE expression expression RPAREN
                  | LPAREN GE expression expression RPAREN
                  | LPAREN EQ expression expression RPAREN
                  | LPAREN NE expression expression RPAREN'''
    p[0] = ('binop', p[2], p[3], p[4])

def p_expression_defun(p):
    '''expression : LPAREN ID expression RPAREN'''
    p[0] = ('call', p[1], p[3])

def p_error(p):
    print("Erro de sintaxe!")

parser = yacc.yacc()

# Interpretador
env = {}

def eval_expr(expr):
    etype = expr[0]

    if etype == 'number':
        return expr[1]

    elif etype == 'id':
        return env.get(expr[1], f"Erro: variável {expr[1]} não definida")

    elif etype == 'binop':
        op, left, right = expr[1], expr[2], expr[3]
        lval, rval = eval_expr(left), eval_expr(right)

        if op == '+': return lval + rval
        elif op == '-': return lval - rval
        elif op == '*': return lval * rval
        elif op == '/': return lval / rval
        elif op == 'div': return lval // rval
        elif op == 'mod': return lval % rval
        elif op == 'exp': return lval ** rval
        elif op == '<': return lval < rval
        elif op == '>': return lval > rval
        elif op == '<=': return lval <= rval
        elif op == '>=': return lval >= rval
        elif op == '=': return lval == rval
        elif op == '!=': return lval != rval

    return None


# Testes
while True:
    try:
        s = input("lisp> ")
    except EOFError:
        break
    if not s:
        continue
    result = parser.parse(s)
    print("AST:", result)
    print("Resultado:", eval_expr(result))
