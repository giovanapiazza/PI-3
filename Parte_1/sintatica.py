import ply.lex as lex
import ply.yacc as yacc

reserved = {
    'defun': 'DEFUN',
    'if': 'IF',
    'cond': 'COND',
    'car': 'CAR',
    'cdr': 'CDR',
    'cons': 'CONS',
    'eq': 'EQSYM',
    'nil': 'NIL',
    't': 'T'
}

tokens = [
    'LPAREN', 'RPAREN', 'QUOTE', 'NUMBER', 'ID',
    'PLUS', 'MINUS', 'TIMES', 'DIV', 'DIVINT', 'MOD', 'EXP',
    'LT', 'GT', 'LE', 'GE', 'EQUAL', 'NEQ'
] + list(reserved.values())

# Símbolos simples
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_QUOTE = r"\'"

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIV = r'/'
t_DIVINT = r'div'
t_MOD = r'mod'
t_EXP = r'exp'

t_LT = r'<'
t_GT = r'>'
t_LE = r'<='
t_GE = r'>='
t_EQUAL = r'='
t_NEQ = r'!='

t_ignore = ' \t\n\r'

# Tokens mais complexos
def t_NUMBER(t):
    r'0|([1-9][0-9]*)'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value in reserved:
        t.type = reserved[t.value]
    return t

def t_COMMENT(t):
    r'\;.*'
    pass

def t_error(t):
    print(f"Caractere inválido: {t.value[0]}")
    t.lexer.skip(1)

# SINTÁTICO
# Programa → várias expressões
def p_program(p):
    '''program : expr_list'''
    p[0] = ("program", p[1])

def p_expr_list(p):
    '''expr_list : expr expr_list
                 | expr'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

# Expressões
def p_expr(p):
    '''expr : atom
            | list'''
    p[0] = p[1]

# Átomos (números e identificadores)
def p_atom_number(p):
    'atom : NUMBER'
    p[0] = ("number", p[1])

def p_atom_id(p):
    'atom : ID'
    p[0] = ("id", p[1])

# Listas e chamadas de função
def p_list_binop(p):
    '''list : LPAREN PLUS expr expr RPAREN
            | LPAREN MINUS expr expr RPAREN
            | LPAREN TIMES expr expr RPAREN
            | LPAREN DIV expr expr RPAREN
            | LPAREN DIVINT expr expr RPAREN
            | LPAREN MOD expr expr RPAREN
            | LPAREN EXP expr expr RPAREN
            | LPAREN LT expr expr RPAREN
            | LPAREN GT expr expr RPAREN
            | LPAREN LE expr expr RPAREN
            | LPAREN GE expr expr RPAREN
            | LPAREN EQUAL expr expr RPAREN
            | LPAREN NEQ expr expr RPAREN'''
    p[0] = ("binop", p[2], p[3], p[4])

# Definição de função (ex: (defun nome (args) corpo))
def p_list_defun(p):
    '''list : LPAREN DEFUN ID LPAREN arg_list RPAREN expr RPAREN'''
    p[0] = ("defun", p[3], p[5], p[7])

def p_arg_list(p):
    '''arg_list : ID arg_list
                | ID
                | empty'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    elif len(p) == 2 and p[1] is not None:
        p[0] = [p[1]]
    else:
        p[0] = []

# Condicional simples
def p_list_if(p):
    '''list : LPAREN IF expr expr expr RPAREN'''
    p[0] = ("if", p[3], p[4], p[5])

# Lista genérica (ex: (foo 1 2))
def p_list_call(p):
    '''list : LPAREN ID expr_list RPAREN'''
    p[0] = ("call", p[2], p[3])

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        print(f"Erro de sintaxe perto de '{p.value}'")
    else:
        print("Erro de sintaxe no fim do arquivo")

parser = yacc.yacc()

#teste
if __name__ == "__main__":
    data = """
    (defun soma (x y)
        (+ x y))
    (if (> 5 2)
        (soma 3 4)
        0)
    """

    result = parser.parse(data)
    print("AST resultante:\n", result)
