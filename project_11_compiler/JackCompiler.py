import os
import sys


def main():
    if len(sys.argv) != 2:
        print("Illegal number of arguments. (1 required)")
        print("Path to .jack file or dir with .jack files required.")
        sys.exit(2)

    program_arg = sys.argv[1]
    if os.path.isdir(program_arg):
        print("Directory!")
        sys.exit(0)
    elif program_arg.endswith(".jack"):
        print("File!")
        sys.exit(0)
    else:
        print("Couldn't find .jack file(s)")
        sys.exit(1)


if __name__ == "__main__":
    main()
