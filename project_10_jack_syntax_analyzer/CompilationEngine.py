class CompilationEngine:
    """
    Class that effects the actual compilation output.
    Gets its input from a JackTokenizer and emits its
    parsed structure into an output file/stream.

    This version of the compiler emits a structured
    printout of the code, wrapped in XML tags. In the final
    version of the compiler, (project 11), this module
    generates executable VM code.
    """

    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
