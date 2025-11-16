import ply.lex as lex
import ply.yacc as yacc

# Analisador Léxico 
tokens = (
    'PLUS', 'MINUS', 'TIMES', 'DIV', 'DIVINT', 'MOD', 'EXP',
    'LT', 'GT', 'LE', 'GE', 'EQ', 'NE',
    'LPAREN', 'RPAREN',
    'ID', 'NUMBER'
)

t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIV     = r'/'
t_DIVINT  = r'div'
t_MOD     = r'mod'
t_EXP     = r'exp'

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

# Analisador Sintático
def p_expression_number(p):
    'expression : NUMBER'
    # Retorna uma tupla simples para a AST
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
    # Gera o nó da AST para operação binária
    p[0] = ('binop', p[2], p[3], p[4])

# Regra de chamada
def p_expression_call(p):
    '''expression : LPAREN ID expression RPAREN'''
    # Corrigido de p[1] para p[2] (ID) e p[3] (expressão)
    p[0] = ('call', p[2], p[3])

def p_error(p):
    print("Erro de sintaxe!")

parser = yacc.yacc()

# Gerador de Código Intermediário
class Compiler:
    def __init__(self):
        self.intermediate_code = [] # Vetor de armazenamento 
        self.temp_counter = 0

    def new_temp(self):
        """ Cria uma nova variável temporária (ex: t0, t1, t2) [cite: 177] """
        self.temp_counter += 1
        return f't{self.temp_counter - 1}'

    def generate_code(self, node):
        """ 
        Passo 4: Percorre a árvore em profundidade, das folhas para a raiz 
        Gera quádruplas <op, arg1, arg2, result> [cite: 253]
        """
        etype = node[0]
            #Folha
        if etype == 'number':
            # Retorna o próprio valor (constante)
            return node[1]
        
        if etype == 'id':
            # Retorna o nome da variável
            return node[1]

        if etype == 'binop':
            op, left, right = node[1], node[2], node[3]
            
            # Folhas para a raiz
            l_val = self.generate_code(left)
            r_val = self.generate_code(right)
            
            # Novo temporário para o resultado
            result_temp = self.new_temp()
            
            # Determina a tupla (Quádrupla)
            quad = (op, l_val, r_val, result_temp)
            
            # Insere a instrução no vetor 
            self.intermediate_code.append(quad)
            
            # Retorna o nome do temporário que contém o resultado
            return result_temp

        if etype == 'call':
            print(f"Aviso: Geração de código para 'call' não implementada.")
            return None
        
        raise ValueError(f"Nó da AST desconhecido: {etype}")

# Ambiente de Execução
class VirtualMachine:
    def __init__(self):
        # Ambiente para armazenar variáveis e temporários
        self.env = {}

    def execute(self, ic_list):
        """ Passo 6/8: Executa a estrutura de código intermediária [cite: 427, 432] """

        last_result = None
        
        for instruction in ic_list:
            op, arg1, arg2, result = instruction
            
            # Se for um nome, busca no env. Se for um número, usa direto.
            val1 = self.env.get(arg1, arg1) if isinstance(arg1, str) else arg1
            val2 = self.env.get(arg2, arg2) if isinstance(arg2, str) else arg2
            
            # Traduz a instrução para a execução
            if op == '+': self.env[result] = val1 + val2
            elif op == '-': self.env[result] = val1 - val2
            elif op == '*': self.env[result] = val1 * val2
            elif op == '/': self.env[result] = val1 / val2
            elif op == 'div': self.env[result] = val1 // val2
            elif op == 'mod': self.env[result] = val1 % val2
            elif op == 'exp': self.env[result] = val1 ** val2
            elif op == '<': self.env[result] = val1 < val2
            elif op == '>': self.env[result] = val1 > val2
            elif op == '<=': self.env[result] = val1 <= val2
            elif op == '>=': self.env[result] = val1 >= val2
            elif op == '=': self.env[result] = val1 == val2
            elif op == '!=': self.env[result] = val1 != val2
            
            last_result = self.env[result]
            
        return last_result


# Loop principal 
print("Compilador LISP-like para Código Intermediário")
print("Exemplo: (+ (* 10 2) (- 30 5))")

while True:
    try:
        s = input("lisp> ")
    except EOFError:
        break
    if not s:
        continue
    
    # 1. Parsing -> AST 
    ast = parser.parse(s)
    if not ast:
        continue
    print(f"\nAST Gerada:\n{ast}\n")
    
    # Compilação p/ código intermediário
    compiler = Compiler()
    try:
        # Retorna o nome do último temporário
        compiler.generate_code(ast)
        ic_code = compiler.intermediate_code

        # Descarregador do código intermediário 
        print("Código Intermediário (Quádruplas):")  
        for line in ic_code:
            print(f"  {line}")
        print()

        # Execução p/ resultado final 
        vm = VirtualMachine()
        final_result = vm.execute(ic_code)
        print(f"Resultado (VM):\n{final_result}\n")
        
    except Exception as e:
        print(f"Erro no runtime: {e}")
