import ply.lex as lex

reserved = {
    'defun' : 'DEFUN',
    'if'    : 'IF',
    'cond'  : 'COND',
    'car'   : 'CAR',
    'cdr'   : 'CDR',
    'cons'  : 'CONS',
    'eq'    : 'EQ',
    'nil'   : 'NIL',
    't'     : 'T',
}

# Lista de tokens
tokens = [
    'LPAREN', 'RPAREN', 'QUOTE', 'NUMBER', 'ID', 'DEFUN',
    'PLUS', 'MINUS', 'TIMES', 'DIV', 'DIVINT', 'MOD', 'EXP',
    'LT', 'GT', 'LE', 'GE', 'EQ', 'NE', 'LIST'
    ] + list(reserved.values())

# Regulares simples
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_QUOTE = r"\'"

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

t_ignore = "\t\n\r\ "

# Tokens mais complexos
def t_NUMBER(t):
    r'0|([1-9][0-9]*)'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t

def t_error(t):
    print(f"Caractere inválido: {t.value[0]}")
    t.lexer.skip(1)

def t_COMMENT(t):
    r'\;.*'
    pass


if __name__ == "__main__":
    lexer = lex.lex()

    data = "( defun sqr (div 12 0 2 300))"

    lexer.input(data)
    for tok in lexer:
        print(tok)
