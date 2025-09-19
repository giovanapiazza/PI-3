import ply.lex as lex

# Lista de tokens
tokens = (
    # Operadores aritméticos
    'PLUS', 'MINUS', 'TIMES', 'DIV', 'DIVINT', 'MOD', 'EXP',

    # Operadores de comparação
    'LT', 'GT', 'LE', 'GE', 'EQ', 'NE',

    # Símbolos
    'ASSIGN', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'COMMA', 'SEMICOLON',

    # Literais
    'INT', 'FLOAT', 'ID',

    # Palavras reservadas
    'FUNCTION', 'RETURN', 'IF', 'ELSE', 'WHILE', 'FOR',

    'SPACE', 'TAB', 'NEWLINE',
)

# Regras simples (regex)
t_PLUS      = r'\+'
t_MINUS     = r'\-'
t_TIMES     = r'\*'
t_DIV       = r'\/'
t_EXP       = r'\^'
t_MOD       = r'\%'
t_LT        = r'\<'
t_GT        = r'\>'
t_LE        = r'\<='
t_GE        = r'\>='
t_EQ        = r'\=='
t_NE        = r'\!='
t_ASSIGN    = r'\='
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LBRACE    = r'\{'
t_RBRACE    = r'\}'
t_COMMA     = r'\,'
t_SEMICOLON = r'\;'

# Palavras reservadas
reserved_map = {
    'function': 'FUNCTION',
    'return':   'RETURN',
    'if':       'IF',
    'else':     'ELSE',
    'while':    'WHILE',
    'for':      'FOR',
    'div':      'DIVINT',
}

# Tokens com ação
def t_FLOAT(t):
    r'\0|[1-9]\[0-9]\.\[0-9]'
    t.value = float(t.value)
    return t

def t_NUMBER(t):
    r'0|[1-9][0-9]*'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved_map.get(t.value, 'ID')  # Verifica palavra reservada
    return t

# Comentários e espaços
def t_COMMENT(t):
    r'//.|/\[\s\S]?\/'
    pass  # Ignora comentário

t_ignore = ' \t'  # Espaços e tabulações

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Tratamento de erro
def t_error(t):
    print(f"Caractere ilegal '{t.value[0]}' na linha {t.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()
data = '''
function soma(x, y) {
    return x + y;
}
z = soma(10, 20) div 2 mod 3;
if (z >= 10) {
    z = z exp 2;
}
'''
lexer.input(data)

for tok in lexer:
    print(lexer.token())
