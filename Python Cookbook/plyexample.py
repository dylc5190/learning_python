# plyexample.py
#
# Example of parsing with PLY

from ply.lex import lex
from ply.yacc import yacc

# Token list
tokens = [ 'NUM', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LPAREN', 'RPAREN' ]

# Ignored characters

t_ignore = ' \t\n'

# Token specifications (as regexs)
t_PLUS   = r'\+'
t_MINUS  = r'-'
t_TIMES  = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'

# Token processing functions
def t_NUM(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Error handler
def t_error(t):
    print('Bad character: {!r}'.format(t.value[0]))
    t.skip(1)

# Build the lexer
lexer = lex()

# Grammar rules and handler functions
def print_name_and_args(name,yp):
    print(name)
    for i,p in enumerate(yp):
        print("  {}: {}".format(i,p))

def p_expr(yp):
    '''
    expr : expr PLUS term
         | expr MINUS term
    '''
    print_name_and_args(p_expr.__name__,yp)
    if yp[2] == '+':
        yp[0] = yp[1] + yp[3]
    elif yp[2] == '-':
        yp[0] = yp[1] - yp[3]

def p_expr_term(yp):
    '''
    expr : term
    '''
    print_name_and_args(p_expr_term.__name__,yp)
    yp[0] = yp[1]

def p_term(yp):
    '''
    term : term TIMES factor
         | term DIVIDE factor
    '''
    print_name_and_args(p_term.__name__,yp)
    if yp[2] == '*':
        yp[0] = yp[1] * yp[3]
    elif yp[2] == '/':
        yp[0] = yp[1] / yp[3]

def p_term_factor(yp):
    '''
    term : factor
    '''
    print_name_and_args(p_term_factor.__name__,yp)
    yp[0] = yp[1]

def p_factor(yp):
    '''
    factor : NUM
    '''
    print_name_and_args(p_factor.__name__,yp)
    yp[0] = yp[1]

def p_factor_group(yp):
    '''
    factor : LPAREN expr RPAREN
    '''
    print_name_and_args(p_factor_group.__name__,yp)
    yp[0] = yp[2]

def p_error(yp):
    print('Syntax error')

parser = yacc()

if __name__ == '__main__':
    #print(parser.parse('2'))
    #print(parser.parse('2+3'))
    expr = '2+(3+4)*5'
    print(expr)
    print(parser.parse(expr))
