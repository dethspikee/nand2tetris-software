class JackTokenizer:
    def __init__(self, input_stream) -> None:
        """
        Opens the input .jack file and gets
        ready to tokenize it.
        """
        self.fp = open(input_stream, 'rt')

    def has_more_tokens() -> bool:
        """
        Check if there are more tokens
        in the input stream.
        """
        pass

    def advance() -> None:
        """
        Gets the next token from the input,
        and makes it the current token.

        This method should be only called if
        has_more_tokens is true.

        Initially there is no current token.
        """
        pass

    def token_type() -> str:
        """
        Returns type of current token,
        as a constant.
        """
        pass

    def keyword() -> str:
        pass

    def symbol() -> str:
        pass

    def identifier() -> str:
        pass

    def int_val() -> int:
        pass

    def str_val() -> str:
        pass
