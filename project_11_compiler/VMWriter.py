import os


class VMWriter:
    def __init__(self, dirname, output_name):
        self.fp = open(
            f"{os.path.join(dirname, output_name)}.vm", "wt", encoding="utf-8"
        )

    def write_push(self, segment: str, index: int) -> None:
        """
        Writes a VM push command.
        """
        self.fp.write(f"push {segment} {index}\n")

    def write_pop(self, segment: str, index: int) -> None:
        """
        Writes a VM pop command.
        """
        self.fp.write(f"pop {segment} {index}\n")

    def write_arithmetic(self, command: str) -> None:
        """
        Writes a VM arithmetic-logical command.
        """
        self.fp.write(f"{command}\n")

    def write_label(self, label: str) -> None:
        """
        Writes a VM label command.
        """
        pass
    
    def write_goto(self, label: str) -> None:
        """
        Writes a VM goto command.
        """
        pass

    def write_if(self, label: str) -> None:
        """
        Writes a VM if-goto command.
        """
        pass

    def write_call(self, name: str, nArgs: int) -> None:
        """
        Writes a VM call command.
        """
        pass

    def write_function(self, name: str, nLocal: str) -> None:
        """
        Wrotes a VM function command.
        """
        pass

    def write_return(self) -> None:
        """
        Writes a VM return command.
        """
        pass
    
    def close(self) -> None:
        """
        Closes the output file.
        """
        pass
