import os
import sys


def trim(docstring):
    if not docstring:
        return ""
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return "\n".join(trimmed)


class Parser(object):
    def __init__(self, inputfile):
        self.file = open(inputfile)
        self.currentCommand = ""
        self.hasMoreCommands = True

    def advance(self):
        try:
            while True:
                self.currentCommand = self.file.readline()
                if self.currentCommand == "":
                    raise EOFError
                if not self.currentCommand.startswith((r"//", "\n")):
                    break
        except EOFError:
            self.hasMoreCommands = False

    def commandtype(self, command):
        if command.startswith("push"):
            return "C_PUSH"
        elif command.startswith("pop"):
            return "C_POP"
        elif command.startswith(
            ("add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not")
        ):
            return "C_ARITHMETIC"

    def arg1(self):
        return self.currentCommand.split(" ")[0].replace("\n", "")

    def arg2(self):
        if self.commandtype(self.currentCommand) in (
            "C_PUSH",
            "C_POP",
            "C_FUNCTION",
            "C_CALL",
        ):
            return [i.replace("\n", "") for i in self.currentCommand.split(" ")[1:]]

    def close(self):
        self.file.close()


class CodeWriter(object):
    def __init__(self, outputfile):
        self.file = open(outputfile, "w")
        self.labelcounter = 0
        self.filename = os.path.basename(outputfile).replace(".asm", "")

    def writeArithmetic(self, command):
        if command == "add":
            asm = """
            {}
            @SP
            M=M-1
            @SP
            A=M
            D=M
            @SP
            M=M-1
            @SP
            A=M
            M=D+M
            @SP
            M=M+1
            """
            self.file.writelines(trim(asm).format("\n" + r"// " + command))

        elif command == "sub":
            asm = """
            {}
            @SP
            M=M-1
            @SP
            A=M
            D=M
            @SP
            M=M-1
            @SP
            A=M
            M=M-D
            @SP
            M=M+1
            """
            self.file.writelines(trim(asm).format("\n" + r"// " + command))

        elif command == "neg":
            asm = """
            {}
            @SP
            M=M-1
            @SP
            A=M
            M=-M
            @SP
            M=M+1
            """
            self.file.writelines(trim(asm).format("\n" + r"// " + command))

        elif command == "eq":
            asm = """
            {0}
            @SP
            M=M-1
            @SP
            A=M
            D=M
            @SP
            M=M-1
            @SP
            A=M
            D=M-D
            @EQ{1}
            D;JEQ
            @NEQ{2}
            0;JMP
            (EQ{1})
            @SP
            A=M
            M=-1
            @END{3}
            0;JMP    
            (NEQ{2})
            @SP
            A=M
            M=0
            (END{3})
            @SP
            M=M+1
            """
            labeln = [i for i in range(self.labelcounter, self.labelcounter + 3)]
            self.labelcounter += 3
            self.file.writelines(trim(asm).format("\n" + r"// " + command, *labeln))

        elif command == "gt":
            asm = """
            {0}
            @SP
            M=M-1
            @SP
            A=M
            D=M
            @SP
            M=M-1
            @SP
            A=M
            D=M-D
            @GT{1}
            D;JGT
            @NGT{2}
            0;JMP
            (GT{1})
            @SP
            A=M
            M=-1
            @END{3}
            0;JMP    
            (NGT{2})
            @SP
            A=M
            M=0
            (END{3})
            @SP
            M=M+1
            """
            labeln = [i for i in range(self.labelcounter, self.labelcounter + 3)]
            self.labelcounter += 3
            self.file.writelines(trim(asm).format("\n" + r"// " + command, *labeln))

        elif command == "lt":
            asm = """
            {0}
            @SP
            M=M-1
            @SP
            A=M
            D=M
            @SP
            M=M-1
            @SP
            A=M
            D=M-D
            @LT{1}
            D;JLT
            @NLT{2}
            0;JMP
            (LT{1})
            @SP
            A=M
            M=-1
            @END{3}
            0;JMP    
            (NLT{2})
            @SP
            A=M
            M=0
            (END{3})
            @SP
            M=M+1
            """
            labeln = [i for i in range(self.labelcounter, self.labelcounter + 3)]
            self.labelcounter += 3
            self.file.writelines(trim(asm).format("\n" + r"// " + command, *labeln))

        elif command == "and":
            asm = """
            {}
            @SP
            M=M-1
            @SP
            A=M
            D=M
            @SP
            M=M-1
            @SP
            A=M
            M=D&M
            @SP
            M=M+1
            """
            self.file.writelines(trim(asm).format("\n" + r"// " + command))

        elif command == "or":
            asm = """
            {}
            @SP
            M=M-1
            @SP
            A=M
            D=M
            @SP
            M=M-1
            @SP
            A=M
            MD=D|M
            @SP
            M=M+1
            """
            self.file.writelines(trim(asm).format("\n" + r"// " + command))

        elif command == "not":
            asm = """
            {}
            @SP
            M=M-1
            @SP
            A=M
            M=!M
            @SP
            M=M+1
            """
            self.file.writelines(trim(asm).format("\n" + r"// " + command))

    def close(self):
        self.file.close()

    def writepushpop(self, command, segment, index):
        # build command string, same for all segments
        commandstring = "{}// {} {} {}".format("\n", command, segment, index)

        # translate segment into assembly segment name
        if segment == "local":
            segmentName = "LCL"
        elif segment == "argument":
            segmentName = "ARG"
        elif segment == "this":
            segmentName = "THIS"
        elif segment == "that":
            segmentName = "THAT"

        if command == "push":
            if segment == "constant":
                asm = """
                {}
                @{}
                D=A
                @SP
                A=M
                M=D
                @SP
                M=M+1
                """
                self.file.writelines(trim(asm).format(commandstring, index))
            elif segment in ("local", "argument", "this", "that"):
                asm = """
                {0}
                @{1}
                D=M
                @{2}
                D=D+A
                @addr{3}
                M=D
                @addr{3}
                A=M
                D=M
                @SP
                A=M
                M=D
                @SP
                M=M+1
                """
                self.file.writelines(
                    trim(asm).format(
                        commandstring, segmentName, index, self.labelcounter
                    )
                )
                self.labelcounter += 1
            elif segment == "temp":
                segmentName = str(5 + int(index))
                asm = """
                {}
                @{}
                D=M
                @SP
                A=M
                M=D
                @SP
                M=M+1
                """
                self.file.writelines(trim(asm).format(commandstring, segmentName))
            elif segment == "static":
                segmentName = "{}.{}".format(self.filename, index)
                asm = """
                {}
                @{}
                D=M
                @SP
                A=M
                M=D
                @SP
                M=M+1
                """
                self.file.writelines(trim(asm).format(commandstring, segmentName))
            elif segment == "pointer":
                if index == "0":
                    segmentName = "THIS"
                else:
                    segmentName = "THAT"
                asm = """
                {}
                @{}
                D=M
                @SP
                A=M
                M=D
                @SP
                M=M+1
                """
                self.file.writelines(trim(asm).format(commandstring, segmentName))

        elif command == "pop":
            if segment in ("local", "argument", "this", "that"):
                asm = """
                {0}
                @{1}
                D=M
                @{2}
                D=D+A
                @addr{3}
                M=D
                @SP
                M=M-1
                @SP
                A=M
                D=M
                @addr{3}
                A=M
                M=D
                """
                self.file.writelines(
                    trim(asm).format(
                        commandstring, segmentName, index, self.labelcounter
                    )
                )
                self.labelcounter += 1
            elif segment == "temp":
                segmentName = str(5 + int(index))
                asm = """
                {0}
                @SP
                M=M-1
                @SP
                A=M
                D=M
                @{1}
                A=M
                M=D
                """
                self.file.writelines(trim(asm).format(commandstring, segmentName))

            elif segment == "static":
                segmentName = "{}.{}".format(self.filename, index)
                asm = """
                {}
                @SP
                M=M-1
                @SP
                A=M
                D=M
                @{}
                M=D
                """
                self.file.writelines(trim(asm).format(commandstring, segmentName))
            elif segment == "pointer":
                if index == "0":
                    segmentName = "THIS"
                else:
                    segmentName = "THAT"
                asm = """
                {}
                @SP
                M=M-1
                @SP
                A=M
                D=M
                @{}
                M=D
                """
                self.file.writelines(trim(asm).format(commandstring, segmentName))


if __name__ == "__main__":
    inputf = sys.argv[1]
    outputfile = os.path.basename(inputf).replace(".vm", ".asm")
    outputpath = os.path.split(inputf)[0]
    outputfullname = os.path.join(outputpath, outputfile)
    parser = Parser(inputf)
    cw = CodeWriter(outputfullname)
    while parser.hasMoreCommands:
        parser.advance()
        if parser.commandtype(parser.currentCommand) == "C_ARITHMETIC":
            cw.writeArithmetic(parser.arg1())
        elif parser.commandtype(parser.currentCommand) in ("C_PUSH", "C_POP"):
            cmd = parser.arg1()
            seg, idx = parser.arg2()
            cw.writepushpop(cmd, seg, idx)
    cw.close()
    parser.close()
