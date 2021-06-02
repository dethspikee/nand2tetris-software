from typing import Generator
import re


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
    """

    def __init__(self, input_stream) -> None:
        """
        Opens the input .jack file and gets
        ready to tokenize it.
        """
        self.file_obj = open(input_stream, "rt")
        self.tokens = self.generate_tokens()
        self.current_token = None

    def remove_comments(self) -> str:
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
            if stripped.startswith(("//", "/**")):
                continue
            try:
                start_of_comment = stripped.index("//")
                stripped = stripped[:start_of_comment]
            except ValueError:
                pass
            no_comments.append(stripped)

        return "".join(no_comments)

    def generate_tokens(self) -> Generator[str, None, None]:
        """
        Tokenize (generate tokens from) the input
        stream. Return list of tokens.
        """
        strings = r"\"(.+?)\""
        names = r"[a-zA-Z_][a-zA-Z_0-9]*"
        numbers = r"\d+"
        whitespace = r"(?P<WHITESPACE>)\s+"
        jack_tokens = r"[(+?.~\-/\){},<>*;=&|\[\]]"

        master_pat = re.compile(
            "|".join([names, numbers, whitespace, jack_tokens, strings])
        )
        text = self.remove_comments()
        scanner = master_pat.scanner(text)
        for match in iter(scanner.match, None):
            if match.lastgroup != "WHITESPACE":
                token = match.group()
                yield token

    def has_more_tokens(self) -> bool:
        """
        Check if there are more tokens
        in the input stream.
        """
        return self._advance()

    def _advance(self) -> None:
        """
        Gets the next token from the input,
        and makes it the current token.

        This method should be only called if
        has_more_tokens is true.

        Initially there is no current token.
        """
        try:
            self.current_token = next(self.tokens)
            return True
        except StopIteration:
            return False

    def _token_type(self) -> str:
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
        if self.current_token in keywords:
            return "KEYWORD"
        if self.current_token in symbols:
            return "SYMBOL"
        if self.current_token.startswith('"') and self.current_token.endswith('"'):
            return "STRING_CONST"
        if self.current_token.isnumeric():
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
        return self.current_token.upper()

    def _symbol(self) -> str:
        """
        Returns the character which is the current token.
        Should only be called if token_type is SYMBOL.
        """
        return self.current_token.upper()

    def identifier(self) -> str:
        pass

    def int_val(self) -> int:
        pass

    def str_val(self) -> str:
        pass
