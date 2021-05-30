class JackTokenizer:
    def __init__(self, input_stream) -> None:
        """
        Opens the input .jack file and gets
        ready to tokenize it.
        """
        self.fp = open(input_stream, 'rt')
        self.tokens = []

    def remove_comments(self) -> str:
        """
        Traverse through the input stream
        and remove all the comments from it;
        including the inline comments. Return
        joined string that will be used by the
        'get_tokens' method to retrieve all tokens.
        """
        no_comments = []
        for line in self.fp:
            if line.startswith(('//', '/**')):
                continue
            stripped = line.strip('\t\n ')
            try:
                start_of_comment = stripped.index('//')
                stripped = stripped[:start_of_comment]
            except ValueError:
                pass
            no_comments.append(stripped)

        joined = ''.join(no_comments)
        return joined

    def get_tokens(self) -> list:
        """
        Get tokens from the input stream.
        """
        pass
                


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
