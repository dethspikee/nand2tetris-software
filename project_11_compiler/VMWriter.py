class VMWriter:
    def __init__(self, input_stream):
        self.fp = input_stream

    def write_push(segment: str, index: int) -> None:
        """
        Writes a VM push command.
        """
        pass

    def write_pop(segment: str, index: int) -> None:
        """
        Writes a VM pop command.
        """
        pass

    def write_arithmetic(command: str) -> None:
        """
        Writes a VM arithmetic-logical command.
        """
        pass

    def write_label(label: str) -> None:
        """
        Writes a VM label command.
        """
        pass
    
    def write_goto(label: str) -> None:
        """
        Writes a VM goto command.
        """
        pass

    def write_if(label: str) -> None:
        """
        Writes a VM if-goto command.
        """
        pass

    def write_call(name: str, nArgs: int) -> None:
        """
        Writes a VM call command.
        """
        pass

    def write_function(name: str, nLocal: str) -> None:
        """
        Wrotes a VM function command.
        """
        pass

    def write_return() -> None:
        """
        Writes a VM return command.
        """
        pass
    
    def close() -> None:
        """
        Closes the output file.
        """
        pass
