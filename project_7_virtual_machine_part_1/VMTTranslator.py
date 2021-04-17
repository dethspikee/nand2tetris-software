import sys
import os


def main():
    """
    Open file containing VM commands and translate it
    into assembly code.
    <file.vm> -> <file.asm>
    """
    if len(sys.argv) != 2:
        print('Translate .vm files into assembly instruction')
        print('Incorrent number of arguments (1 required).\n')
        print('usage: python3 VMTranslator <input_file.vm>/<input_folder>\n')
        sys.exit(1)

    with Parser(sys.argv[1]) as vmtranslator:
        vmtranslator.parse()
         

class Parser:

    def __init__(self, source):
        self.source = source

    def parse(self):
        """
        Retrieve all commands from the source file(s);
        and its arguments.
        """
        translator = Translator(self.target)
        for file_ in self.files:
            try:
                fp = open(file_, 'rt')
                for line in fp.readlines():
                    if line[:2] in ['\n', '//']:
                        continue
                    line_rstrip = line.rstrip('\n')
                    arg_1 = ''
                    arg_2 = ''
                    command_type = self.get_command_type(line_rstrip)
                    if command_type != 'C_RETURN':
                        arg_1 = self.get_argument_1(line_rstrip)
                    if command_type in ['C_PUSH', 'C_POP', 
                                        'C_FUNCTION', 'C_CALL']:
                        arg_2 = self.get_argument_2(line_rstrip)
                    translator.translate(command_type, arg_1, arg_2)
            finally:
                fp.close()

    def get_command_type(self, command: str) -> str:
        """
        Return command type based on the command received
        """
        commands = {
                'add': 'C_ARITHMETIC',
                'sub': 'C_ARITHMETIC',
                'neg': 'C_ARITHMETIC',
                'eq': 'C_ARITHMETIC',
                'gt': 'C_ARITHMETIC',
                'lt': 'C_ARITHMETIC',
                'and': 'C_ARITHMETIC',
                'or': 'C_ARITHMETIC',
                'not': 'C_ARITHMETIC',
                'push': 'C_PUSH',
                'pop': 'C_POP',
                }
        command = command.split()[0]
        return commands[command]

    def get_argument_1(self, command: str) -> str:
        """
        Return first argument of the command received;
        return command itself if C_ARITHMETIC
        """
        argument = command.split()
        return argument[0] if len(argument) == 1 else argument[1]

    def get_argument_2(self, command: str) -> int:
        """
        Return second argument of the command received;
        converted to int
        """
        argument = command.split()[-1]
        return int(argument)

    def __enter__(self):
        self.files = []
        if os.path.isdir(self.source):
            for file_ in os.listdir(self.source):
                if '.vm' in file_:
                    self.files.append(file_)
            filepath = os.path.join('.', self.source, f'{self.source}.asm')
            self.target = open(f'{filepath}', 'wt')
        elif '.vm' in self.source:
            self.files.append(self.source)
            name, extension = self.source.split('.')
            self.target = open(f'{name}.asm', 'wt')
        else:
            print('Problem opening input file.')
            print('Only .vm files are accepted')
            sys.exit(1)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value is None:
            self.target.close()
            print('.asm file created succesfully')


class Translator:

    def __init__(self, fp):
        self.fp = fp

    def translate(self, command_type, arg_1, arg_2):
        if command_type == 'C_ARITHMETIC':
            self.write_arithmetic(arg_1)
        elif command_type in ['C_PUSH', 'C_POP']:
            self.write_push_pop(command_type, arg_1, arg_2)

    def write_push_pop(self, command_type, segment, index):
        if segment == 'constant' and command_type == 'C_PUSH':
            self.fp.write(f'@{index}\n')
            self.fp.write('D=A\n')
            self.fp.write('@SP\n')
            self.fp.write('A=M\n')
            self.fp.write('M=D\n')
            self.fp.write('@SP\n')
            self.fp.write('M=M+1\n')

    def write_arithmetic(self, command):
        if command == 'add':
            self.fp.write('@SP\n')
            self.fp.write('AM=M-1\n')
            self.fp.write('D=M\n')
            self.fp.write('@SP\n')
            self.fp.write('AM=M-1\n')
            self.fp.write('D=D+M\n')
            self.fp.write('@SP\n')
            self.fp.write('A=M\n')
            self.fp.write('M=D\n')
            self.fp.write('@SP\n')
            self.fp.write('M=M+1\n')
        elif command == 'sub':
            self.fp.write('@SP\n')
            self.fp.write('AM=M-1\n')
            self.fp.write('D=M\n')
            self.fp.write('@SP\n')
            self.fp.write('AM=M-1\n')
            self.fp.write('MD=M-D\n')
            self.fp.write('@SP\n')
            self.fp.write('M=M+1\n')
        elif command == 'neg':
            self.fp.write('@SP\n')
            self.fp.write('AM=M-1\n')
            self.fp.write('M=-M\n')
            self.fp.write('@SP\n')
            self.fp.write('M=M+1\n')
        elif command == 'eq':
            self.fp.write('@SP\n')
            self.fp.write('AM=M-1\n')
            self.fp.write('D=M\n')
            self.fp.write('@SP\n')
            self.fp.write('AM=M-1\n')
            self.fp.write('MD=M-D\n')
            self.fp.write('@EQUAL\n')
            self.fp.write('D;JEQ\n')
            self.fp.write('@NOTEQUAL\n')
            self.fp.write('D;JNE\n')
            self.fp.write('(EQUAL)\n')
            self.fp.write('@SP\n')
            self.fp.write('A=M\n')
            self.fp.write('M=-1\n')
            self.fp.write('@END\n')
            self.fp.write('0;JMP\n')
            self.fp.write('(NOTEQUAL)\n')
            self.fp.write('@SP\n')
            self.fp.write('A=M\n')
            self.fp.write('M=0\n')
            self.fp.write('@END\n')
            self.fp.write('0;JMP\n')
            self.fp.write('(END)\n')
            self.fp.write('@SP\n')
            self.fp.write('M=M+1\n')
        elif command == 'gt':
            self.fp.write('@SP\n')
            self.fp.write('AM=M-1\n')
            self.fp.write('D=M\n')
            self.fp.write('@SP\n')
            self.fp.write('AM=M-1\n')
            self.fp.write('MD=M-D\n')
            self.fp.write('@GREATER\n')
            self.fp.write('D;JGT\n')
            self.fp.write('@NOTGREATER\n')
            self.fp.write('D;JMP\n')
            self.fp.write('(GREATER)\n')
            self.fp.write('@SP\n')
            self.fp.write('A=M\n')
            self.fp.write('M=-1\n')
            self.fp.write('@END\n')
            self.fp.write('0;JMP\n')
            self.fp.write('(NOTGREATER)\n')
            self.fp.write('@SP\n')
            self.fp.write('A=M\n')
            self.fp.write('M=0\n')
            self.fp.write('@END\n')
            self.fp.write('0;JMP\n')
            self.fp.write('(END)\n')
            self.fp.write('@SP\n')
            self.fp.write('M=M+1\n')
        elif command == 'lt':
            self.fp.write('@SP\n')
            self.fp.write('AM=M-1\n')
            self.fp.write('D=M\n')
            self.fp.write('@SP\n')
            self.fp.write('AM=M-1\n')
            self.fp.write('MD=M-D\n')
            self.fp.write('@SMALLER\n')
            self.fp.write('D;JLT\n')
            self.fp.write('@NOTSMALLER\n')
            self.fp.write('D;JMP\n')
            self.fp.write('(SMALLER)\n')
            self.fp.write('@SP\n')
            self.fp.write('A=M\n')
            self.fp.write('M=-1\n')
            self.fp.write('@END\n')
            self.fp.write('0;JMP\n')
            self.fp.write('(NOTSMALLER)\n')
            self.fp.write('@SP\n')
            self.fp.write('A=M\n')
            self.fp.write('M=0\n')
            self.fp.write('@END\n')
            self.fp.write('0;JMP\n')
            self.fp.write('(END)\n')
            self.fp.write('@SP\n')
            self.fp.write('M=M+1\n')
        elif command == 'and':
            self.fp.write('@SP\n')
            self.fp.write('AM=M-1\n')
            self.fp.write('D=M\n')
            self.fp.write('@SP\n')
            self.fp.write('AM=M-1\n')
            self.fp.write('M=M&D\n')
            self.fp.write('@SP\n')
            self.fp.write('M=M+1\n')
        elif command == 'or':
            self.fp.write('@SP\n')
            self.fp.write('AM=M-1\n')
            self.fp.write('D=M\n')
            self.fp.write('@SP\n')
            self.fp.write('AM=M-1\n')
            self.fp.write('M=M|D\n')
            self.fp.write('@SP\n')
            self.fp.write('M=M+1\n')
        elif command == 'not':
            self.fp.write('@SP\n')
            self.fp.write('AM=M-1\n')
            self.fp.write('M=!M\n')
            self.fp.write('@SP\n')
            self.fp.write('M=M+1\n')


if __name__ == '__main__':
    main()
