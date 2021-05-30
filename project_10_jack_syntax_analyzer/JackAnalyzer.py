import sys


def main() -> None:
    """
    Entrypoint of the syntax analyzer.
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


if __name__ == '__main__':
    main()
