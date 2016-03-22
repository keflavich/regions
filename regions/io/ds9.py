from astropy import units as u
import os
import re
#from .. import circle
from regions import circle

from astropy.extern.ply import lex,yacc

tokens = (
    'NAME',
    'OPEN_PAREN',
    'CLOSE_PAREN',
    'COMMA',
    'SIGN',
    'SEXAGESIMAL',
    'POUND',
    'UINT',
    'UFLOAT',
    'UNIT'
)

t_OPEN_PAREN = r'\('
t_CLOSE_PAREN = r'\)'
t_COMMA = r','
t_POUND = r'\#'

# NOTE THE ORDERING OF THESE RULES IS IMPORTANT!!
# Regular expression rules for simple tokens
def t_NAME(t):
    r'[a-z]+'
    return t

def t_SEXAGESIMAL(t):
    r'[0-9]+:[0-9]+:[0-9\.]+'
    return t

def t_UFLOAT(t):
    r'((\d+\.?\d+)|(\.\d+))([eE][+-]?\d+)?'
    if not re.search(r'[eE\.]', t.value):
        t.type = 'UINT'
        t.value = int(t.value)
    else:
        t.value = float(t.value)
    return t

def t_UINT(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_SIGN(t):
    r'[+-](?=\d)'
    t.value = float(t.value + '1')
    return t

def t_UNIT(t):
    r'[°"\']'
    t.value = {'"': u.arcsec,
               "'": u.arcmin,
               "°": u.degree,}[t.value]
    return t

t_ignore = ''

# Error handling rule
def t_error(t):
    raise ValueError(
        "Invalid character at col {0}".format(t.lexpos))

lexer = lex.lex()
#optimize=True, lextab='ds9reg_lextab',
#                outputdir=os.path.dirname(__file__),
#                reflags=re.UNICODE)

names = {}
coordinates = []
def p_statement_assign(t):
    'statement : NAME coordinates'
    #print("statement assign:", t)
    #print("t[0]: {0}  t[1]: {1}".format(t[0], t[1]))
    names['name'] = t[1]
    t[0] = (t[1], t[2])

def p_coordinates_dosomething(t):
    'coordinates : OPEN_PAREN coordlist CLOSE_PAREN'
    #print('coordinates_dosomethign: ',t)
    #print("t[0]: {0}  t[1]: {1}".format(t[0], t[1]))
    t[0] = t[2]


def p_coordlist_split(t):
    'coordlist : coord COMMA coord COMMA size'
    #print('coordlsit_split: ',t)
    #print("t[0]: {0}  t[1]: {1}  t[2]: {2}".format(t[0], t[1], t[2]))
    t[0] = (t[1],t[3],t[5])

def p_coord_doot(t):
    '''coord : UINT
             | SEXAGESIMAL'''
    #print('coord_doot: ',t)
    #print("t[0]: {0}  t[1]: {1}".format(t[0], t[1], ))
    coordinates.append(t[1])
    t[0] = t[1]

def p_size_something(t):
    "size : UINT"
    #print('size_something: ',t)
    #print("t[0]: {0}  t[1]: {1}".format(t[0], t[1], ))
    coordinates.append(t[1])
    t[0] = t[1]


def p_error(t):
    print("Syntax error at '%s'" % t.value)

parser = yacc.yacc(optimize=True)

def parse(string):
    name, coordinates = parser.parse(string)
    return circle.CircularRegion(coordinates[:2], coordinates[2])
    #return names, coordinates
