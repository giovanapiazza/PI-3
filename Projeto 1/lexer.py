import ply.lex as lex

# Palavras reservadas
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
    'div'   : 'DIVINT',
    'mod'   : 'MOD',
    'exp'   : 'EXP',
}

# Lista de tokens
tokens = [
    'LPAREN', 'RPAREN', 'QUOTE',
    'NUMBER', 'ID',
    'PLUS', 'MINUS', 'TIMES', 'DIV',
    'LT', 'GT', 'LE', 'GE', 'EQUALS', 'NE',
] + list(reserved.values())

# Tokens compostos
t_LE     = r'<='
t_GE     = r'>='
t_NE     = r'!='

# Tokens simples
t_LT     = r'<'
t_GT     = r'>'
t_EQUALS = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_QUOTE  = r"\'"
t_PLUS   = r'\+'
t_MINUS  = r'-'
t_TIMES  = r'\*'
t_DIV    = r'/'

# Ignorar espaços
t_ignore = " \t\r"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_NUMBER(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value) if '.' in t.value else int(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_COMMENT(t):
    r'\;.*'
    pass

def t_error(t):
    print(f"Caractere inválido: {t.value[0]} na linha {t.lexer.lineno}")
    t.lexer.skip(1)

if __name__ == "__main__":
    lexer = lex.lex()
    data = "( defun sqr (div 12 0 2 300))"
    lexer.input(data)
    for tok in lexer:
        print(tok)
