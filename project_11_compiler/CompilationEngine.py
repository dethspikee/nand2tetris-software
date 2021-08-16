import os

from VMWriter import VMWriter
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
        self.class_name = ""
        self.function_name = ""
        self.items_pushed_on_stack = 0
        self.label_counter = 0
        self.constructor = False
        self.method = False

    def parse(self) -> None:
        """
        Parses given stream of tokens and creates
        XML parse tree.
        """
        while self.tokenizer.has_tokens():
            self._compile_class()
        #self.class_symbol_table.show_table()

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
            if self.tokenizer.token == "constructor":
                self.constructor = True
            elif self.tokenizer.token == "method":
                self.method = True
            self.routine_symbol_table.start_subroutine()
            self.label_counter = 0
            self.file_obj.write(" " * self.indent + "<subroutineDec>\n")
            if self.tokenizer.token == "method":
                self.routine_symbol_table.define("this", self.class_name, "argument")
            self._increase_indent()
            self._eat(self.tokenizer.token)
            if self.tokenizer.token == "void":
                self._eat("void")
            else:
                self._compile_type()
            self.function_name = f"{self.class_name}.{self.tokenizer.token}"
            self._compile_subroutine_name()
            self._eat("(")
            self._compile_parameter_list()
            self._eat(")")
            self._compile_subroutine_body()
            self._decrease_indent()
            self.constructor = False
            self.method = False
            self.file_obj.write(" " * self.indent + "</subroutineDec>\n")
            #self.routine_symbol_table.show_table()

    def _compile_parameter_list(self) -> None:
        """
        Compiles parameter list.
        """
        self.file_obj.write(" " * self.indent + "<parameterList>\n")
        if self.tokenizer.token != ")":
            kind = "argument"
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

    def _compile_subroutine_name(self, method=False) -> None:
        """
        Compiles subroutine name.
        Raises IncorrectVariableName if first character is a digit.
        """
        first_char_of_token = self.tokenizer.token[0]
        if not first_char_of_token.isdigit():
            if not method:
                self._eat(
                    self.tokenizer.token, category="subroutine", meaning="expression"
                )
            else:
                self._eat(self.tokenizer.token, category="method", meaning="expression")
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
        self.vmwriter.write_function(
            self.function_name, self.routine_symbol_table.var_count("local")
        )
        if self.constructor:
            var_needed = 0
            var_needed += self.class_symbol_table.var_count("field")
            self.vmwriter.write_push("constant", var_needed)
            self.vmwriter.write_call("Memory.alloc", 1)
            self.vmwriter.write_pop("pointer", 0)
        elif self.method:
            self.vmwriter.write_push("argument", 0)
            self.vmwriter.write_pop("pointer", 0)
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
        if next_token == "." and token in self.routine_symbol_table.table:
            self.items_pushed_on_stack += 1
            token_type = self.routine_symbol_table.type_of(token)
            class_name = token_type
            self._eat(token, advance=False, category="object", meaning="expression")
            self.tokenizer.token = next_token
            self._eat(".")
            self.function_name = self.tokenizer.token
            self._compile_subroutine_name()
            self._eat("(")
            self._compile_expression_list()
            self.vmwriter.write_call(
                f"{token_type}.{self.function_name}", self.items_pushed_on_stack
            )
            self.items_pushed_on_stack = 0
            self._eat(")")
        elif next_token == "." and token in self.class_symbol_table.table:
            type = self.class_symbol_table.type_of(token)
            class_name_copy = token
            self._eat(token, advance=False, category="class", meaning="expression")
            self.tokenizer.token = next_token
            self._eat(".")
            self.function_name = self.tokenizer.token
            self._compile_subroutine_name()
            self._eat("(")
            self._compile_expression_list()
            self.items_pushed_on_stack += 1
            self.vmwriter.write_call(
                f"{type}.{self.function_name}", self.items_pushed_on_stack
            )
            self.items_pushed_on_stack = 0
            self._eat(")")
        elif next_token == "." and token not in self.routine_symbol_table.table:
            class_name_copy = token
            self._eat(token, advance=False, category="class", meaning="expression")
            self.tokenizer.token = next_token
            self._eat(".")
            self.function_name = self.tokenizer.token
            self._compile_subroutine_name()
            self._eat("(")
            self._compile_expression_list()
            if token in self.class_symbol_table.table:
                self.items_pushed_on_stack += 1
                type = self.class_symbol_table.type_of(token)
                self.vmwriter.write_call(
                    f"{type}.{self.function_name}", self.items_pushed_on_stack
                )
            else:
                self.vmwriter.write_call(
                    f"{class_name_copy}.{self.function_name}", self.items_pushed_on_stack
                )
            self.items_pushed_on_stack = 0
            self._eat(")")
        elif next_token == "(":
            function_name = token
            self._eat(token, advance=False, category="method", meaning="expression")
            self.tokenizer.token = next_token
            self._eat("(")
            self.vmwriter.write_push("pointer", 0)
            self.items_pushed_on_stack += 1
            self._compile_expression_list()
            self.vmwriter.write_call(
                f"{self.class_name}.{function_name}", self.items_pushed_on_stack
            )
            self.items_pushed_on_stack = 0
            self._eat(")")
        elif next_token == "[":
            self._eat(token, advance=False, category="class", meaning="expression")
            self.tokenizer.token = next_token
            self._eat("[")
            self._compile_expression()
            self._eat("]")

    def _compile_expression_list(self, method=False) -> None:
        """
        Compiles expression list.
        """
        self.file_obj.write(" " * self.indent + "<expressionList>\n")
        self._increase_indent()
        if self.tokenizer.token != ")":
            self.items_pushed_on_stack += 1
            self._compile_expression()
            while self.tokenizer.token == ",":
                self._eat(",")
                self.items_pushed_on_stack += 1
                self._compile_expression()
        self._decrease_indent()
        self.file_obj.write(" " * self.indent + "</expressionList>\n")

    def _compile_var_dec(self) -> None:
        """
        Compiles variable declaration.
        """
        self.file_obj.write(" " * self.indent + "<varDec>\n")
        self._increase_indent()
        kind = "local"
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
                self.label_counter += 1
                self._compile_while()
            elif self.tokenizer.token == "if":
                self.label_counter += 1
                self._compile_if()
        self.file_obj.write(" " * self.indent + "</statements>\n")

    def _compile_if(self) -> None:
        """
        Compiles if statement.
        """
        self._increase_indent()
        self.file_obj.write(" " * self.indent + "<ifStatement>\n")
        self._increase_indent()
        label_else = f"{self.function_name}{self.label_counter}"
        self._eat("if")
        self._eat("(")
        self._compile_expression()
        self._eat(")")
        self.vmwriter.write_arithmetic("~")
        self.vmwriter.write_if(label_else)
        self._eat("{")
        self._compile_statements()
        self.label_counter += 1
        label_endif = f"{self.function_name}{self.label_counter}"
        self.vmwriter.write_goto(label_endif)
        self._eat("}")
        self.vmwriter.write_label(label_else)
        if self.tokenizer.token == "else":
            self._eat("else")
            self._eat("{")
            self._compile_statements()
            self._eat("}")
        self.vmwriter.write_label(label_endif)
        self._decrease_indent()
        self.file_obj.write(" " * self.indent + "</ifStatement>\n")
        self._decrease_indent()

    def _compile_let(self) -> None:
        """
        Compiles let statements.
        """
        array_expression = False
        self._increase_indent()
        self.file_obj.write(" " * self.indent + f"<letStatement>\n")
        self._increase_indent()
        self._eat("let")
        varname = self.tokenizer.token
        varname_index = self._search_for_index(varname)
        varname_category = self._search_for_category(varname)
        self._compile_var_name(category=varname_category, meaning="assign")
        if self.tokenizer.token == "[":
            array_expression = True
            self._eat("[")
            self._compile_expression()
            self._eat("]")
            self.vmwriter.write_push(varname_category, varname_index)
            self.vmwriter.write_arithmetic("+")
        self._eat("=")
        self._compile_expression()
        self._eat(";")
        self._decrease_indent()
        if self.constructor:
            self.vmwriter.write_pop("this", varname_index)
        elif varname_category == "field":
            self.vmwriter.write_pop("this", varname_index)
        elif array_expression:
            self.vmwriter.write_pop("temp", 0)
            self.vmwriter.write_pop("pointer", 1)
            self.vmwriter.write_push("temp", 0)
            self.vmwriter.write_pop("that", 0)
            #self.vmwriter.write_pop(varname_category, varname_index)
        else:
            self.vmwriter.write_pop(varname_category, varname_index)
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
        self.vmwriter.write_pop("temp", 0)
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
        else:
            self.vmwriter.write_push("constant", 0)
        self.vmwriter.write_return()
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
        label_endwhile = f"{self.function_name}{self.label_counter}"
        self.label_counter += 1
        label_while = f"{self.function_name}{self.label_counter}"
        self.vmwriter.write_label(label_while)
        self._eat("while")
        self._eat("(")
        self._compile_expression()
        self._eat(")")
        self.vmwriter.write_arithmetic("~")
        self.vmwriter.write_if(label_endwhile)
        self._eat("{")
        self._compile_statements()
        self.vmwriter.write_goto(label_while)
        self._eat("}")
        self.vmwriter.write_label(label_endwhile)
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
            self.vmwriter.write_arithmetic(op)
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

        if varname_classification == "integerConstant":
            self.vmwriter.write_push("constant", int(varname))
            self._eat(varname, advance=False, classification=varname_classification)
            self.tokenizer.token = next_token
        elif varname_classification == "stringConstant":
            removed_quotes = varname.strip('"')
            string_length = len(removed_quotes)
            self.vmwriter.write_push("constant", string_length)
            self.vmwriter.write_call("String.new", 1)
            for char in removed_quotes:
                ascii = ord(char)
                self.vmwriter.write_push("constant", ascii)
                self.vmwriter.write_call("String.appendChar", 2)
            self._eat(varname, advance=False, classification=varname_classification)
            self.tokenizer.token = next_token
        elif varname == "null":
            self._eat(varname, advance=False, classification=varname_classification)
            self.tokenizer.token = next_token
        elif varname == "this":
            self.vmwriter.write_push("pointer", 0)
            self._eat(varname, advance=False, classification=varname_classification)
            self.tokenizer.token = next_token
        elif varname == "true":
            self.vmwriter.write_push("constant", 1)
            self.vmwriter.write_negation()
            self._eat(varname, advance=False, classification=varname_classification)
            self.tokenizer.token = next_token
        elif varname == "false":
            self.vmwriter.write_push("constant", 0)
            self._eat(varname, advance=False, classification=varname_classification)
            self.tokenizer.token = next_token
        elif varname == "(":
            self._eat("(", advance=False, classification=varname_classification)
            self.tokenizer.token = next_token
            self._compile_expression()
            self._eat(")")
        elif varname == "-":
            self._eat(varname, advance=False, classification=varname_classification)
            self.tokenizer.token = next_token
            self._compile_term()
            self.vmwriter.write_negation()
        elif varname == "~":
            self._eat(varname, advance=False, classification=varname_classification)
            self.tokenizer.token = next_token
            self._compile_term()
            self.vmwriter.write_arithmetic("~")
        elif varname_classification == "identifier" and next_token == "[":
            self.tokenizer.token = next_token
            self._eat("[")
            self._compile_expression()
            self._eat("]")
            self._eat(
                varname,
                advance=False,
                classification="identifier",
                category="variable",
                meaning="expression",
            )
            self.vmwriter.write_arithmetic("+")
            self.vmwriter.write_pop("pointer", 1)
            self.vmwriter.write_push("that", 0)
        elif varname_classification == "identifier" and next_token == ".":
            class_name = varname
            self._eat(
                varname,
                advance=False,
                classification="identifier",
                category="class",
                meaning="expression",
            )
            self.tokenizer.token = next_token
            self._eat(".")
            self.function_name = self.tokenizer.token
            self._compile_subroutine_name()
            self._eat("(")
            self._compile_expression_list()
            self._eat(")")
            if class_name in self.class_symbol_table.table:
                type = self.class_symbol_table.type_of(class_name)
                self.items_pushed_on_stack += 1
                self.vmwriter.write_call(f"{type}.{self.function_name}",
                        self.items_pushed_on_stack)
            else:
                self.vmwriter.write_call(f"{class_name}.{self.function_name}",
                        self.items_pushed_on_stack)
            self.items_pushed_on_stack = 0
        elif varname_classification == "identifier" and next_token == "(":
            self._eat(
                varname,
                advance=False,
                classification="identifier",
                category="subroutine",
                meaning="expression",
            )
            self.tokenizer.token = next_token
            self._eat("(")
            self._compile_expression_list()
            self._eat(")")
        elif varname_classification == "identifier":
            self._eat(
                varname,
                advance=False,
                classification="identifier",
                category="",
                meaning="expression",
            )
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

        if classification == "identifier":
            self._handle_identifier(token, classification, **kwargs)
        else:
            self.file_obj.write(" " * self.indent + f"<{classification}>")
            self.file_obj.write(f" {token} ")
            self.file_obj.write(f"</{classification}>\n")

        if advance:
            self.tokenizer.advance()

    def _handle_identifier(self, token, classification, **kwargs):
        if token in self.routine_symbol_table.table or \
                token in self.class_symbol_table.table:
            meaning = kwargs.get("meaning")
            category = (
                self.class_symbol_table.kind_of(token)
                or self.routine_symbol_table.kind_of(token)
                or kwargs["category"]
            )
            running_index = self.class_symbol_table.index_of(
                token
            ) or self.routine_symbol_table.index_of(token)
            self.file_obj.write(
                " " * self.indent + f'<{classification} category="{category}" '
                f'index="{running_index}" meaning="{meaning}">'
            )
            self.file_obj.write(f" {token} ")
            self.file_obj.write(f"</{classification}>\n")

            if meaning == "expression":
                if category == "field":
                    self.vmwriter.write_push("this", int(running_index))
                else:
                    self.vmwriter.write_push(category, int(running_index))
        else:
            category = kwargs["category"]
            self.file_obj.write(
                " " * self.indent + f'<{classification} category="{category}">'
            )
            self.file_obj.write(f" {token} ")
            self.file_obj.write(f"</{classification}>\n")

    def _search_for_index(self, varname: str):
        return self.routine_symbol_table.index_of(
            varname
        ) or self.class_symbol_table.index_of(varname)

    def _search_for_category(self, varname: str):
        return self.routine_symbol_table.kind_of(
            varname
        ) or self.class_symbol_table.kind_of(varname)

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
        self.vmwriter = VMWriter(dirname, output_name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Clean up by closing all references to the open file.
        """
        if self.file_obj:
            self.file_obj.close()
        if self.vmwriter.fp:
            self.vmwriter.fp.close()
