class Parser(object):
    def __init__(self, filename):
        import re
        self.lines = []
        with open(filename) as f:
            for line in f:
                if not line.startswith((r'//', '\n')):
                    line = line.lstrip()
                    line = re.sub(r'\s+.*', '', line)
                    self.lines.append(line)

    def commandtype(self, command):
        if command.startswith('@'):
            return 'A_COMMAND'
        elif command.startswith('('):
            return 'L_COMMAND'
        else:
            return 'C_COMMAND'

    def symbol(self, command, commandtype):
        if commandtype == 'A_COMMAND':
            return command[1:]
        elif commandtype == 'L_COMMAND':
            return command[1:-1]
        else:
            raise ValueError

    def dest(self, command):
        if self.commandtype(command) != 'C_COMMAND':
            raise ValueError
        if not '=' in command:
            return 'null'
        dest, _ = command.split('=')
        return dest

    def comp(self, command):
        if self.commandtype(command) != 'C_COMMAND':
            raise ValueError
        if ';' in command:
            lhs, _ = command.split(';')
            if '=' in lhs:
                _, compute = lhs.split('=')
            else:
                compute = lhs
        else:
            if '=' in command:
                _, compute = command.split('=')
            else:
                compute = command
        return compute

    def jump(self, command):
        if self.commandtype(command) != 'C_COMMAND':
            raise ValueError
        if not ';' in command:
            return 'null'
        _, jump = command.split(';')
        return jump


class SymbolTable(object):
    def __init__(self):
        self.symboltable = {
        'SP': '0',
        'LCL': '1',
        'ARG': '2',
        'THIS': '3',
        'THAT': '4',
        'R0': '0',
        'R1': '1',
        'R2': '2',
        'R3': '3',
        'R4': '4',
        'R5': '5',
        'R6': '6',
        'R7': '7',
        'R8': '8',
        'R9': '9',
        'R10': '10',
        'R11': '11',
        'R12': '12',
        'R13': '13',
        'R14': '14',
        'R15': '15',
        'SCREEN': '16384',
        'KBD': '24576'
    }

    def addentry(self, symbol, address):    
        self.symboltable[symbol] = str(address)

    def getaddress(self, symbol):
        return self.symboltable[symbol]

class Code(object):
    def __init__(self):
        self.dest = {
            'null': '000',
            'M': '001',
            'D': '010',
            'MD': '011',
            'A': '100',
            'AM': '101',
            'AD': '110',
            'AMD': '111'
        }
        self.jump = {
            'null': '000',
            'JGT': '001',
            'JEQ': '010',
            'JGE': '011',
            'JLT': '100',
            'JNE': '101',
            'JLE': '110',
            'JMP': '111'
        }
        self.compad = {
            '0':   '0101010',
            '1':   '0111111',
            '-1':  '0111010',
            'D':   '0001100',
            'A':   '0110000',
            '!D':  '0001101',
            '!A':  '0110001',
            '-D':  '0001111',
            '-A':  '0110011',
            'D+1': '0011111',
            'A+1': '0110111',
            'D-1': '0001110',
            'A-1': '0110010',
            'D+A': '0000010',
            'D-A': '0010011',
            'A-D': '0000111',
            'D&A': '0000000',
            'D|A': '0010101'
        }
        self.compm = {
            'M':   '1110000',
            '!M':  '1110001',
            '-m':  '1110011',
            'M+1': '1110111',
            'M-1': '1110010',
            'D+M': '1000010',
            'D-M': '1010011',
            'M-D': '1000111',
            'D&M': '1000000',
            'D|M': '1010101',
        }
        
    def destc(self, dest_mnemonic):
        return self.dest[dest_mnemonic]
    
    def compc(self, comp_mnemonic):
        if comp_mnemonic in self.compad:
            return self.compad[comp_mnemonic]
        else:
            return self.compm[comp_mnemonic]
    
    def jumpc(self, jump_mnemonic):
        return self.jump[jump_mnemonic]
    
    def acommand(self, address):
        return bin(int(address))[2::].zfill(16) + '\n'


if __name__ == "__main__":
    import sys 
    import os
    filename = sys.argv[1]
    p = Parser(filename)
    s = SymbolTable()

    #first pass: construct symbol table with labels only
    linenum = 0
    for line in p.lines:
        cmdtype = p.commandtype(line)
        if cmdtype == 'L_COMMAND':
            sym = p.symbol(line, cmdtype)
            s.addentry(sym, linenum)
        else:
            linenum += 1
    
    #second pass: construct rest of symbols
    memptr = 16
    for line in p.lines:
        cmdtype = p.commandtype(line)
        if cmdtype == 'A_COMMAND':
            var = p.symbol(line, cmdtype)
            try:
                int(var)
            except ValueError:
                if var not in s.symboltable:
                    s.addentry(var, memptr)
                    memptr += 1
    
    #translate into machine code
    c = Code()
    ofilename = os.path.basename(filename).replace('.asm', '.hack')
    with open(ofilename, 'w') as of:
        for line in p.lines:
            cmdtype = p.commandtype(line)
            if cmdtype == 'A_COMMAND':
                sym = p.symbol(line, cmdtype)
                try:
                    int(sym)
                    of.write(c.acommand(sym))
                except:
                    of.write(c.acommand(s.getaddress(sym)))
            elif cmdtype == 'C_COMMAND':
                dest = p.dest(line)
                comp = p.comp(line)
                jump = p.jump(line)
                destc = c.destc(dest)
                compc = c.compc(comp)
                jumpc = c.jumpc(jump)
                output = ''.join(('111', compc, destc, jumpc, '\n'))
                of.write(output)

