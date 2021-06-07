import os


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
        self.indent = 0

    def parse(self):
        while self.tokenizer.has_tokens():
            if self.tokenizer.token == "class":
                self._compile_class()
            elif self.tokenizer.token == "while":
                self.compile_while()

    def _compile_class(self):
        self.file_obj.write(" " * self.indent + "<class>\n")
        self._increase_indent()
        self._eat("class")
        self._compile_class_name()
        self._eat("{")
        self._eat("}")
        self._decrease_indent()
        self.file_obj.write(" " * self.indent + "</class>\n")

    def _compile_class_name(self):
        first_char_of_token = self.tokenizer.token[0]
        if not first_char_of_token.isdigit():
            self._eat(self.tokenizer.token)
        else:
            # raise an error if first char if identifier is a digit
            pass

    def _compile_statements(self):
        self.file_obj.write(" " * self.indent + "<statements>\n")
        if self.tokenizer.token == "let":
            self.compile_let()
        self.file_obj.write(" " * self.indent + "</statements>\n")

    def compile_let(self):
        self._increase_indent()
        self.file_obj.write(" " * self.indent + f"<letStatement>\n")
        self._increase_indent()
        self._eat("let")
        self._eat(self.tokenizer.token)
        self._eat("=")
        self.compile_expression()
        self._eat(";")
        self._decrease_indent()
        self.file_obj.write(" " * self.indent + f"<letStatement>\n")
        self._decrease_indent()

    def compile_while(self):
        self.file_obj.write("<whileStatement>\n")
        self._increase_indent()
        self._eat("while")
        self._eat("(")
        self.compile_expression()
        self._eat(")")
        self._eat("{")
        self._compile_statements()
        self._eat("}")
        self._decrease_indent()
        self.file_obj.write("</whileStatement>\n")

    def compile_expression(self):
        self.file_obj.write(" " * self.indent + "<expression>\n")
        self._increase_indent()
        self.complile_term()
        op = self.tokenizer.token
        if self.tokenizer.token_type() == "SYMBOL":
            self._eat(op)
            self.complile_term()
        self._decrease_indent()
        self.file_obj.write(" " * self.indent + "</expression>\n")

    def complile_term(self):
        self.file_obj.write(" " * self.indent + "<term>\n")
        self._increase_indent()
        varname = self.tokenizer.token
        next_token = next(self.tokenizer.tokens)
        if next_token == ".":
            pass
        elif next_token == "(":
            pass
        elif next_token == "[":
            pass
        else:
            classification = self.tokenizer.get_token_classification()
            self.file_obj.write(" " * self.indent + f"<{classification}>")
            self.file_obj.write(f" {self.tokenizer.token} ")
            self.file_obj.write(f"</{classification}>\n")
        self._decrease_indent()
        self.file_obj.write(" " * self.indent + "</term>\n")
        self.tokenizer.token = next_token

    def _eat(self, token: str) -> None:
        """
        This method accepts a token for which it retrieves a classification
        and writes the following line to the output xml file:

        <token classification> token </token classification>

        for example:

        <symbol> { </symbol>

        In the end it calls 'advance()' method of the tokenizer object
        retrieve next token from the input.
        """
        classification = self.tokenizer.get_token_classification()
        self.file_obj.write(" " * self.indent + f"<{classification}>")
        self.file_obj.write(f" {token} ")
        self.file_obj.write(f"</{classification}>\n")
        self.tokenizer.advance()

    def show_tokens(self):
        print(list(self.tokenizer.tokens))

    def _increase_indent(self):
        """
        Method used to increase indentation level in the
        the output xml file.

        Together with _decrease_indent() creates better readable XML file:
        <symbol>
          <identifier>
          </identifier>
        </symbol>
        """
        self.indent += 2

    def _decrease_indent(self):
        """
        Method used to decrease indentation level in the
        output xml file.

        Together with _increase_indent() creates better readable XML file:
        <symbol>
          <identifier>
          </identifier>
        </symbol>
        """
        self.indent -= 2

    def __enter__(self):
        basename = os.path.basename(self.tokenizer.file_obj.name)
        output_name = basename.split(".")[0]
        self.file_obj = open(f"{output_name}.xml", "wt", encoding="utf-8")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file_obj:
            self.file_obj.close()
