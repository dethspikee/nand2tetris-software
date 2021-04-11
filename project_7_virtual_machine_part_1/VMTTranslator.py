import sys


def main():
    """
    Open file containing VM commands and translate it
    into assembly code.
    <file.vm> -> <file.asm>
    """
    if len(sys.argv) != 2:
        print('Incorrent number of arguments (1 required).')
        print('usage: python3 VMTranslator <input_file.vm>/<input_folder>')
        sys.exit(1)

    file_arg = sys.argv[1]
    filename, extension = file_arg.split('.')

    with Parser(file_arg, filename) as fp:
        fp.parse()


class Parser:

    def __init__(self, file_arg, filename):
        self.file_arg = file_arg
        self.filename = filename

    def parse(self):
        """
        Retrieve all commands from the source file;
        and store them in the 'commands' list
        """
        for line in self.fp.readlines():
            if line[:2] in ['\n', '//']:
                continue
            command = line.rstrip('\n');
            command_type = self.command_type(command)
            if command_type != 'C_RETURN':
                arg_1 = self.get_argument_1(command)
            if command_type in ['C_PUSH', 'C_POP', 'C_FUNCTION', 'C_CALL']:
                arg_2 = self.get_argument_2(command)
            else:
                arg_2 = ''
            
            if command_type == ('C_PUSH' or 'C_POP'):
                self.writePushPop(command)


    def command_type(self, command: str) -> str:
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


    def __enter__(self):
        try:
            self.fp = open(self.file_arg, 'rt')
        except FileNotFoundError:
            print('File not found')
            sys.exit(1)

        self.outfp = open(f'{self.filename}.asm', mode='wt')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.fp.close()
        self.outfp.close()
        print(f'Succesfully created {self.filename}.asm')


if __name__ == '__main__':
    main()
