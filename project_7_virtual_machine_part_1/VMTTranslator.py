import sys


def main():
    """
    Open file containing VM commands and translate it
    into assembly code.
    <file.vm> -> <file.asm>
    """
    if len(sys.argv) != 2:
        print('Incorrent number of arguments (1 required).')
        print('usage: python3 VMTranslator <input_file.vm>')
        sys.exit(1)

    file_arg = sys.argv[1]
    filename, extension = file_arg.split('.')

    with Parser(file_arg) as fp:
        fp.parse()


class Parser:

    def __init__(self, file_arg):
        self.file_arg = file_arg

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

    def __enter__(self):
        try:
            self.fp = open(self.file_arg, 'rt')
        except FileNotFoundError:
            print('File not found')
            sys.exit(1)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.fp.close()
        print('File has been closed...')


if __name__ == '__main__':
    main()

