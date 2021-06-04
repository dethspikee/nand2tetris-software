import sys
import os

from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine


def main() -> None:
    """
    Entrypoint of the syntax analyzer, expects input path.
    Uses two classes internally:

    JackTokenizer     :: responsible for retrieving all tokens
                         from the input file | input dir.

    CompilationEngine :: responsible for parsing tokes and building
                         grammatical structure represented via the XML
                         file(s).
                         Each xxx.jack file will produce xxx.xml file.
                         Directory with x number of jack files will produce
                         x number of xml files stored in the root directory.
    """
    if len(sys.argv) != 2:
        print("Illegal number of arguments. (1 required)")
        print("Path to .jack file or dir with .jack files required.")
        sys.exit(2)

    program_arg = sys.argv[1]
    if os.path.isdir(program_arg):
        jack_files = [
            os.path.join(program_arg, name)
            for name in os.listdir(program_arg)
            if name.endswith(".jack")
            and os.path.isfile(os.path.join(program_arg, name))
        ]
        for file_ in jack_files:
            tokenizer = JackTokenizer(file_)
            with CompilationEngine(tokenizer) as compiler:
                compiler.show_tokens()
            tokenizer.file_obj.close()
    elif program_arg.endswith(".jack"):
        tokenizer = JackTokenizer(program_arg)
        with CompilationEngine(tokenizer) as compiler:
            compiler.parse()

        tokenizer.file_obj.close()


if __name__ == "__main__":
    main()
