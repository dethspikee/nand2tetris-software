import sys


def main():
    """
    Read and translate .vm file to assembly code
    """
    if len(sys.argv) != 2:
        print('Incorrent number of arguments (1 required).')
        print('usage: python3 VMTranslator <input_file.vm>')
        sys.exit(1)

    file_arg = sys.argv[1]
    filename, extension = file_arg.split('.')

    with Parser(file_arg) as fp:
        fp.parse()
        print(fp.instructions)



class Parser:

    def __init__(self, file_arg):
        self.file_arg = file_arg
        self.instructions = []

    def parse(self):
        """
        Retrieve all instructions from the source file;
        and store them in the 'instructions' list
        """
        for line in self.fp.readlines():
            if line[:2] in ['\n', '//']:
                continue
            self.instructions.append(line.rstrip('\n'))

    def __enter__(self):
        self.fp = open(self.file_arg)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.fp.close()
        print('File has been closed...')

if __name__ == '__main__':
    main()

