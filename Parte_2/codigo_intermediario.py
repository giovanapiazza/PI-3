# compiler_ply_optionB_ast_dict_irA.py
import ply.lex as lex
import ply.yacc as yacc
import json
import sys

# LÉXICO
reserved = {
    'defun': 'DEFUN',
    'if': 'IF',
    'cond': 'COND',
    'car': 'CAR',
    'cdr': 'CDR',
    'cons': 'CONS',
    'eq': 'EQ',
    'nil': 'NIL',
    't': 'T',
    'div': 'DIVINT',
    'mod': 'MOD',
    'exp': 'EXP',
}

tokens = [
    'LPAREN', 'RPAREN', 'QUOTE', 'NUMBER', 'ID',
    'PLUS', 'MINUS', 'TIMES', 'DIV',
    'LT', 'GT', 'LE', 'GE', 'EQ_OP', 'NE',
] + list(reserved.values())

t_LPAREN = r'\('
t_RPAREN = r'\)'
t_QUOTE = r'\''
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIV = r'/'

# tokens relacionais
t_LE = r'<='
t_GE = r'>='
t_NE = r'!='
t_LT = r'<'
t_GT = r'>'
t_EQ_OP = r'='

t_ignore = " \t\r\n"

def t_COMMENT(t):
    r'\;.*'
    pass 

def t_DEFUN(t):
    r'\bdefun\b'
    t.type = 'DEFUN'
    return t

def t_IF(t):
    r'\bif\b'
    t.type = 'IF'
    return t

def t_CONS(t):
    r'\bcons\b'
    t.type = 'CONS'
    return t

def t_car(t):
    r'\bcar\b'
    t.type = 'CAR'
    return t

def t_cdr(t):
    r'\bcdr\b'
    t.type = 'CDR'
    return t

def t_EQ(t):
    r'\beq\b'
    t.type = 'EQ'
    return t

def t_NIL(t):
    r'\bnil\b'
    t.type = 'NIL'
    return t

def t_NUMBER(t):
    r'0|([1-9][0-9]*)'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    # se for palavra reservada, mapeia antes
    if t.value in reserved:
        t.type = reserved[t.value]
    return t

def t_error(t):
    print(f"Caractere inválido: {t.value[0]!r}")
    t.lexer.skip(1)

# PARSER
precedence = ()

def p_program(p):
    '''program : expr_list'''
    # p[1] é uma lista de nós AST
    ast = p[1]

    # Análise semântica, executada dentro do parser
    semantic_errors = []
    functions = collect_defuns(ast)

    # checa funções duplicadas
    duplicates = [name for name in functions if list(functions.keys()).count(name) > 1]
    for d in set(duplicates):
        semantic_errors.append(f"Função duplicada: {d}")

    # analisa cada expressão de nível superior
    for node in ast:
        semantic_analyze_node(node, functions, {}, semantic_errors)

    if semantic_errors:
        print("\n=== ERROS SEMÂNTICOS ===")
        for e in semantic_errors:
            print(" -", e)
        print("\nAbortando geração de código devido a erros semânticos.")
        p[0] = {"type": "program", "ast": ast, "sem_ok": False, "errors": semantic_errors}
        return

    print("\n=== SEMÂNTICA OK ===")
    print("Funções detectadas:")
    for fn_name, info in functions.items():
        print(f" - {fn_name}({', '.join(info['params'])})")

    # Geração de código intermediário (3-endereços)
    ir_lines = []
    # Mapa de funções para o gerador
    global_codegen_setup(functions)

    for node in ast:
        lines, res = gen_code(node, {})
        if lines:
            ir_lines.extend(lines)

    print("\n=== CÓDIGO INTERMEDIÁRIO (3-endereços) ===")
    for l in ir_lines:
        print(l)

    p[0] = {"type": "program", "ast": ast, "sem_ok": True, "ir": ir_lines}

def p_expr_list(p):
    '''expr_list : expr expr_list
                 | expr'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_expr_atom(p):
    '''expr : atom'''
    p[0] = p[1]

def p_expr_listnode(p):
    '''expr : list'''
    p[0] = p[1]

# Atom 
def p_atom_number(p):
    'atom : NUMBER'
    p[0] = {"type": "number", "value": p[1]}

def p_atom_id_or_token(p):
    '''atom : ID
            | PLUS
            | MINUS
            | TIMES
            | DIV
            | LT
            | GT
            | LE
            | GE
            | EQ_OP
            | NE
            | DEFUN
            | IF
            | COND
            | CAR
            | CDR
            | CONS
            | EQ
            | NIL
            | T
            | DIVINT
            | MOD
            | EXP'''
    # mantém tipo de token e lexema
    p[0] = {"type": "symbol", "token": p.slice[1].type, "lexeme": p[1]}

def p_empty(p):
    'empty :'
    p[0] = None

# Lista Constructas
def p_list_empty(p):
    'list : LPAREN RPAREN'
    p[0] = {"type": "nil"}

def p_list_if(p):
    '''list : LPAREN IF expr expr expr RPAREN
            | LPAREN IF expr expr RPAREN'''
    if len(p) == 7:
        # (if cond then else)
        p[0] = {"type": "if", "cond": p[3], "then": p[4], "else": p[5]}
    else:
        # (if cond then) -> else implícito nil
        p[0] = {"type": "if", "cond": p[3], "then": p[4], "else": {"type": "nil"}}

def p_list_defun(p):
    'list : LPAREN DEFUN ID LPAREN param_list RPAREN expr RPAREN'
    # (defun <id> (<params>) <body>)
    p[0] = {"type": "defun", "name": p[3], "params": p[5], "body": p[7]}

def p_param_list(p):
    '''param_list : ID param_list
                  | ID
                  | empty'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    elif len(p) == 2 and p[1] is not None:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_list_application(p):
    'list : LPAREN elements RPAREN'
    # elements é uma lista python: primeiro é operador, resto são args
    elems = p[2]
    operator = elems[0]
    args = elems[1:]
    p[0] = {"type": "application", "operator": operator, "args": args}

def p_elements(p):
    '''elements : expr elements
                | expr'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_error(p):
    if p:
        print(f"Erro de sintaxe: token inesperado '{p.value}' (tipo {p.type})")
    else:
        print("Erro de sintaxe: EOF inesperado")
        
        
# ANÁLISE SEMÂNTICA (funções auxiliares)
# tipos simples: 'number', 'list', 'any'
builtin_arith_tokens = {'PLUS','MINUS','TIMES','DIV'}
builtin_comp_tokens = {'LT','GT','LE','GE','EQ_OP','NE'}
builtin_names = {
    'cons': 'CONS', 'car': 'CAR', 'cdr': 'CDR', 'eq': 'EQ'
}

def collect_defuns(ast):
    """Retorna dict: nome -> {'params': [...], 'body': node}"""
    funcs = {}
    for node in ast:
        if isinstance(node, dict) and node.get("type") == "defun":
            name = node["name"]
            params = node["params"]
            body = node["body"]
            funcs[name] = {"params": params, "body": body}
    return funcs

def semantic_analyze_node(node, functions, env, errors):
    """
    node: nó AST (dict)
    functions: dict de defuns
    env: mapeamento var->tipo (parâmetros locais)
    errors: lista para armazenar mensagens
    retorna: tipo inferido: 'number'|'list'|'any'
    """
    if not isinstance(node, dict):
        return 'any'

    ntype = node.get("type")

    if ntype == "number":
        return 'number'
    if ntype == "nil":
        return 'list'
    if ntype == "symbol":
        tok = node.get("token")
        # uso de símbolo como identificador
        if tok == 'ID':
            name = node.get("lexeme")
            if name in env:
                return env[name] or 'any'
            else:
                errors.append(f"Variável não declarada: {name}")
                return 'any'
        # outros tokens usados como átomos -> tipo genérico
        return 'any'

    if ntype == "defun":
        name = node["name"]
        params = node["params"]
        body = node["body"]
        # ambiente local: parâmetros são any
        local_env = {p: 'any' for p in params}
        semantic_analyze_node(body, functions, local_env, errors)
        return 'any'

    if ntype == "if":
        semantic_analyze_node(node["cond"], functions, env, errors)
        t_then = semantic_analyze_node(node["then"], functions, env, errors)
        t_else = semantic_analyze_node(node["else"], functions, env, errors)
        if t_then == t_else:
            return t_then
        return 'any'

    if ntype == "application":
        op_node = node["operator"]
        args = node["args"]

        # operador deve ser símbolo
        if not isinstance(op_node, dict) or op_node.get("type") != "symbol":
            errors.append("Operador inválido em aplicação")
            for a in args:
                semantic_analyze_node(a, functions, env, errors)
            return 'any'

        optoken = op_node.get("token")
        oplex = op_node.get("lexeme")

        # função definida pelo usuário
        if optoken == 'ID' and oplex in functions:
            expected = len(functions[oplex]['params'])
            got = len(args)
            if expected != got:
                errors.append(f"Chamada de '{oplex}' com aridade incorreta: esperado {expected}, obteve {got}")
            for a in args:
                semantic_analyze_node(a, functions, env, errors)
            return 'any'

        # built-ins aritméticos
        if optoken in builtin_arith_tokens:
            if len(args) != 2:
                errors.append(f"Operador aritmético '{oplex}' precisa de 2 argumentos (recebeu {len(args)})")
            t1 = semantic_analyze_node(args[0], functions, env, errors) if len(args) >= 1 else 'any'
            t2 = semantic_analyze_node(args[1], functions, env, errors) if len(args) >= 2 else 'any'
            if t1 not in ('number','any'):
                errors.append(f"Operador '{oplex}' espera número no 1º argumento")
            if t2 not in ('number','any'):
                errors.append(f"Operador '{oplex}' espera número no 2º argumento")
            return 'number'

        if optoken in builtin_comp_tokens:
            if len(args) != 2:
                errors.append(f"Operador de comparação '{oplex}' precisa de 2 argumentos")
            semantic_analyze_node(args[0], functions, env, errors)
            semantic_analyze_node(args[1], functions, env, errors)
            return 'any'

        # cons, car, cdr, eq
        if optoken == 'CONS' or (optoken == 'ID' and oplex == 'cons'):
            if len(args) != 2:
                errors.append(f"cons precisa de 2 argumentos")
            semantic_analyze_node(args[0], functions, env, errors)
            semantic_analyze_node(args[1], functions, env, errors)
            return 'list'

        if optoken == 'CAR' or (optoken == 'ID' and oplex == 'car'):
            if len(args) != 1:
                errors.append("car precisa de 1 argumento")
            t = semantic_analyze_node(args[0], functions, env, errors)
            if t not in ('list','any'):
                errors.append("car espera uma lista no argumento")
            return 'any'

        if optoken == 'CDR' or (optoken == 'ID' and oplex == 'cdr'):
            if len(args) != 1:
                errors.append("cdr precisa de 1 argumento")
            t = semantic_analyze_node(args[0], functions, env, errors)
            if t not in ('list','any'):
                errors.append("cdr espera uma lista no argumento")
            return 'list'

        if optoken == 'EQ' or (optoken == 'ID' and oplex == 'eq'):
            if len(args) != 2:
                errors.append("eq precisa de 2 argumentos")
            semantic_analyze_node(args[0], functions, env, errors)
            semantic_analyze_node(args[1], functions, env, errors)
            return 'any'

        # operador é ID mas não é função definida
        if optoken == 'ID':
            if oplex not in functions:
                errors.append(f"Função não definida: {oplex}")
                for a in args:
                    semantic_analyze_node(a, functions, env, errors)
                return 'any'

        # fallback
        for a in args:
            semantic_analyze_node(a, functions, env, errors)
        return 'any'

    return 'any'

# GERAÇÃO DE CÓDIGO INTERMEDIÁRIO (3-endereços)
_temp_counter = 0
_label_counter = 0
_codegen_functions = {}

def reset_codegen():
    global _temp_counter, _label_counter
    _temp_counter = 0
    _label_counter = 0

def new_temp():
    global _temp_counter
    name = f"t{_temp_counter}"
    _temp_counter += 1
    return name

def new_label():
    global _label_counter
    name = f"L{_label_counter}"
    _label_counter += 1
    return name

def global_codegen_setup(functions):
    """Prepara tabela de funções para geração de código; reinicia contadores."""
    reset_codegen()
    global _codegen_functions
    _codegen_functions = {}
    for name, info in functions.items():
        _codegen_functions[name] = (info['params'], info['body'])

def gen_code(node, env):
    """
    node: nó AST
    env: ambiente mapeando variáveis para temporários ou nomes
    retorna: (lista_de_linhas_IR, temp_resultante)
    """
    if not isinstance(node, dict):
        return ([], None)

    ntype = node.get("type")

    if ntype == "number":
        t = new_temp()
        return ([f"{t} = {node['value']}"], t)

    if ntype == "nil":
        t = new_temp()
        return ([f"{t} = NIL"], t)

    if ntype == "symbol":
        tok = node.get("token")
        lexeme = node.get("lexeme")
        if tok == 'ID':
            if lexeme in env:
                return ([], env[lexeme])
            else:
                t = new_temp()
                return ([f"{t} = {lexeme}"], t)
        else:
            t = new_temp()
            return ([f"{t} = {lexeme}"], t)

    if ntype == "defun":
        # gera bloco da função
        name = node["name"]
        params = node["params"]
        body = node["body"]

        lines = [f"# função {name}:"]
        entry = f"func_{name}"
        lines.append(f"{entry}:")
        local_env = {}
        for p in params:
            local_env[p] = p
            lines.append(f"# param {p}")

        body_lines, body_temp = gen_code(body, local_env)
        lines.extend(body_lines)
        if body_temp:
            lines.append(f"return {body_temp}")
        else:
            lines.append("return NIL")
        return (lines, None)

    if ntype == "if":
        cond = node["cond"]
        then_node = node["then"]
        else_node = node["else"]

        code = []
        cond_code, cond_temp = gen_code(cond, env)
        code.extend(cond_code)

        L_true = new_label()
        L_false = new_label()
        L_end = new_label()

        code.append(f"if {cond_temp} goto {L_true}")
        code.append(f"goto {L_false}")

        # then
        code.append(f"{L_true}:")
        then_code, then_temp = gen_code(then_node, env)
        code.extend(then_code)
        res_temp = new_temp()
        if then_temp:
            code.append(f"{res_temp} = {then_temp}")
        else:
            code.append(f"{res_temp} = NIL")
        code.append(f"goto {L_end}")

        # else
        code.append(f"{L_false}:")
        else_code, else_temp = gen_code(else_node, env)
        code.extend(else_code)
        if else_temp:
            code.append(f"{res_temp} = {else_temp}")
        else:
            code.append(f"{res_temp} = NIL")

        code.append(f"{L_end}:")
        return (code, res_temp)

    if ntype == "application":
        op_node = node["operator"]
        args = node["args"]

        if not isinstance(op_node, dict) or op_node.get("type") != "symbol":
            return (["# erro: operador inválido"], None)

        optoken = op_node.get("token")
        oplex = op_node.get("lexeme")

        # chamada de função definida pelo usuário
        if optoken == 'ID' and oplex in _codegen_functions:
            params, body = _codegen_functions[oplex]
            code = []
            arg_temps = []
            for a in args:
                a_code, a_temp = gen_code(a, env)
                code.extend(a_code)
                arg_temps.append(a_temp)
            for p, at in zip(params, arg_temps):
                code.append(f"{p} = {at}  # param")
            local_env = {p: p for p in params}
            body_lines, body_temp = gen_code(body, local_env)
            code.extend(body_lines)
            res = new_temp()
            if body_temp:
                code.append(f"{res} = {body_temp}  # resultado {oplex}")
            else:
                code.append(f"{res} = NIL  # resultado {oplex}")
            return (code, res)

        # built-ins aritméticos
        if optoken in {'PLUS','MINUS','TIMES','DIV'}:
            code = []
            left_code, left_temp = gen_code(args[0], env)
            right_code, right_temp = gen_code(args[1], env)
            code.extend(left_code)
            code.extend(right_code)
            res = new_temp()
            op_symbol = op_node.get("lexeme") or op_token_to_symbol(optoken)
            code.append(f"{res} = {left_temp} {op_symbol} {right_temp}")
            return (code, res)

        # comparações
        if optoken in {'LT','GT','LE','GE','EQ_OP','NE'}:
            code = []
            left_code, left_temp = gen_code(args[0], env)
            right_code, right_temp = gen_code(args[1], env)
            code.extend(left_code); code.extend(right_code)
            res = new_temp()
            op_symbol = op_node.get("lexeme") or op_token_to_symbol(optoken)
            code.append(f"{res} = {left_temp} {op_symbol} {right_temp}")
            return (code, res)

        # cons, car, cdr, eq
        if optoken == 'CONS' or (optoken == 'ID' and oplex == 'cons'):
            code = []
            a1_code, a1_temp = gen_code(args[0], env)
            a2_code, a2_temp = gen_code(args[1], env)
            code.extend(a1_code); code.extend(a2_code)
            res = new_temp()
            code.append(f"{res} = CONS({a1_temp}, {a2_temp})")
            return (code, res)

        if optoken == 'CAR' or (optoken == 'ID' and oplex == 'car'):
            code = []
            a_code, a_temp = gen_code(args[0], env)
            code.extend(a_code)
            res = new_temp()
            code.append(f"{res} = CAR({a_temp})")
            return (code, res)

        if optoken == 'CDR' or (optoken == 'ID' and oplex == 'cdr'):
            code = []
            a_code, a_temp = gen_code(args[0], env)
            code.extend(a_code)
            res = new_temp()
            code.append(f"{res} = CDR({a_temp})")
            return (code, res)

        if optoken == 'EQ' or (optoken == 'ID' and oplex == 'eq'):
            code = []
            a1_code, a1_temp = gen_code(args[0], env)
            a2_code, a2_temp = gen_code(args[1], env)
            code.extend(a1_code); code.extend(a2_code)
            res = new_temp()
            code.append(f"{res} = EQ({a1_temp}, {a2_temp})")
            return (code, res)

        # chamada de função não reconhecida
        if optoken == 'ID':
            code = []
            arg_temps = []
            for a in args:
                a_code, a_temp = gen_code(a, env)
                code.extend(a_code)
                arg_temps.append(a_temp)
            res = new_temp()
            code.append(f"{res} = CALL({oplex}, {', '.join(arg_temps)})")
            return (code, res)

        # fallback
        code = []
        arg_temps = []
        for a in args:
            a_code, a_temp = gen_code(a, env)
            code.extend(a_code)
            arg_temps.append(a_temp)
        res = new_temp()
        code.append(f"{res} = CALL({oplex}, {', '.join(arg_temps)})")
        return (code, res)

    return (["# Nó desconhecido para geração de código"], None)

def op_token_to_symbol(tok):
    mapping = {
        'PLUS': '+', 'MINUS': '-', 'TIMES': '*', 'DIV': '/',
        'LT':'<','GT':'>','LE':'<=','GE':'>=','EQ_OP':'=','NE':'!='
    }
    return mapping.get(tok, tok)

# dados de teste
if __name__ == "__main__":
    lexer = lex.lex()
    parser = yacc.yacc()

    data = """
    (defun soma (x y)
        (+ x y))

    (if (> 5 2)
        (soma 3 4)
        0)
    """

    print("=== INPUT ===")
    print(data)

    print("\n=== TOKENS ===")
    lexer.input(data)
    for tok in lexer:
        print(tok)

    print("\n=== PARSE & PROCESS (AST + SEMÂNTICA + IR) ===")
    result = parser.parse(data)

    if isinstance(result, dict):
        if not result.get("sem_ok"):
            print("\nProcessamento interrompido por erros semânticos.")
        else:
            print("\nProcessamento concluído com sucesso.")
