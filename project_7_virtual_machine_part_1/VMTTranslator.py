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
        print('\tusage: python3 VMTranslator <input_file.vm>/<input_folder>\n')
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
        self.target.close()
        print('Target closed succesfully')


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

    def remove_new_line(self, line: str) -> str :
        return line.strip('\n')

    def translate_and_write(self, line):
        command_type = self.get_command_type(line.rstrip('\n'))

    def writePushPop(self, command):
        action = command.split()[0]
        arg_1 = self.get_argument_1(command)
        arg_2 = self.get_argument_2(command)
        
        if action == 'push' and arg_1 == 'constant':
            self.outfp.write(f'@{arg_2}\n')
            self.outfp.write(f'D=A\n')
            self.outfp.write(f'D=A\n')
            self.outfp.write(f'@SP\n')
            self.outfp.write(f'A=M\n')
            self.outfp.write(f'M=D\n')
            self.outfp.write(f'@SP\n')
            self.outfp.write(f'M=M+1\n')

if __name__ == '__main__':
    main()
