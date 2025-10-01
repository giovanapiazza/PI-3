import ply.lex as lex

# Lista de tokens
tokens = (
    # Aritméticos
    'PLUS', 'MINUS', 'TIMES', 'DIV', 'DIVINT', 'MOD', 'EXP',

    # Comparação
    'LT', 'GT', 'LE', 'GE', 'EQ', 'NE',

    # Especiais
    'LPAREN', 'RPAREN', 'QUOTE',

    # Literais e identificadores
    'NUMBER', 'ID',
)

# Regulares simples
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

# Tokens mais complexos
def t_NUMBER(t):
    r'-?\d+'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t

# Comentários e espaços
def t_COMMENT(t):
    r'\;.*'
    pass  

t_ignore = ' \t\r\n'  # ignora espaços, tabs e quebras de linha

def t_error(t):
    print(f"Caractere invalido: {t.value[0]!r}")
    t.lexer.skip(1)

# Teste
if __name__ == "__main__":
    lexer = lex.lex()

    # Exemplo de código LISP-like
    data = """
    (define fact 
        (lambda (n)
            (if (<= n 1)
                1
                (* n (fact (- n 1))))))
    ; comentário deve ser ignorado
    """

    lexer.input(data)
    for tok in lexer:
        print(tok)
