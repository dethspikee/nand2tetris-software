from typing import Generator
import re
import os


class JackTokenizer:
    """
    Class responsible for grouping characters from the
    input stream into tokens.

    Attributes
    ----------
    file_obj      :: TextWrapper
                     reference to the opened input stream.
    tokens        :: generator
                     yielding next token(s)
    token         :: str
                     reference to the current token. In the beginning
                     token is None.
    """

    def __init__(self, input_stream) -> None:
        """
        Opens the input .jack file and gets
        ready to tokenize it.
        """
        self.file_obj = open(input_stream, "rt")
        self.tokens = self._generate_tokens()
        self.token = None

    def _remove_comments(self) -> str:
        """
        Traverse through the input stream
        and remove all the comments from it;
        including the inline comments. Return
        joined string that will be used by the
        'get_tokens' method to retrieve all tokens.
        """
        no_comments = []
        for line in self.file_obj:
            stripped = line.strip("\t\n ")
            if stripped.startswith(("//", "/**", "*", "*/", '/*')):
                continue
            try:
                start_of_comment = stripped.index("//")
                stripped = stripped[:start_of_comment]
            except ValueError:
                pass
            no_comments.append(stripped)

        return "".join(no_comments)

    def _generate_tokens(self) -> Generator[str, None, None]:
        """
        Tokenize (generate tokens from) the input
        stream. Return list of tokens.
        """
        strings = r"\"(.*?)\""
        names = r"[a-zA-Z_][a-zA-Z_0-9]*"
        numbers = r"\d+"
        whitespace = r"(?P<WHITESPACE>)\s+"
        jack_tokens = r"[(+?.~\-/\){},<>*;=&|\[\]]"

        master_pat = re.compile(
            "|".join([names, numbers, whitespace, jack_tokens, strings])
        )
        text = self._remove_comments()
        scanner = master_pat.scanner(text)
        for match in iter(scanner.match, None):
            if match.lastgroup != "WHITESPACE":
                token = match.group()
                yield token

    def has_tokens(self) -> bool:
        """
        Check if there are more tokens
        in the input stream.
        """
        return self.advance()

    def advance(self) -> None:
        """
        Gets the next token from the input,
        and makes it the current token.

        This method should be only called if
        has_more_tokens is true.

        Initially there is no current token.
        """
        try:
            self.token = next(self.tokens)
            return True
        except StopIteration:
            return False

    def token_type(self) -> str:
        """
        Returns type of current token,
        as a constant.
        """
        keywords = {
            "class",
            "constructor",
            "function",
            "method",
            "field",
            "static",
            "var",
            "int",
            "char",
            "boolean",
            "void",
            "true",
            "true",
            "false",
            "null",
            "this",
            "let",
            "do",
            "if",
            "else",
            "while",
            "return",
        }
        symbols = {
            "{",
            "}",
            "(",
            ")",
            "[",
            "]",
            ".",
            ",",
            ";",
            "+",
            "-",
            "*",
            "/",
            "&",
            "|",
            "<",
            ">",
            "=",
            "~",
        }
        if self.token in keywords:
            return "KEYWORD"
        if self.token in symbols:
            return "SYMBOL"
        if self.token.startswith('"') and self.token.endswith('"'):
            return "STRING_CONST"
        if self.token.isnumeric():
            return "INT_CONST"
        else:
            return "IDENTIFIER"

    def _keyword(self) -> str:
        """
        Returns the keyword which is the current,
        as a constant.

        This method should be called only if token_type
        is KEYWORD
        """
        return self.token.upper()

    def _symbol(self) -> str:
        """
        Returns the character which is the current token.
        Should only be called if token_type is SYMBOL.
        """
        return self.token

    def _identifier(self) -> str:
        """
        Returns the identifier which is the current token.
        Should only be called if token_type is IDENTIFIER.
        """
        return self.token

    def _int_val(self) -> int:
        """
        Returns the integer value of the current token.
        Should only be called if token_type is INT_CONST.
        """
        return int(self.token)

    def _string_val(self) -> str:
        """
        Returns the string value of the current token.
        Should only be called if token_type is STRING_CONST.

        The string value returned will have double quotes removed.
        Reasoning below:

        As per the specification string values must be presented without
        the surrounding double quotes.
        """
        copy = self.token
        return copy.replace('"', "")

    def get_token_classification(self) -> str:
        """
        Return classification needed for the XML output.
        """
        if self.token_type() == "KEYWORD":
            return "keyword"
        if self.token_type() == "SYMBOL":
            return "symbol"
        if self.token_type() == "INT_CONST":
            return "integerConstant"
        if self.token_type() == "STRING_CONST":
            return "stringConstant"
        if self.token_type() == "IDENTIFIER":
            return "identifier"

    def test(self):
        """
        Calling this method will result in writing new .xml file
        containing the following structure:
        <tokens>
            <token classification> token </token class>
        </tokens>

        Method used for debugging purposes.
        """
        basename = os.path.basename(self.file_obj.name)
        output_name = basename.split(".")[0]
        with open(f"{output_name}T.xml", "wt", encoding="utf-8") as fp:
            fp.write("<tokens>\n")
            while self.has_tokens():
                classification = self._get_token_classification()
                if self.token_type() == "STRING_CONST":
                    token = self.token.replace('"', "").strip(" ")
                elif self.token == "<":
                    token = "&lt;"
                elif self.token == ">":
                    token = "&gt;"
                elif self.token == '"':
                    token = "&quot;"
                elif self.token == "&":
                    token = "&amp;"
                else:
                    token = self.token
                fp.write(
                    f"\t<{self._get_token_classification()}> {token} </{self._get_token_classification()}>\n"
                )
            fp.write("</tokens>\n")
