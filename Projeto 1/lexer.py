import ply.lex as lex

# Palavras reservadas da linguagem
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
    'LPAREN', 'RPAREN', 'QUOTE',
    'NUMBER', 'ID',

    # Operadores aritméticos
    'PLUS', 'MINUS', 'TIMES', 'DIV', 'DIVINT', 'MOD', 'EXP',

    # Operadores relacionais
    'LT', 'GT', 'LE', 'GE', 'EQUALS', 'NE',
] + list(reserved.values())

# Tokens MULTICARACTERE primeiro
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
t_DIVINT = r'div'
t_MOD    = r'mod'
t_EXP    = r'exp'

# Ignorar espaços e quebras de linha
t_ignore = " \t\n\r"


def t_NUMBER(t):
    r'0|([1-9][0-9]*)'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')  # Verifica se é palavra reservada
    return t

def t_COMMENT(t):
    r'\;.*'
    pass  # Apenas ignora comentários iniciados com ;

# Erro lexical
def t_error(t):
    print(f"Caractere inválido: {t.value[0]}")
    t.lexer.skip(1)

if __name__ == "__main__":
    lexer = lex.lex()

    data = "( defun sqr (div 12 0 2 300))"

    lexer.input(data)

    for tok in lexer:
        print(tok)
