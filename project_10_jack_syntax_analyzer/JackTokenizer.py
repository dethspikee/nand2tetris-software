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
    tokens        :: list
                     of all tokens needed for the parsing.
    """

    def __init__(self, input_stream) -> None:
        """
        Opens the input .jack file and gets
        ready to tokenize it.
        """
        self.file_obj = open(input_stream, "rt")
        self.tokens = list(self.generate_tokens())

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
            if line.startswith(("//", "/**")):
                continue
            stripped = line.strip("\t\n ")
            try:
                start_of_comment = stripped.index("//")
                stripped = stripped[:start_of_comment]
            except ValueError:
                pass
            no_comments.append(stripped)

        joined = "".join(no_comments)
        return joined

    def generate_tokens(self) -> Generator[str, None, None]:
        """
        Tokenize (generate tokens from) the input
        stream. Return list of tokens.
        """
        variables = r"[a-zA-Z_][a-zA-Z_0-9]*"
        numbers = r"\d+"
        whitespace = r"\s+"
        jack_tokens = r'[(+?.~\-/\){},<>*:;="&|\[\]]'

        master_pat = re.compile("|".join([variables, numbers, whitespace, jack_tokens]))
        text = self.remove_comments()
        scanner = master_pat.scanner(text)
        for match in iter(scanner.match, None):
            token = match.group()
            yield token

    def has_more_tokens(self) -> bool:
        """
        Check if there are more tokens
        in the input stream.
        """
        pass

    def advance(self) -> None:
        """
        Gets the next token from the input,
        and makes it the current token.

        This method should be only called if
        has_more_tokens is true.

        Initially there is no current token.
        """
        pass

    def token_type(self) -> str:
        """
        Returns type of current token,
        as a constant.
        """
        pass

    def keyword(self) -> str:
        pass

    def symbol(self) -> str:
        pass

    def identifier(self) -> str:
        pass

    def int_val(self) -> int:
        pass

    def str_val(self) -> str:
        pass
