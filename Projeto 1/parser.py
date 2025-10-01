import ply.lex as lex
import ply.yacc as yacc

# Tokens
tokens = (
    'PLUS','MINUS','TIMES','DIV','DIVINT','MOD','EXP',
    'LT','GT','LE','GE','EQ','NE',
    'LPAREN','RPAREN','QUOTE',
    'NUMBER','ID'
)

# Regras léxicas
t_PLUS   = r'\+'
t_MINUS  = r'-'
t_TIMES  = r'\*'
t_DIV    = r'/'
t_DIVINT = r'div'
t_MOD    = r'mod'
t_EXP    = r'exp'

t_LT     = r'<'
t_GT     = r'>'
t_LE     = r'<='
t_GE     = r'>='
t_EQ     = r'='
t_NE     = r'!='

t_LPAREN = r'\('
t_RPAREN = r'\)'
t_QUOTE  = r'\''

def t_NUMBER(t):
    r'-?\d+'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t

def t_COMMENT(t):
    r'\;.*'
    pass

t_ignore = ' \t\r\n'

def t_error(t):
    print(f"Caractere ilegal: {t.value[0]!r}")
    t.lexer.skip(1)

lexer = lex.lex()

# Parser
def p_program(p): # Programa = várias expressões
    '''program : expr_list'''
    p[0] = ("program", p[1])

# Lista de expressões
def p_expr_list(p):
    '''expr_list : expr expr_list
                 | expr'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

# Expressões possíveis
def p_expr(p):
    '''expr : atom
            | list'''
    p[0] = p[1]

# Átomos
def p_atom_number(p):
    '''atom : NUMBER'''
    p[0] = ("number", p[1])

def p_atom_id(p):
    '''atom : ID'''
    p[0] = ("id", p[1])

def p_list(p):
    '''list : LPAREN expr_list RPAREN'''
    p[0] = ("list", p[2])

def p_error(p):
    if p:
        print(f"Erro de sintaxe perto de '{p.value}'")
    else:
        print("Erro de sintaxe no fim do arquivo")

parser = yacc.yacc()

# Teste
if __name__ == "__main__":
    data = """
    (define fact 
        (lambda (n)
            (if (<= n 1)
                1
                (* n (fact (- n 1))))))
    """

    result = parser.parse(data)
    print(result)
