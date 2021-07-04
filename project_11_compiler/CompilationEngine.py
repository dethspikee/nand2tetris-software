import os

from SymbolTable import SymbolTable
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
        self.class_symbol_table = SymbolTable()
        self.routine_symbol_table = SymbolTable()
        self.class_name = ''

    def parse(self) -> None:
        """
        Parses given stream of tokens and creates
        XML parse tree.
        """
        while self.tokenizer.has_tokens():
            self._compile_class()
        self.class_symbol_table.show_table()

    def _compile_class(self) -> None:
        """
        Compiles a comlete class.
        """
        self.file_obj.write(" " * self.indent + "<class>\n")
        self._increase_indent()
        self._eat("class")
        self.class_name = self.tokenizer.token
        self._compile_class_name()
        self._eat("{")
        self._compile_class_var_dec()
        self._compile_subroutine_dec()
        self._eat("}")
        self._decrease_indent()
        self.file_obj.write(" " * self.indent + "</class>\n")

    def _compile_class_name(self) -> None:
        """
        Compiles a class name. Raises IncorrectVariableName
        exception if first character is a digit.
        """
        first_char_of_token = self.tokenizer.token[0]
        if not first_char_of_token.isdigit():
            self._eat(self.tokenizer.token, category="class", meaning="expression")
        else:
            raise IncorrectVariableName(
                "First character of the class cannot be a digit!"
            )

    def _compile_class_var_dec(self) -> None:
        """
        Compiles a static declaration or
        a field declaration.
        """
        while self.tokenizer.token in {"field", "static"}:
            self.file_obj.write(" " * self.indent + "<classVarDec>\n")
            self._increase_indent()
            kind = self.tokenizer.token
            self._eat(self.tokenizer.token)
            type = self.tokenizer.token
            self._compile_type()
            name = self.tokenizer.token
            self.class_symbol_table.define(name, type, kind)
            self._compile_var_name(meaning="define")
            while self.tokenizer.token == ",":
                self._eat(",")
                name = self.tokenizer.token
                self.class_symbol_table.define(name, type, kind)
                self._compile_var_name(meaning="define")
            self._eat(";")
            self._decrease_indent()
            self.file_obj.write(" " * self.indent + "</classVarDec>\n")

    def _compile_type(self) -> None:
        """
        Compiles a variable type otherwise calls _compile_class_name().
        """
        if self.tokenizer.token in {"int", "boolean", "char"}:
            self._eat(self.tokenizer.token)
        else:
            self._compile_class_name()

    def _compile_var_name(self, **kwargs) -> None:
        """
        Compiles variable name. Raises IncorrectVariableName
        exception if first character is a digit.
        """
        first_char_of_token = self.tokenizer.token[0]
        if not first_char_of_token.isdigit():
            self._eat(self.tokenizer.token, **kwargs)
        else:
            raise IncorrectVariableName(
                "First character of the variable cannot be a digit!"
            )

    def _compile_subroutine_dec(self) -> None:
        """
        Compiles a subroutine declaration.
        """
        while self.tokenizer.token in {"constructor", "function", "method"}:
            self.routine_symbol_table.start_subroutine()
            self.file_obj.write(" " * self.indent + "<subroutineDec>\n")
            if self.tokenizer.token == "method":
                self.routine_symbol_table.define("this", self.class_name,
                        "argument")
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
            self.routine_symbol_table.show_table()

    def _compile_parameter_list(self) -> None:
        """
        Compiles parameter list.
        """
        self.file_obj.write(" " * self.indent + "<parameterList>\n")
        if self.tokenizer.token != ")":
            kind = 'argument'
            self._increase_indent()
            type = self.tokenizer.token
            self._compile_type()
            name = self.tokenizer.token
            self.routine_symbol_table.define(name, type, kind)
            self._compile_var_name(meaning="parameter")
            while self.tokenizer.token == ",":
                self._eat(",")
                type = self.tokenizer.token
                self._compile_type()
                name = self.tokenizer.token
                self.routine_symbol_table.define(name, type, kind)
                self._compile_var_name(meaning="parameter")
            self._decrease_indent()
        self.file_obj.write(" " * self.indent + "</parameterList>\n")

    def _compile_subroutine_name(self) -> None:
        """
        Compiles subroutine name.
        Raises IncorrectVariableName if first character is a digit.
        """
        first_char_of_token = self.tokenizer.token[0]
        if not first_char_of_token.isdigit():
            self._eat(self.tokenizer.token, category="subroutine", meaning="expression")
        else:
            raise IncorrectVariableName(
                "First character of the subroutine cannot be a digit!"
            )

    def _compile_subroutine_body(self) -> None:
        """
        Compiles subroutine body.
        """
        self.file_obj.write(" " * self.indent + "<subroutineBody>\n")
        self._increase_indent()
        self._eat("{")
        while self.tokenizer.token == "var":
            self._compile_var_dec()
        self._compile_statements()
        self._eat("}")
        self._decrease_indent()
        self.file_obj.write(" " * self.indent + "</subroutineBody>\n")

    def _compile_subroutine_call(self) -> None:
        """
        Compiles subroutine call.
        """
        token = self.tokenizer.token
        next_token = next(self.tokenizer.tokens)
        if next_token == ".":
            self._eat(token, advance=False, category="class", meaning="expression")
            self.tokenizer.token = next_token
            self._eat(".")
            self._compile_subroutine_name()
            self._eat("(")
            self._compile_expression_list()
            self._eat(")")
        elif next_token == "(":
            self._eat(token, advance=False, category="class", meaning="expression")
            self.tokenizer.token = next_token
            self._eat("(")
            self._compile_expression_list()
            self._eat(")")
        elif next_token == "[":
            self._eat(token, advance=False, category="class", meaning="expression")
            self.tokenizer.token = next_token
            self._eat("[")
            self._compile_expression()
            self._eat("]")

    def _compile_expression_list(self) -> None:
        """
        Compiles expression list.
        """
        self.file_obj.write(" " * self.indent + "<expressionList>\n")
        self._increase_indent()
        if self.tokenizer.token != ")":
            self._compile_expression()
            while self.tokenizer.token == ",":
                self._eat(",")
                self._compile_expression()
        self._decrease_indent()
        self.file_obj.write(" " * self.indent + "</expressionList>\n")

    def _compile_var_dec(self) -> None:
        """
        Compiles variable declaration.
        """
        self.file_obj.write(" " * self.indent + "<varDec>\n")
        self._increase_indent()
        kind = self.tokenizer.token
        self._eat("var")
        type = self.tokenizer.token
        self._compile_type()
        name = self.tokenizer.token
        self.routine_symbol_table.define(name, type, kind)
        self._compile_var_name(meaning="define")
        while self.tokenizer.token == ",":
            self._eat(",")
            name = self.tokenizer.token
            self.routine_symbol_table.define(name, type, kind)
            self._compile_var_name(meaning="define")
        self._eat(";")
        self._decrease_indent()
        self.file_obj.write(" " * self.indent + "</varDec>\n")

    def _compile_statements(self) -> None:
        """
        Compiles statements.
        """
        self.file_obj.write(" " * self.indent + "<statements>\n")
        while self.tokenizer.token in {"let", "if", "while", "do", "return"}:
            if self.tokenizer.token == "let":
                self._compile_let()
            elif self.tokenizer.token == "do":
                self._compile_do()
            elif self.tokenizer.token == "return":
                self._compile_return()
            elif self.tokenizer.token == "while":
                self._compile_while()
            elif self.tokenizer.token == "if":
                self._compile_if()
        self.file_obj.write(" " * self.indent + "</statements>\n")

    def _compile_if(self) -> None:
        """
        Compiles if statement.
        """
        self._increase_indent()
        self.file_obj.write(" " * self.indent + "<ifStatement>\n")
        self._increase_indent()
        self._eat("if")
        self._eat("(")
        self._compile_expression()
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

    def _compile_let(self) -> None:
        """
        Compiles let statements.
        """
        self._increase_indent()
        self.file_obj.write(" " * self.indent + f"<letStatement>\n")
        self._increase_indent()
        self._eat("let")
        self._compile_var_name(meaning="expression")
        if self.tokenizer.token == "[":
            self._eat("[")
            self._compile_expression()
            self._eat("]")
        self._eat("=")
        self._compile_expression()
        self._eat(";")
        self._decrease_indent()
        self.file_obj.write(" " * self.indent + f"</letStatement>\n")
        self._decrease_indent()

    def _compile_do(self) -> None:
        """
        Compiles do statements.
        """
        self._increase_indent()
        self.file_obj.write(" " * self.indent + "<doStatement>\n")
        self._increase_indent()
        self._eat("do")
        self._compile_subroutine_call()
        self._eat(";")
        self._decrease_indent()
        self.file_obj.write(" " * self.indent + "</doStatement>\n")
        self._decrease_indent()

    def _compile_return(self) -> None:
        """
        Compiles return statements.
        """
        self._increase_indent()
        self.file_obj.write(" " * self.indent + "<returnStatement>\n")
        self._increase_indent()
        self._eat("return")
        if self.tokenizer.token != ";":
            self._compile_expression()
        self._eat(";")
        self._decrease_indent()
        self.file_obj.write(" " * self.indent + "</returnStatement>\n")
        self._decrease_indent()

    def _compile_while(self) -> None:
        """
        Compiles while statements.
        """
        self._increase_indent()
        self.file_obj.write(" " * self.indent + "<whileStatement>\n")
        self._increase_indent()
        self._eat("while")
        self._eat("(")
        self._compile_expression()
        self._eat(")")
        self._eat("{")
        self._compile_statements()
        self._eat("}")
        self._decrease_indent()
        self.file_obj.write(" " * self.indent + "</whileStatement>\n")
        self._decrease_indent()

    def _compile_expression(self) -> None:
        """
        Compiles expressions.
        """
        self.file_obj.write(" " * self.indent + "<expression>\n")
        self._increase_indent()
        self._compile_term()
        op = self.tokenizer.token
        if op in {"+", "-", "*", "/", "&", "|", "<", ">", "="}:
            self._eat(op)
            self._compile_term()
        self._decrease_indent()
        self.file_obj.write(" " * self.indent + "</expression>\n")

    def _compile_term(self) -> None:
        """
        Compiles a term.
        """
        self.file_obj.write(" " * self.indent + "<term>\n")
        self._increase_indent()
        varname = self.tokenizer.token
        varname_classification = self.tokenizer.get_token_classification()
        next_token = next(self.tokenizer.tokens)

        if (
            varname_classification == "integerConstant"
            or varname_classification == "stringConstant"
            or varname in {"true", "false", "null", "this"}
        ):
            self._eat(varname, advance=False, classification=varname_classification)
            self.tokenizer.token = next_token
        elif varname == "(":
            self._eat("(", advance=False, classification=varname_classification)
            self.tokenizer.token = next_token
            self._compile_expression()
            self._eat(")")
        elif varname in {"-", "~"}:
            self._eat(varname, advance=False, classification=varname_classification)
            self.tokenizer.token = next_token
            self._compile_term()
        elif varname_classification == "identifier" and next_token == "[":
            self._eat(varname, advance=False, classification="identifier",
                    category="variable", meaning="expression")
            self.tokenizer.token = next_token
            self._eat("[")
            self._compile_expression()
            self._eat("]")
        elif varname_classification == "identifier" and next_token == ".":
            self._eat(varname, advance=False, classification="identifier",
                    category="class", meaning="expression")
            self.tokenizer.token = next_token
            self._eat(".")
            self._compile_subroutine_name()
            self._eat("(")
            self._compile_expression_list()
            self._eat(")")
        elif varname_classification == 'identifier' and next_token == '(':
            self._eat(varname, advance=False, classification='identifier',
                    category="subroutine", meaning="expression")
            self.tokenizer.token = next_token
            self._eat('(')
            self._compile_expression_list()
            self._eat(')')
        elif varname_classification == "identifier":
            self._eat(varname, advance=False, classification="identifier",
                    category="", meaning="expression")
            self.tokenizer.token = next_token

        self._decrease_indent()
        self.file_obj.write(" " * self.indent + "</term>\n")

    def _eat(self, token: str, advance=True, classification=None, **kwargs) -> None:
        """
        This method accepts a positional arg 'token' for which it retrieves its
        classification and writes the following line to the output xml file:

        <token classification> token </token classification>

        for example calling _eat('{') will write following line:

        <symbol> { </symbol>

        Users can also pass additional keyword arguments 'advance' to fetch
        next token and 'classification' to provide own token classification used
        when writing to the XML file.

        if classification is not provided as an argument then _eat() method will call
        get_token_classification() method of the tokenizer object to retrieve
        one.

        In order to produce HTML friendly XML file(s) some of the tokens must be
        escaped to be displayed on a web page.
        """
        if not classification:
            classification = self.tokenizer.get_token_classification()
            print(token, classification)

        if classification == "stringConstant":
            token = token.replace('"', "").strip()
        elif token == "<":
            token = "&lt;"
        elif token == ">":
            token = "&gt;"
        elif token == '"':
            token = "&quot;"
        elif token == "&":
            token = "&amp;"

        if classification == "identifier" and (token in \
            self.routine_symbol_table.table or self.class_symbol_table.table):
            running_index = ''
            meaning = kwargs["meaning"]
            category = self.class_symbol_table.kind_of(token) or \
                    self.routine_symbol_table.kind_of(token) or \
                    kwargs["category"]
            if category not in {"class", "subroutine"}:
                running_index = self.class_symbol_table.index_of(token) or \
                        self.routine_symbol_table.index_of(token)
                self.file_obj.write(" " * self.indent + f'<{classification} category=\"{category}\" '
                        f'index="{running_index}" meaning="{meaning}">')
                self.file_obj.write(f" {token} ")
                self.file_obj.write(f"</{classification}>\n")
            else:
                self.file_obj.write(" " * self.indent + f"<{category}, {meaning}>")
                self.file_obj.write(f" {token} ")
                self.file_obj.write(f"</{classification}>\n")

        elif classification == "identifier":
            print(token, classification)
            category = kwargs["category"]
            self.file_obj.write(" " * self.indent + f'<{classification} category="{category}">')
            self.file_obj.write(f" {token} ")
            self.file_obj.write(f"</{classification}>\n")
        else:
            self.file_obj.write(" " * self.indent + f"<{classification}>")
            self.file_obj.write(f" {token} ")
            self.file_obj.write(f"</{classification}>\n")


        if advance:
            self.tokenizer.advance()

    def _show_tokens(self) -> None:
        """
        Prints list of tokens. This can be used for debugging purposes
        in order to inspect output of the JackTokenizer.
        """
        print(list(self.tokenizer.tokens))

    def _increase_indent(self) -> None:
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

    def _decrease_indent(self) -> None:
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
        """
        Implements context management protocol.

        Retrieve dirname and the basename of the input file passed to
        tokenizer.

        This method is used when a directory was supplied to the JackAnalyzer.
        Creates an output name for each input file and opens a file in the
        directory passed to JackAnalyzer. Each output file will have a name of
        'output_name.xml'
        """
        dirname = os.path.dirname(self.tokenizer.file_obj.name)
        basename = os.path.basename(self.tokenizer.file_obj.name)
        output_name = basename.split(".")[0]
        self.file_obj = open(
            f"{os.path.join(dirname, output_name)}.xml", "wt", encoding="utf-8"
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Clean up by closing all references to the open file.
        """
        if self.file_obj:
            self.file_obj.close()
