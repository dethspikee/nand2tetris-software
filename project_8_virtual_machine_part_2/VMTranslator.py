import sys
import os


def main():
    """
    Open file containing VM commands and translate it
    into assembly code.
    <file.vm> -> <file.asm>
    """
    if len(sys.argv) != 2:
        print('Translate .vm files into assembly instruction')
        print('Incorrent number of arguments (1 required).\n')
        print('usage: python3 VMTranslator <input_file.vm>/<input_folder>\n')
        sys.exit(1)

    with Parser(sys.argv[1]) as vmtranslator:
        vmtranslator.parse()
         

class Parser:

    def __init__(self, source):
        """
        Initialize Parser instances with path to file/directory.
        """
        self.source = source
        self.is_dir = None

    def parse(self):
        """
        Retrieve all commands from the source file(s);
        and all arguments.
        """
        translator = Translator(self.target)
        if len(self.files) > 1:
            translator.write_init()
        for file_ in self.files:
            try:
                counter = 0
                translator.current_file = file_
                fp = open(file_, 'rt')
                for line in fp.readlines():
                    if line[:2] in {'\n', '//'}:
                        continue
                    line_rstrip = line.rstrip('\n')
                    arg_1 = ''
                    arg_2 = ''
                    command_type = self.get_command_type(line_rstrip)
                    if command_type != 'C_RETURN':
                        arg_1 = self.get_argument_1(line_rstrip)
                    if command_type in {'C_PUSH', 'C_POP', 
                                        'C_FUNCTION', 'C_CALL'}:
                        arg_2 = self.get_argument_2(line_rstrip)
                    translator.translate(command_type, arg_1, arg_2, counter,
                                         self.source)
                    counter += 1
            finally:
                fp.close()

    def get_command_type(self, command: str) -> str:
        """
        Return command type based on the command received.
        """
        commands = {
                'add': 'C_ARITHMETIC',
                'sub': 'C_ARITHMETIC',
                'neg': 'C_ARITHMETIC',
                'eq': 'C_ARITHMETIC',
                'gt': 'C_ARITHMETIC',
                'lt': 'C_ARITHMETIC',
                'and': 'C_ARITHMETIC',
                'or': 'C_ARITHMETIC',
                'not': 'C_ARITHMETIC',
                'push': 'C_PUSH',
                'pop': 'C_POP',
                'label': 'C_LABEL',
                'goto': 'C_GOTO',
                'if-goto': 'C_IF',
                'function': 'C_FUNCTION',
                'return': 'C_RETURN',
                'call': 'C_CALL',
        }
        command = command.split()[0]
        return commands[command]

    def get_argument_1(self, command: str) -> str:
        """
        Return first argument of the command received;
        return command itself if C_ARITHMETIC.
        """
        argument = command.split()
        if argument[0] in {'add', 'sub', 'lt', 'eq', 'gt', 'not'}:
            return argument[0]
        else:
            return argument[1]

    def get_argument_2(self, command: str) -> int:
        """
        Return second argument of the command received;
        converted to int.
        """
        SECOND_ARGUMENT = 2
        argument = command.split()[SECOND_ARGUMENT]
        return int(argument)

    def __enter__(self):
        self.files = []
        if os.path.isdir(self.source):
            self.is_dir = True
            for file_ in os.listdir(self.source):
                if '.vm' in file_:
                    file_ = os.path.join(self.source, file_)
                    self.files.append(file_)
            filepath = os.path.join('.', self.source, f'{self.source}.asm')
            self.target = open(f'{filepath}', 'wt')
        elif '.vm' in self.source:
            self.files.append(self.source)
            name, extension = self.source.split('.')
            self.target = open(f'{name}.asm', 'wt')
        else:
            print('Problem opening input file.')
            print('Only .vm files are accepted')
            sys.exit(1)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value is None:
            print('.asm file created succesfully')
        self.target.close()


class Translator:

    def __init__(self, fp):
        """
        Initialize Translator instance. Receive file pointer to output file.
        """
        self.fp = fp
        self.current_file = None

    def translate(self, command_type, arg_1, arg_2, counter, filename) -> None:
        """
        Delegate translation of commands based on their command type.
        """
        if command_type == 'C_ARITHMETIC':
            self.write_arithmetic(arg_1, counter)
        elif command_type in {'C_PUSH', 'C_POP'}:
            self.write_push_pop(command_type, arg_1, arg_2, counter, filename)
        elif command_type == 'C_LABEL':
            self.write_label(command_type, arg_1, filename)
        elif command_type == 'C_IF':
            self.write_if(command_type, arg_1, filename)
        elif command_type == 'C_GOTO':
            self.write_goto(command_type, arg_1, filename)
        elif command_type == 'C_CALL':
            self.write_call(arg_1, arg_2, counter)
        elif command_type == 'C_FUNCTION':
            self.write_function(arg_1, arg_2)
        elif command_type == 'C_RETURN':
            self.write_return()

    def write_init(self) -> None:
        """
        Change later.
        """
        self.fp.write('@256\n')
        self.fp.write('D=A\n')
        self.fp.write('@SP\n')
        self.fp.write('M=D\n')
        self.write_call('Sys.init', 0, -1)

    def write_label(self, command_type, arg_1, filename) -> None:
        """
        Writes assembly code that effects
        the label command.
        """
        filename = filename.split('.')[0]
        if '/' in filename:
            filename = filename.split('/')[-1]
        label = f'({filename}${arg_1})\n'
        self.fp.write(label)

    def write_if(self, command_type, arg_1, filename) -> None:
        """
        Writes assembly code that effects
        the if-goto command.
        """
        filename = filename.split('.')[0]
        if '/' in filename:
            filename = filename.split('/')[-1]
        label = f'@{filename}${arg_1}\n'
        self.fp.write('@SP\n')
        self.fp.write('AM=M-1\n')
        self.fp.write('D=M\n')
        self.fp.write(label)
        self.fp.write('D;JNE\n')

    def write_goto(self, command_type, arg_1, filename) -> None:
        """
        Writes assembly code that effects
        the goto command.
        """
        filename = filename.split('.')[0]
        if '/' in filename:
            filename = filename.split('/')[-1]
        label = f'@{filename}${arg_1}\n'
        self.fp.write(label)
        self.fp.write('0;JMP\n')

    def write_call(self, function_name, num_args, counter) -> None:
        """
        Write later.
        """
        # generate return label
        return_label = function_name.split('.')[0]
        return_label = f'{return_label}$ret.{counter + 1}'

        # push return address onto the stack
        self.fp.write(f'@{return_label}\n')
        self.fp.write('D=A\n')
        self.fp.write('@SP\n')
        self.fp.write('A=M\n')
        self.fp.write('M=D\n')
        self.fp.write('@SP\n')
        self.fp.write('M=M+1\n')
        # save LCL of the caller
        self.fp.write('@LCL\n')
        self.fp.write('D=M\n')
        self.fp.write('@SP\n')
        self.fp.write('A=M\n')
        self.fp.write('M=D\n')
        self.fp.write('@SP\n')
        self.fp.write('M=M+1\n')
        # save ARG of the caller
        self.fp.write('@ARG\n')
        self.fp.write('D=M\n')
        self.fp.write('@SP\n')
        self.fp.write('A=M\n')
        self.fp.write('M=D\n')
        self.fp.write('@SP\n')
        self.fp.write('M=M+1\n')
        # save THIS of the caller
        self.fp.write('@THIS\n')
        self.fp.write('D=M\n')
        self.fp.write('@SP\n')
        self.fp.write('A=M\n')
        self.fp.write('M=D\n')
        self.fp.write('@SP\n')
        self.fp.write('M=M+1\n')
        # save THAT of the caller
        self.fp.write('@THAT\n')
        self.fp.write('D=M\n')
        self.fp.write('@SP\n')
        self.fp.write('A=M\n')
        self.fp.write('M=D\n')
        self.fp.write('@SP\n')
        self.fp.write('M=M+1\n')
        # reposition ARG
        self.fp.write('@SP\n')
        self.fp.write('D=M\n')
        self.fp.write(f'@{5 + num_args}\n')
        self.fp.write('D=D-A\n')
        self.fp.write('@ARG\n')
        self.fp.write('M=D\n')
        # reposition LCL
        self.fp.write('@SP\n')
        self.fp.write('D=M\n')
        self.fp.write(f'@LCL\n')
        self.fp.write('M=D\n')
        # transfer control to the called function
        self.fp.write(f'@{function_name}\n')
        self.fp.write('0;JMP\n')
        # declare label for the return addresss
        self.fp.write(f'({return_label})\n')

    def write_function(self, arg_1, arg_2) -> None:
        """
        Change later
        """
        self.fp.write(f'({arg_1})\n')
        while arg_2 > 0:
            self.handle_constant_push(0)
            arg_2 -= 1

    def write_return(self) -> None:
        """
        Change later.
        """
        # copy LCL to endFrame
        self.fp.write('@LCL\n')
        self.fp.write('D=M\n')
        self.fp.write('@endFrame\n')
        self.fp.write('M=D\n')
        # get the return address; store it in retAddr
        self.fp.write('@5\n')
        self.fp.write('A=D-A\n')
        self.fp.write('D=M\n')
        self.fp.write('@retAddr\n')
        self.fp.write('M=D\n')
        # reposition the return value for the caller; *ARG = pop()
        self.fp.write('@SP\n')
        self.fp.write('AM=M-1\n')
        self.fp.write('D=M\n')
        self.fp.write('@ARG\n')
        self.fp.write('A=M\n')
        self.fp.write('M=D\n')
        # reposition SP of the caller; SP = ARG + 1
        self.fp.write('@ARG\n')
        self.fp.write('A=M\n')
        self.fp.write('D=A+1\n')
        self.fp.write('@SP\n')
        self.fp.write('M=D\n')
        # restore THAT segment of the caller
        self.fp.write('@endFrame\n')
        self.fp.write('D=M\n')
        self.fp.write('@1\n')
        self.fp.write('A=D-A\n')
        self.fp.write('D=M\n')
        self.fp.write('@THAT\n')
        self.fp.write('M=D\n')
        # restore THIS segment of the caller
        self.fp.write('@endFrame\n')
        self.fp.write('D=M\n')
        self.fp.write('@2\n')
        self.fp.write('A=D-A\n')
        self.fp.write('D=M\n')
        self.fp.write('@THIS\n')
        self.fp.write('M=D\n')
        # restore ARG segment of the caller
        self.fp.write('@endFrame\n')
        self.fp.write('D=M\n')
        self.fp.write('@3\n')
        self.fp.write('A=D-A\n')
        self.fp.write('D=M\n')
        self.fp.write('@ARG\n')
        self.fp.write('M=D\n')
        # restore LCL segment of the caller
        self.fp.write('@endFrame\n')
        self.fp.write('D=M\n')
        self.fp.write('@4\n')
        self.fp.write('A=D-A\n')
        self.fp.write('D=M\n')
        self.fp.write('@LCL\n')
        self.fp.write('M=D\n')
        # return to retAddr
        self.fp.write('@retAddr\n')
        self.fp.write('A=M\n')
        self.fp.write('0;JMP\n')

    def write_push_pop(self, command_type, segment, index, counter, filename) -> None:
        """
        Translate commands for PUSH/POP operations.
        """
        if command_type == 'C_PUSH':
            if segment in {'local', 'argument', 'this', 'that'}:
                self.handle_lcl_arg_this_that_push(segment, index);
            elif segment == 'constant':
                self.handle_constant_push(index)
            elif segment == 'pointer':
                self.handle_pointer_push(segment, index)
            elif segment == 'static':
                self.handle_static_push(segment, index, counter, filename)
            elif segment == 'temp':
                self.handle_temp_push(segment, index);
        elif command_type == 'C_POP':
            if segment in {'local', 'argument', 'this', 'that'}:
                self.handle_lcl_arg_this_that_pop(segment, index);
            elif segment == 'pointer':
                self.handle_pointer_pop(segment, index)
            elif segment == 'static':
                self.handle_static_pop(segment, index, counter, filename)
            elif segment == 'temp':
                self.handle_temp_pop(segment, index)

    def handle_constant_push(self, index) -> None:
        """
        Handle PUSH commands for constant segment.
        """
        self.fp.write(f'@{index}\n')
        self.fp.write('D=A\n')
        self.fp.write('@SP\n')
        self.fp.write('A=M\n')
        self.fp.write('M=D\n')
        self.fp.write('@SP\n')
        self.fp.write('M=M+1\n')

    def handle_lcl_arg_this_that_push(self, segment, index) -> None:
        """
        Handle translation of push commands for
        LOCAL/ARGUMENT/THIS/THAT memory segments.
        """
        segment_pointer = ''
        if segment == 'local':
            segment_pointer = 'LCL'
        elif segment == 'argument':
            segment_pointer = 'ARG'
        elif segment == 'this':
            segment_pointer = 'THIS'
        elif segment == 'that':
            segment_pointer = 'THAT'

        self.fp.write(f'@{segment_pointer}\n')
        self.fp.write('D=M\n')
        self.fp.write(f'@{index}\n')
        self.fp.write('A=D+A\n')
        self.fp.write('D=M\n')
        self.fp.write('@SP\n')
        self.fp.write('A=M\n')
        self.fp.write('M=D\n')
        self.fp.write('@SP\n')
        self.fp.write('M=M+1\n')

    def handle_lcl_arg_this_that_pop(self, segment, index) -> None:
        """
        Handle translation of pop commands for
        LOCAL/ARGUMENT/THIS/THAT memory segments.
        """
        segment_pointer = ''
        if segment == 'local':
            segment_pointer = 'LCL'
        elif segment == 'argument':
            segment_pointer = 'ARG'
        elif segment == 'this':
            segment_pointer = 'THIS'
        elif segment == 'that':
            segment_pointer = 'THAT'

        self.fp.write(f'@{segment_pointer}\n')
        self.fp.write('D=M\n')
        self.fp.write(f'@{index}\n')
        self.fp.write('D=D+A\n')
        self.fp.write('@ADDRESS\n')
        self.fp.write('M=D\n')
        self.fp.write('@SP\n')
        self.fp.write('AM=M-1\n')
        self.fp.write('D=M\n')
        self.fp.write('@ADDRESS\n')
        self.fp.write('A=M\n')
        self.fp.write('M=D\n')

    def handle_temp_push(self, segment, index) -> None:
        """
        Handle translation of push commands for
        TEMP memory segment.
        """
        segment_pointer = 5
        self.fp.write(f'@{segment_pointer}\n')
        self.fp.write('D=A\n')
        self.fp.write(f'@{index}\n')
        self.fp.write('D=D+A\n')
        self.fp.write('A=D\n')
        self.fp.write('D=M\n')
        self.fp.write('@SP\n')
        self.fp.write('A=M\n')
        self.fp.write('M=D\n')
        self.fp.write('@SP\n')
        self.fp.write('AM=M+1\n')


    def handle_temp_pop(self, segment, index) -> None:
        """
        Handle translation of pop commands for
        TEMP memory segment.
        """
        segment_pointer = 5
        self.fp.write(f'@{segment_pointer}\n')
        self.fp.write('D=A\n')
        self.fp.write(f'@{index}\n')
        self.fp.write('D=D+A\n')
        self.fp.write('@ADDRESS\n')
        self.fp.write('M=D\n')
        self.fp.write('@SP\n')
        self.fp.write('AM=M-1\n')
        self.fp.write('D=M\n')
        self.fp.write('@ADDRESS\n')
        self.fp.write('A=M\n')
        self.fp.write('M=D\n')

    def handle_pointer_push(self, segment, index) -> None:
        """
        Handle push operation for pointer segment.
        """
        segment_pointer = ''
        if index == 0:
            segment_pointer = 'THIS'
        elif index == 1:
            segment_pointer = 'THAT'

        self.fp.write(f'@{segment_pointer}\n')
        self.fp.write('D=M\n')
        self.fp.write('@SP\n')
        self.fp.write('A=M\n')
        self.fp.write('M=D\n')
        self.fp.write('@SP\n')
        self.fp.write('M=M+1\n')

    def handle_pointer_pop(self, segment, index) -> None:
        """
        Handle pop operation for pointer segment.
        """
        segment_pointer = ''
        if index == 0:
            segment_pointer = 'THIS'
        elif index == 1:
            segment_pointer = 'THAT'

        self.fp.write('@SP\n')
        self.fp.write('AM=M-1\n')
        self.fp.write('D=M\n')
        self.fp.write(f'@{segment_pointer}\n')
        self.fp.write('M=D\n')

    def handle_static_push(self, segment, index, counter, filename) -> None:
        """
        Handle STATIC segment push command.
        """
        if '/' in self.current_file:
            filename = self.current_file.split('/')[-1]
        else:
            filename = filename.split('.')[0]
        variable_name = f'{filename}.{index}'

        self.fp.write(f'@{variable_name}\n')
        self.fp.write('D=M\n')
        self.fp.write('@SP\n')
        self.fp.write('A=M\n')
        self.fp.write('M=D\n')
        self.fp.write('@SP\n')
        self.fp.write('AM=M+1\n')

    def handle_static_pop(self, segment, index, counter, filename) -> None:
        """
        Handle STATIC segment pop command.
        """
        if '/' in self.current_file:
            filename = self.current_file.split('/')[-1]
        else:
            filename = filename.split('.')[0]
        variable_name = f'{filename}.{index}'

        self.fp.write('@SP\n')
        self.fp.write('AM=M-1\n')
        self.fp.write('D=M\n')
        self.fp.write(f'@{variable_name}\n')
        self.fp.write('M=D\n')

    def handle_lt_gt_eq(self, command, counter) -> None:
        """
        Handle lt/gt/eq operations. All three commands are
        translated in a similar way. Use f-strings and counter
        to create unique loops and variables.
        """
        action_if_true = ''
        action_if_false = ''
        jump_condition = ''
        if command == 'eq':
            action_if_true = 'EQUAL'
            action_if_false = 'NOTEQUAL'
            jump_condition = 'JEQ';
        elif command == 'gt':
            action_if_true = 'GREATER'
            action_if_false = 'NOTGREATER'
            jump_condition = 'JGT';
        elif command == 'lt':
            action_if_true = 'SMALLER'
            action_if_false = 'NOTSMALLER'
            jump_condition = 'JLT';

        self.fp.write('@SP\n')
        self.fp.write('AM=M-1\n')
        self.fp.write('D=M\n')
        self.fp.write('@SP\n')
        self.fp.write('AM=M-1\n')
        self.fp.write('MD=M-D\n')
        self.fp.write(f'@{action_if_true}{counter}\n')
        self.fp.write(f'D;{jump_condition}\n')
        self.fp.write(f'@{action_if_false}{counter}\n')
        self.fp.write('0;JMP\n')
        self.fp.write(f'({action_if_true}{counter})\n')
        self.fp.write('@SP\n')
        self.fp.write('A=M\n')
        self.fp.write('M=-1\n')
        self.fp.write(f'@END{counter}\n')
        self.fp.write('0;JMP\n')
        self.fp.write(f'({action_if_false}{counter})\n')
        self.fp.write('@SP\n')
        self.fp.write('A=M\n')
        self.fp.write('M=0\n')
        self.fp.write(f'@END{counter}\n')
        self.fp.write('0;JMP\n')
        self.fp.write(f'(END{counter})\n')
        self.fp.write('@SP\n')
        self.fp.write('M=M+1\n')



    def write_arithmetic(self, command, counter) -> None:
        """
        Translate arithmetic and logical commands.
        """
        if command == 'add':
            self.fp.write('@SP\n')
            self.fp.write('AM=M-1\n')
            self.fp.write('D=M\n')
            self.fp.write('@SP\n')
            self.fp.write('AM=M-1\n')
            self.fp.write('D=D+M\n')
            self.fp.write('@SP\n')
            self.fp.write('A=M\n')
            self.fp.write('M=D\n')
            self.fp.write('@SP\n')
            self.fp.write('M=M+1\n')
        elif command == 'sub':
            self.fp.write('@SP\n')
            self.fp.write('AM=M-1\n')
            self.fp.write('D=M\n')
            self.fp.write('@SP\n')
            self.fp.write('AM=M-1\n')
            self.fp.write('MD=M-D\n')
            self.fp.write('@SP\n')
            self.fp.write('M=M+1\n')
        elif command == 'neg':
            self.fp.write('@SP\n')
            self.fp.write('AM=M-1\n')
            self.fp.write('M=-M\n')
            self.fp.write('@SP\n')
            self.fp.write('M=M+1\n')
        elif command == 'and':
            self.fp.write('@SP\n')
            self.fp.write('AM=M-1\n')
            self.fp.write('D=M\n')
            self.fp.write('@SP\n')
            self.fp.write('AM=M-1\n')
            self.fp.write('M=M&D\n')
            self.fp.write('@SP\n')
            self.fp.write('M=M+1\n')
        elif command == 'or':
            self.fp.write('@SP\n')
            self.fp.write('AM=M-1\n')
            self.fp.write('D=M\n')
            self.fp.write('@SP\n')
            self.fp.write('AM=M-1\n')
            self.fp.write('M=M|D\n')
            self.fp.write('@SP\n')
            self.fp.write('M=M+1\n')
        elif command == 'not':
            self.fp.write('@SP\n')
            self.fp.write('AM=M-1\n')
            self.fp.write('M=!M\n')
            self.fp.write('@SP\n')
            self.fp.write('M=M+1\n')
        else:
            self.handle_lt_gt_eq(command, counter)


if __name__ == '__main__':
    main()
