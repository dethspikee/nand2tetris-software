import os


from exceptions import IncorrectVariableName


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
        """
        Parses given input stream of tokens into a XML parse tree.
        """
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
        self._compile_class_var_dec()
        self._compile_subroutine_dec()
        self._eat("}")
        self._decrease_indent()
        self.file_obj.write(" " * self.indent + "</class>\n")

    def _compile_class_name(self):
        first_char_of_token = self.tokenizer.token[0]
        if not first_char_of_token.isdigit():
            self._eat(self.tokenizer.token)
        else:
            raise IncorrectVariableName(
                "First character of the class cannot be a digit!"
            )

    def _compile_class_var_dec(self):
        while self.tokenizer.token in {"field", "static"}:
            self.file_obj.write(" " * self.indent + "<classVarDec>\n")
            self._increase_indent()
            self._eat(self.tokenizer.token)
            self._compile_type()
            self._compile_var_name()
            while self.tokenizer.token == ",":
                self._eat(",")
                self._compile_var_name()
            self._eat(";")
            self._decrease_indent()
            self.file_obj.write(" " * self.indent + "</classVarDec>\n")

    def _compile_type(self):
        if self.tokenizer.token in {"int", "boolean", "char"}:
            self._eat(self.tokenizer.token)
        else:
            self._compile_class_name()

    def _compile_var_name(self):
        first_char_of_token = self.tokenizer.token[0]
        if not first_char_of_token.isdigit():
            self._eat(self.tokenizer.token)
        else:
            raise IncorrectVariableName(
                "First character of the variable cannot be a digit!"
            )

    def _compile_subroutine_dec(self):
        while self.tokenizer.token in {"constructor", "function", "method"}:
            self.file_obj.write(" " * self.indent + "<subroutineDec>\n")
            self._increase_indent()
            self._eat(self.tokenizer.token)
            if self.tokenizer.token == "void":
                self._eat("void")
            else:
                self._compile_type()
            self._compile_subroutine_name()
            self._eat("(")
            self._compile_parameter_list()
            self._eat(")")
            self._compile_subroutine_body()
            self._decrease_indent()
            self.file_obj.write(" " * self.indent + "</subroutineDec>\n")

    def _compile_parameter_list(self):
        self.file_obj.write(" " * self.indent + "<parameterList>\n")
        if self.tokenizer.token != ")":
            self._increase_indent()
            self._compile_type()
            self._compile_var_name()
            while self.tokenizer.token == ",":
                self._eat(",")
                self._compile_type()
                self._compile_var_name()
            self._decrease_indent()
        self.file_obj.write(" " * self.indent + "</parameterList>\n")

    def _compile_subroutine_name(self):
        first_char_of_token = self.tokenizer.token[0]
        if not first_char_of_token.isdigit():
            self._eat(self.tokenizer.token)
        else:
            raise IncorrectVariableName(
                "First character of the subroutine cannot be a digit!"
            )

    def _compile_subroutine_body(self):
        self.file_obj.write(" " * self.indent + "<subroutineBody>\n")
        self._increase_indent()
        self._eat("{")
        while self.tokenizer.token == "var":
            self._compile_var_dec()
        self._compile_statements()
        self._eat("}")
        self._decrease_indent()
        self.file_obj.write(" " * self.indent + "</subroutineBody>\n")

    def _compile_subroutine_call(self):
        self._eat(self.tokenizer.token)
        if self.tokenizer.token == ".":
            self._eat(".")
            self._compile_subroutine_name()
            self._eat("(")
            self._compile_expression_list()
            self._eat(")")

    def _compile_expression_list(self):
        self.file_obj.write(" " * self.indent + "<expressionList>\n")
        self._increase_indent()
        if self.tokenizer.token != ")":
            self.compile_expression()
            while self.tokenizer.token == ",":
                self._eat(",")
                self.compile_expression()
        self._decrease_indent()
        self.file_obj.write(" " * self.indent + "</expressionList>\n")

    def _compile_var_dec(self):
        self.file_obj.write(" " * self.indent + "<varDec>\n")
        self._increase_indent()
        self._eat("var")
        self._compile_type()
        self._compile_var_name()
        while self.tokenizer.token == ",":
            self._eat(",")
            self._compile_var_name()
        self._eat(";")
        self._decrease_indent()
        self.file_obj.write(" " * self.indent + "</varDec>\n")

    def _compile_statements(self):
        self.file_obj.write(" " * self.indent + "<statements>\n")
        while self.tokenizer.token in {"let", "if", "while", "do", "return"}:
            if self.tokenizer.token == "let":
                self.compile_let()
            elif self.tokenizer.token == "do":
                self._compile_do()
            elif self.tokenizer.token == "return":
                self._compile_return()
            elif self.tokenizer.token == "while":
                self.compile_while()
            elif self.tokenizer.token == "if":
                self._compile_if()
        self.file_obj.write(" " * self.indent + "</statements>\n")

    def _compile_if(self):
        self._increase_indent()
        self.file_obj.write(" " * self.indent + "<ifStatement>\n")
        self._increase_indent()
        self._eat("if")
        self._eat("(")
        self.compile_expression()
        self._eat(")")
        self._eat("{")
        self._compile_statements()
        self._eat("}")
        if self.tokenizer.token == "else":
            self._eat("else")
            self._eat("{")
            self._compile_statements()
            self._eat("}")
        self._decrease_indent()
        self.file_obj.write(" " * self.indent + "</ifStatement>\n")
        self._decrease_indent()

    def compile_let(self):
        self._increase_indent()
        self.file_obj.write(" " * self.indent + f"<letStatement>\n")
        self._increase_indent()
        self._eat("let")
        self._compile_var_name()
        self._eat("=")
        self.compile_expression()
        self._eat(";")
        self._decrease_indent()
        self.file_obj.write(" " * self.indent + f"</letStatement>\n")
        self._decrease_indent()

    def _compile_do(self):
        self._increase_indent()
        self.file_obj.write(" " * self.indent + "<doStatement>\n")
        self._increase_indent()
        self._eat("do")
        self._compile_subroutine_call()
        self._eat(";")
        self._decrease_indent()
        self.file_obj.write(" " * self.indent + "</doStatement>\n")
        self._decrease_indent()

    def _compile_return(self):
        self._increase_indent()
        self.file_obj.write(" " * self.indent + "<returnStatement>\n")
        self._increase_indent()
        self._eat("return")
        if self.tokenizer.token != ";":
            self.compile_expression()
        self._eat(";")
        self._decrease_indent()
        self.file_obj.write(" " * self.indent + "</returnStatement>\n")
        self._decrease_indent()

    def compile_while(self):
        self._increase_indent()
        self.file_obj.write(" " * self.indent + "<whileStatement>\n")
        self._increase_indent()
        self._eat("while")
        self._eat("(")
        self.compile_expression()
        self._eat(")")
        self._eat("{")
        self._compile_statements()
        self._eat("}")
        self._decrease_indent()
        self.file_obj.write(" " * self.indent + "</whileStatement>\n")
        self._decrease_indent()

    def compile_expression(self):
        self.file_obj.write(" " * self.indent + "<expression>\n")
        self._increase_indent()
        self.complile_term()
        op = self.tokenizer.token
        if op in {"+", "-", "*", "/", "&", "|", "<", ">", "="}:
            self._eat(op)
            self.complile_term()
        self._decrease_indent()
        self.file_obj.write(" " * self.indent + "</expression>\n")

    def complile_term(self):
        self.file_obj.write(" " * self.indent + "<term>\n")
        self._increase_indent()
        varname = self.tokenizer.token
        print(varname)
        self._eat(varname)
        if self.tokenizer.token == ".":
            self._eat(self.tokenizer.token)
            self._compile_subroutine_name()
            self._eat(self.tokenizer.token)
        elif self.tokenizer.token == "(":
            pass
        elif self.tokenizer.token == "[":
            pass
        self._decrease_indent()
        self.file_obj.write(" " * self.indent + "</term>\n")

    def _eat(self, token: str, classification=None) -> None:
        """
        This method accepts a token for which it retrieves its classification
        and writes the following line to the output xml file:

        <token classification> token </token classification>

        for example calling _eat('{') will result in writing the following
        to the output xml file:

        <symbol> { </symbol>

        In the end calls 'advance()' method of the tokenizer object to
        retrieve next token from the tokenizer.
        """
        if classification is None:
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
