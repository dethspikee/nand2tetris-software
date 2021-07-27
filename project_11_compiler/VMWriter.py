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
        if command == "*":
            self.write_call("Math.multiply", 2);
        elif command == "/":
            self.write_call("Math.divide", 2);
        else:
            commands = {
                "+": "add",
                "-": "sub",
                "=": "eq",
                "<": "lt",
                ">": "gt",
                "&": "and",
                "~": "not",
            }
            self.fp.write(f"{commands[command]}\n")

    def write_negation(self) -> None:
        """
        Todo
        """
        self.fp.write("neg\n")

    def write_label(self, label: str) -> None:
        """
        Writes a VM label command.
        """
        self.fp.write(f"label {label}\n")
    
    def write_goto(self, label: str) -> None:
        """
        Writes a VM goto command.
        """
        self.fp.write(f"goto {label}\n")

    def write_if(self, label: str) -> None:
        """
        Writes a VM if-goto command.
        """
        self.fp.write(f"if-goto {label}\n")

    def write_call(self, name: str, nArgs: int) -> None:
        """
        Writes a VM call command.
        """
        self.fp.write(f"call {name} {nArgs}\n")

    def write_function(self, name: str, nLocal: str) -> None:
        """
        Wrotes a VM function command.
        """
        self.fp.write(f"function {name} {nLocal}\n")

    def write_return(self) -> None:
        """
        Writes a VM return command.
        """
        self.fp.write("return\n")
    
    def close(self) -> None:
        """
        Closes the output file.
        """
        pass
