#!/usr/bin/python3

"""
Retro Basic Compiler
Author: Phon Chitnelawong
"""

import sys
import string

if len(sys.argv) != 3:
    print('usage: ./retroc.py [source_file] [output_file]')
    sys.exit(1)

src_file = open(sys.argv[1], 'r')
out_file = open(sys.argv[2], 'w')

symbol_table = {
        'id': set(string.ascii_uppercase),
        'const': set([str(i) for i in range(0, 101)]),
        'line_num': set([str(i) for i in range(1, 1001)]),
        'goto': set(['GOTO']),
        'stop': set(['STOP']),
        'if': set(['IF']),
        'print': set(['PRINT']),
        '+': set(['+']),
        '-': set(['-']),
        '<': set(['<']),
        '=': set(['='])
        }

bcode_table = {
        'line_num': '10',
        'id': '11',
        'const': '12',
        'if': '13',
        'goto': '14',
        'print': '15',
        'stop': '16',
        '+': '17',
        '-': '17',
        '<': '17',
        '=': '17',
        }

def bcode_tuple(typ, token):
    ret = [bcode_table[typ]]
    if typ == 'line_num' or typ == 'const':
        ret.append(token)
    elif typ == 'id':
        ret.append(str(ord(token) - ord('A') + 1))
    elif typ == 'if' or typ == 'print' or typ == 'stop':
        ret.append('0')
    else:
        if token == '+':
            ret.append('1')
        elif token == '-':
            ret.append('2')
        elif token == '<':
            ret.append('3')
        elif token == '=':
            ret.append('4')
    return ret

def terminal_type(t):
    ret = []
    for typ, s in symbol_table.items():
        if t in s:
            ret.append(typ)
    return ret

def is_terminal(t):
    return type(t) is str or t == EOF

EOF = -1
PGM = 0
LINE = 1
STMT = 2
ASGMNT = 3
IF = 4
PRINT = 5
GOTO = 6
STOP = 7
EXP = 8
TERM = 9
EXP2 = 10
COND = 11
COND2 = 12
PRINT = 13

rules = [
        [PGM, [LINE, PGM]],
        [PGM, [EOF]], 
        [LINE, ['line_num', STMT]],
        [STMT, [ASGMNT]],
        [STMT, [IF]],
        [STMT, [PRINT]],
        [STMT, [GOTO]],
        [STMT, [STOP]],
        [ASGMNT, ['id','=',EXP]],
        [EXP, [TERM,EXP2]],
        [EXP2, ['+',TERM]],
        [EXP2, ['-',TERM]],
        [TERM, ['id']],
        [TERM, ['const']],
        [IF, ['if',COND,'line_num']],
        [COND, [TERM,COND2]],
        [COND2, ['<',TERM]],
        [COND2, ['=',TERM]],
        [PRINT, ['print','id']],
        [GOTO, ['goto','line_num']],
        [STOP, ['stop']],
        [EXP2, ['']]
        ]

parsing_table = {
        'if': {4, 14},
        'print': {5, 18},
        'goto': {6, 19},
        'stop': {7, 20},
        'id': {3, 8, 9, 12, 15},
        'const': {9, 13, 15},
        'line_num': {0, 2, 9},
        '+': {10},
        '-': {11},
        '<': {16},
        '=': {17},
        EOF: {1, 9}
        }

def quit(status):
    src_file.close()
    out_file.close()
    sys.exit(status)

line = 'init'
output = []
ll_stack = [EOF, PGM]
line_num = 0
while len(line) != 0:
    line = src_file.readline()
    line_num += 1
    output.append([])
    tokens = line.strip().split()
    token_index = 0
    while token_index < len(tokens):
        token = tokens[token_index]
        term_types = terminal_type(token)
        top = ll_stack[-1]
        if len(term_types) == 0:
            print('error: unrecognized symbol `' + str(token) + "' at line", line_num, file=sys.stderr)
            quit(1)
        typ = term_types[0]
        if_goto = False
        raw = False
        if 'line_num' in term_types:
            if token_index == 0:
                typ = 'line_num'
            elif token_index == len(tokens) - 1 and len(tokens) > 2:
                if tokens[1] == 'GOTO':
                    typ = 'line_num'
                    raw = True
                if tokens[1] == 'IF':
                    typ = 'line_num'
                    if_goto = True

        if is_terminal(top):
            if typ == top: # token matches
                if if_goto:
                    output[line_num - 1] += [bcode_table['goto'], token]
                elif raw:
                    output[line_num - 1] += [token]
                else:
                    output[line_num - 1] += bcode_tuple(typ, token)
                token_index += 1
                ll_stack.pop()
            else:
                print('error: expected', top, 'at line', line_num, file=sys.stderr)
                quit(1)
        else:
            accept = False
            for rule_id in parsing_table[typ]:
                if rules[rule_id][0] == top:
                    ll_stack.pop()
                    ll_stack += rules[rule_id][1][::-1]
                    accept = True
                    break
            if not accept:
                for rule in rules:
                    if rule[0] == top:
                        if rule[1][0] == '':
                            accept = True
                            ll_stack.pop()
                            break
            if not accept:
                print('error: unexpected token `' + token + "' at line", line_num, file=sys.stderr)
                quit(1)

for out in output:
    if len(out) > 0:
        out_file.write(' '.join(out))
        out_file.write('\n')
out_file.write('0')
