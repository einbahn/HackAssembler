def openfile(filename):
    import re
    lines = []
    with open(filename) as f:
        for line in f:
            if not line.startswith((r'//', '\n')):
                line = line.lstrip()
                line = re.sub(r'\s+.*', '', line)
                lines.append(line)
    return lines


def command_type(line):
    if line.startswith('@'):
        return 'A'
    elif line.startswith('('):
        return 'L'
    else:
        return 'C'


def parse_c_fields(c_instruction):
    if ';' in c_instruction:
        lhs, jmp = c_instruction.split(';')
        if '=' in lhs:
            dest, comp = lhs.split('=')
        else:
            dest = 'null'
            comp = lhs
    else:
        jmp = 'null'
        if '=' in c_instruction:
            dest, comp = c_instruction.split('=')
        else:
            dest = 'null'
            comp = c_instruction
    return [dest, comp, jmp]


def code_a(a_instruction, symbols):
    try:
        int_a = int(a_instruction[1::])
    except:
        int_a = symbols[a_instruction[1::]]
    return bin(int_a)[2::].zfill(16) + '\n'


def mksymbols(plines):
    symboltable = {
        'SP': 0,
        'LCL': 1,
        'ARG': 2,
        'THIS': 3,
        'THAT': 4,
        'R0': 0,
        'R1': 1,
        'R2': 2,
        'R3': 3,
        'R4': 4,
        'R5': 5,
        'R6': 6,
        'R7': 7,
        'R8': 8,
        'R9': 9,
        'R10': 10,
        'R11': 11,
        'R12': 12,
        'R13': 13,
        'R14': 14,
        'R15': 15,
        'SCREEN': 16384,
        'KBD': 24576
    }
    for i in range(2):
        if i == 0:
            lineno = 0
            # process labels only
            for line in plines:
                if line.startswith('('):
                    label = line[1:-1]
                    symboltable[label] = lineno
                else:
                    lineno += 1
        else:
            # process variables
            memptr = 16
            for line in plines:
                if line.startswith('@'):
                    var = line.replace('@', '')
                    try:
                        int(var)
                    except ValueError:
                        if var not in symboltable:
                            symboltable[var] = memptr
                            memptr += 1
    return symboltable


dest_table = {
    'null': '000',
    'M': '001',
    'D': '010',
    'MD': '011',
    'A': '100',
    'AM': '101',
    'AD': '110',
    'AMD': '111'
}

jmp_table = {
    'null': '000',
    'JGT': '001',
    'JEQ': '010',
    'JGE': '011',
    'JLT': '100',
    'JNE': '101',
    'JLE': '110',
    'JMP': '111'
}

comp_ad_table = {
    '0': '101010',
    '1': '111111',
    '-1': '111010',
    'D': '001100',
    'A': '110000',
    '!D': '001101',
    '!A': '110001',
    '-D': '001111',
    '-A': '110011',
    'D+1': '011111',
    'A+1': '110111',
    'D-1': '001110',
    'A-1': '110010',
    'D+A': '000010',
    'D-A': '010011',
    'A-D': '000111',
    'D&A': '000000',
    'D|A': '010101'
}

comp_m_table = {
    'M':   '110000',
    '!M':  '110001',
    '-m':  '110011',
    'M+1': '110111',
    'M-1': '110010',
    'D+M': '000010',
    'D-M': '010011',
    'M-D': '000111',
    'D&M': '000000',
    'D|M': '010101',
}


def code_c(c_instruction):
    dest, comp, jmp = c_instruction
    if comp in comp_ad_table:
        abit = '1110'
        comp_out = comp_ad_table[comp]
    else:
        abit = '1111'
        comp_out = comp_m_table[comp]
    return abit + comp_out + dest_table[dest] + jmp_table[jmp] + '\n'


if __name__ == "__main__":
    import sys
    import os
    inputlines = openfile(sys.argv[1])
    ofile = os.path.basename(sys.argv[1]).replace('.asm', '.hack')
    symbols = mksymbols(inputlines)
    with open(ofile, 'w') as output_file:
        for i in inputlines:
            if command_type(i) == 'A':
                output_file.write(code_a(i, symbols))
            elif command_type(i) == 'C':
                flds = parse_c_fields(i)
                output_file.write(code_c(flds))
