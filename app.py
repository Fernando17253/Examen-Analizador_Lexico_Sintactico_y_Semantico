from flask import Flask, render_template, request, jsonify
import ply.lex as lex
import ply.yacc as yacc

app = Flask(__name__)

# Lista de palabras reservadas y tipos
reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR',
    'int': 'INT',
    'return': 'RETURN',
    'printf': 'PRINTF',
    'main': 'MAIN'
}

tokens = [
    'ID', 'NUMBER',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'EQ', 'SEMI', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'COMMA', 'INCLUDE', 'HEADER'
] + list(reserved.values())

# Reglas regulares para tokens simples
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_EQ      = r'='
t_SEMI    = r';'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LBRACE  = r'\{'
t_RBRACE  = r'\}'
t_COMMA   = r','

def t_INCLUDE(t):
    r'\#include'
    return t

def t_HEADER(t):
    r'<[a-zA-Z_][a-zA-Z_0-9]*\.h>'
    t.value = t.value[1:-1]  # Remover los caracteres '<' y '>'
    return t

# Reglas regulares con acciones
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')    # Chequea palabras reservadas
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Ignorar espacios y tabulaciones
t_ignore  = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

# Construir el lexer
lexer = lex.lex()

# Definir la precedencia de operadores
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)

# Definir la gramática
def p_program(p):
    '''program : includes functions
               | includes
               | functions'''
    if len(p) == 3:
        p[0] = ('program', p[1], p[2])
    else:
        p[0] = ('program', p[1])

def p_includes(p):
    '''includes : includes include
                | include'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_include(p):
    '''include : INCLUDE HEADER'''
    p[0] = ('include', p[1], p[2])

def p_functions(p):
    '''functions : functions function
                 | function'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_function(p):
    '''function : type ID LPAREN RPAREN LBRACE statements RBRACE'''
    p[0] = ('function', p[1], p[2], p[6])

def p_type(p):
    '''type : INT'''
    p[0] = p[1]

def p_statements(p):
    '''statements : statements statement
                  | statement'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_statement(p):
    '''statement : declaration
                 | assignment
                 | loop
                 | RETURN expression SEMI'''
    p[0] = p[1]

def p_declaration(p):
    '''declaration : type ID EQ expression SEMI'''
    p[0] = ('declaration', p[1], p[2], p[4])

def p_assignment(p):
    '''assignment : ID EQ expression SEMI'''
    p[0] = ('assignment', p[1], p[3])

def p_loop(p):
    '''loop : FOR LPAREN assignment expression SEMI assignment RPAREN LBRACE statements RBRACE'''
    p[0] = ('loop', p[3], p[4], p[6], p[9])

def p_expression(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | NUMBER
                  | ID'''
    if len(p) == 4:
        p[0] = ('expression', p[1], p[2], p[3])
    else:
        p[0] = p[1]

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}'")
    else:
        print("Syntax error at EOF")

parser = yacc.yacc()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analizar', methods=['POST'])
def analizar():
    datos_recibidos = request.json['codigo']
    tokens_analizados = []

    lexer.input(datos_recibidos)

    for token in lexer:
        tokens_analizados.append({'valor': token.value, 'tipo': token.type})

    return jsonify(tokens_analizados)

@app.route('/analizarSintactico', methods=['POST'])
def analizar_sintactico():
    datos_recibidos = request.json['codigo']
    try:
        parser.parse(datos_recibidos)
        return jsonify({'resultado': 'La estructura es correcta'})
    except Exception as e:
        return jsonify({'resultado': f'Error en la estructura: {str(e)}'})

@app.route('/analizarSemantico', methods=['POST'])
def analizar_semantico_route():
    datos_recibidos = request.json['codigo']
    resultado = analizar_semantico(datos_recibidos)
    return jsonify({'resultado': resultado})

def analizar_semantico(codigo):
    lexer.input(codigo)
    tokens = list(lexer)
    declaraciones = {}
    uso_variables = []

    tipo_actual = None

    for token in tokens:
        if token.type in ['INT', 'CHAR', 'FLOAT']:
            tipo_actual = token.type
        elif token.type == 'ID':
            if tipo_actual:
                declaraciones[token.value] = tipo_actual
                tipo_actual = None
            elif token.value not in declaraciones:
                return f"Análisis semántico incorrecto: variable '{token.value}' no declarada"
            uso_variables.append(token.value)
        elif token.type in reserved.values():
            tipo_actual = None

    return "Análisis semántico correcto"

if __name__ == '__main__':
    app.run(debug=True, port=8084)
