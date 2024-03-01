# Kosmas Apostolidis 4259 cse74259
# Konstantinos Malamas 2748 cse42748
import sys
import argparse

TOKEN_TYPES = {
    'IDENTIFIER'    : 'identifier',
    'NUMBER'        : 'number',
    'KEYWORD'       : 'keyword',
    'REL_OPERATOR'  : 'relational operator',
    'ADD_OPERATOR'  : 'add operator',
    'MUL_OPERATOR'  : 'mul operator',
    'COMMENT'       : 'comment',
    'GROUP_SYMBOL'  : 'group symbol',
    'ASSIGNMENT'    : 'assignment',
    'DELIMITER'     : 'delimiter',
    'EOF'           : 'EOF'
}
numbers = set('0123456789')
letters = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')

keywords = ['program', 'if', 'switchcase', 'not', 'function', 'input', 'declare', 'else', 'forcase', ' and',
            'procedure',
            'print', 'while', 'incase', 'or', 'call', 'case', 'return', 'default', 'in', 'inout']
groupSymbol = ['{', '}', '(', ')', '[', ']']
delimiter = [',', ';', '.']
assignment = [':=']
relOperator = ['<', '>', '>=', '<=', '<>', '=']
addOperator = ['+', '-']
mulOperator = ['*', '/']
whiteSpace = [' ', '\t', '\r', '\n']
c_file_generation_flag = 0
program_variables = []      # Helps for the generation of the .c program
program_list = []           # This list keeps all the created quads of the program
quad_label = -1             # Counts every single quad appended to program_list
temp_counter = 0            # For T_1,T_2,... etc
scope = 0                   # Depth of functions level
subprograms_list = []       # Here we keep all the subprogram names
procedure_list = []
offset = [12]               # Offset list begins at 12 bytes
startQuad = 0               # Keep the line of the first quad of a function
actual_parameter_list = []  # Keeps the actual parameters for a procedure call
formal_parameter_list = []  # Keeps the formal parameters
total_actual_parameters = 0 # It will be used to count the actual parameters
count_formal_parameters = 0 # It will be used to count the formal parameters
symbol_table = [[]]         # It stores all the information about variables,functions and procedures
main_name = ""

class Token:
    def __init__(self, token_type, token_string, line_number):
        self.token_type = token_type
        self.token_string = token_string
        self.line_number = line_number

class LexerError(Exception):
    """Custom exception class for lexer errors."""
    def __init__(self, line_number, message="Lexer error"):
        self.line_number = line_number
        self.message = f"Error at line {line_number}: {message}"
        super().__init__(self.message)

class Lexer:
    def __init__(self, input):
        self.current_token = None
        self.input = input
        self.current_char = input[0]
        self.currentPosition = 0
        self.line_number = 1

    def set_current_token(self, final_token):
        self.current_token = final_token

    def get_next_char(self):
        self.peek()
        self.currentPosition += 1
        self.current_char = self.input[self.currentPosition]
        return self.current_char

    def peek(self):
        if self.currentPosition + 1 >= len(self.input):
            if self.current_token.token_string != '.':
                raise LexerError(self.line_number, f"Error. Reached End Of File.'.'")
        else:
            return self.input[self.currentPosition + 1]
        
    #The lexical analysis
    def lex(self):
        while True:
            if self.current_char in whiteSpace:
                self.skip_white_space()
            elif self.current_char == '#':
                self.skip_comment_status()
            else:
                break
        if self.current_char in numbers:
            final_token = self.loop_number_status()
        elif self.current_char in letters:
            final_token = self.loop_identifier_status()
        elif self.current_char in addOperator:
            final_token = Token(TOKEN_TYPES["ADD_OPERATOR"], self.current_char, self.line_number)
        elif self.current_char in mulOperator:
            final_token = Token(TOKEN_TYPES["MUL_OPERATOR"], self.current_char, self.line_number)
        elif self.current_char in delimiter:
            final_token = Token(TOKEN_TYPES["DELIMITER"], self.current_char, self.line_number)
        elif self.current_char == ':':
            final_token = self.loop_assignment_status()
        elif self.current_char in groupSymbol:
            final_token = Token(TOKEN_TYPES["GROUP_SYMBOL"], self.current_char, self.line_number)
        elif self.current_char in relOperator:
            final_token = self.loop_rel_operator_status()
        elif self.current_char == '':
            final_token = Token(TOKEN_TYPES["EOF"], '', self.line_number)
        else:
            sys.exit("Invalid character on line:" + str(self.line_number))
        if final_token.token_string != '.': #todo: change ending check so that compiling doesnt end when '.' is reached and checks if later tokens are whitespace and comments only
            self.get_next_char()
        self.set_current_token(final_token)
        return final_token
    
    #Skips all the whitespaces
    def skip_white_space(self):
        while self.current_char in whiteSpace:
            if self.current_char == '\n':
                self.line_number += 1
            self.get_next_char()
            
    #This method skips all the comment section,eg \n,'' and #
    def skip_comment_status(self):
        assert self.current_char == '#', "Comment must start with #"
        while True:
            self.get_next_char()
            if self.current_char == '\n':
                self.line_number += 1
            elif self.current_char is None:
                raise LexerError("Unclosed comment at EOF.", self.line_number)
            elif self.current_char == '#':
                self.get_next_char()
                break
            
    #Checks the upper/lower bound of a number and if a number is valid
    def loop_number_status(self):
        """Validate number within bounds and construct NUMBER token."""
        positive_limit = 2 ** 32 - 1
        negative_limit = -positive_limit - 1
        number_string = ''
        while self.current_char in numbers:
            number_string += self.current_char
            if not self.peek() in numbers:
                if self.peek() in letters:
                    raise LexerError("Invalid character: letter after digit.", self.line_number)
                break
            self.get_next_char()

        num_value = int(number_string)
        if num_value > positive_limit or num_value < negative_limit:
            raise LexerError(f"Number {num_value} out of valid range.", self.line_number)
        
        return Token(TOKEN_TYPES["NUMBER"], number_string, self.line_number)

    #Checks if a name is an identifier or a keyword
    def loop_identifier_status(self):
        word = self.current_char
        while (self.peek() in letters) or (self.peek() in numbers):
            self.get_next_char()
            word += self.current_char

        if word in keywords:
            final_token = Token(TOKEN_TYPES["KEYWORD"], word, self.line_number)
        else:
            if len(word) <= 30:
                final_token = Token(TOKEN_TYPES["IDENTIFIER"], word, self.line_number)
            else:
                sys.exit("Length of IDENTIFIER > 30 letters,line" + str(self.line_number))
        return final_token

    # Checks the assignment operator token
    def loop_assignment_status(self):
        if self.peek() == '=':
            self.get_next_char()  # Consume '='
            return Token(TOKEN_TYPES["ASSIGNMENT"], ':=', self.line_number)
        else:
            raise LexerError("Expected ':=' for assignment.", self.line_number)
        
    #Checks the relational operator tokens
    def loop_rel_operator_status(self):
        pot_operator = self.current_char
        final_token = None
        if pot_operator == '=':
            final_token = Token(TOKEN_TYPES["REL_OPERATOR"], '=', self.line_number)
        elif pot_operator == '>':
            if self.peek() == '=':
                self.get_next_char()
                final_token = Token(TOKEN_TYPES["REL_OPERATOR"], '>=', self.line_number)
            else:
                final_token = Token(TOKEN_TYPES["REL_OPERATOR"], '>', self.line_number)
        elif pot_operator == '<':
            if self.peek() == '=':
                final_token = Token(TOKEN_TYPES["REL_OPERATOR"], '<=', self.line_number)
                self.get_next_char()
            elif self.peek() == '>':
                final_token = Token(TOKEN_TYPES["REL_OPERATOR"], '<>', self.line_number)
                self.get_next_char()
            else:
                final_token = Token(TOKEN_TYPES["REL_OPERATOR"], '<', self.line_number)

        return final_token

#The main of the program
def program():  # done
    global offset, main_name
    cimple_lexer.lex()
    if cimple_lexer.current_token.token_string == 'program':
        cimple_lexer.lex()
        name = ID()
        main_name = name
        block(main_name,False)
        if cimple_lexer.current_token.token_string == '.':
            genquad("halt", "_", "_", "_")
            genquad("end_block", name, "_", "_")
            #print("scope = "+str(scope)+" ,symbol table = "+str(symbol_table[scope]))
            #print(str(name) + " = " + str(offset[scope]) + " bytes")
            #symbol_table.remove(len(symbol_table) -1)
            print("Compile Completed")
        else:
            sys.exit("Error. '.' was expected , line: " + str(cimple_lexer.current_token.line_number))
    else:
        sys.exit("The keyword 'program' was expected")
#Tge block with all the declarations,subprograms and statements
def block(name, function_flag):  # done
    declarations()
    subprograms()
    genquad("begin_block", name, "_", "_")
    return_flag = statements(function_flag)
    if function_flag:
        if not return_flag:
            sys.exit("Expected return token before block " + str(cimple_lexer.current_token.line_number))

#All names followed by the declare word
def declarations(): #done
    while cimple_lexer.current_token.token_string == 'declare':
        cimple_lexer.lex()
        varlist()
        if cimple_lexer.current_token.token_string == ';':
            cimple_lexer.lex()
        else:
            sys.exit('Error. ; was expected after declaration. line:' + str(cimple_lexer.current_token.line_number))

def varlist(): #done
    global scope,offset
    if cimple_lexer.current_token.token_type == TOKEN_TYPES["IDENTIFIER"]:
        variable_name = cimple_lexer.current_token.token_string
        exists = check_multiple_variable_names_exist_at_the_same_scope_in_symbol_table(symbol_table, scope, variable_name)
        if not exists:
            variable = (variable_name, offset[scope])
            symbol_table[scope].append(variable)
            offset[scope] += 4
        else:
            sys.exit("Multiple defined " + str(variable_name) + " in line " + str(cimple_lexer.current_token.line_number))
        cimple_lexer.lex()
        while cimple_lexer.current_token.token_string == ',':
            cimple_lexer.lex()
            variable_name = ID()
            exists = check_multiple_variable_names_exist_at_the_same_scope_in_symbol_table(symbol_table,scope,variable_name)
            if not exists:
                variable = (variable_name,  offset[scope])
                symbol_table[scope].append(variable)
                offset[scope] += 4
            else:
                sys.exit("Multiple defined " + str(variable_name) + " in line " + str(cimple_lexer.current_token.line_number))

#One or more subprograms can be created
def subprograms():  # and subprogram done
    global scope, offset, startQuad  , subprograms_list , procedure_list
    while cimple_lexer.current_token.token_string == 'function' or cimple_lexer.current_token.token_string == 'procedure':
        isFunction = False
        if cimple_lexer.current_token.token_string == 'function':
            function_flag = True
            isFunction = True
        else:
            function_flag = False
        cimple_lexer.lex()
        sub_program_name = ID()
        if not function_flag:
            procedure_list.append(sub_program_name)  # Here we add the name of the subprogram to a list so that we can check if the name exists in case of a call stat
        subprograms_list.append(sub_program_name)
        tuple_name = (sub_program_name,)
        subprogram_name_exists_in_the_same_scope = check_multiple_variable_names_exist_at_the_same_scope_in_symbol_table(symbol_table,scope,sub_program_name)
        subprogram_name_exists_in_a_previous_scope = check_if_exists_in_symbol_table(symbol_table,sub_program_name)
        if not subprogram_name_exists_in_the_same_scope and not subprogram_name_exists_in_a_previous_scope:
            symbol_table[scope].append(tuple_name)
        else:
            sys.exit("Multiple defined subprogram name " + str(sub_program_name) + " in line " + str(cimple_lexer.current_token.line_number) + ".")
        add_list_to_symbol_table = []  # symbol_table is in form of a 2D list [[],[],[],[],[],....]
        symbol_table.append(add_list_to_symbol_table)
        if cimple_lexer.current_token.token_string == '(':
            cimple_lexer.lex()
            scope += 1  # Increment scope by 1
            offset.append(12)
            arguments = formalparlist()
            if cimple_lexer.current_token.token_string == ')':
                cimple_lexer.lex()
                block(sub_program_name, function_flag)
                genquad("end_block", sub_program_name, "_", "_")
                frameLength =  offset[scope]
                insert_in_symbol_table(symbol_table, sub_program_name, startQuad + 1)
                insert_in_symbol_table(symbol_table, sub_program_name, arguments)
                insert_in_symbol_table(symbol_table, sub_program_name, frameLength)
                #print(str(sub_program_name)+" = "+str(frameLength)+" bytes")
                list_of_arguments = []
                scope = scope - 1           #Decrement the scope after the end of every subprogram
                offset.pop()
            else:
                sys.exit("Error. ')' was expected. line:" + str(cimple_lexer.current_token.line_number))

        else:
            sys.exit("Error. '(' was expected. line:" + str(cimple_lexer.current_token.line_number))

#The list with the formal parameters used by a function or a procedure
def formalparlist():  # and formalparitem done
    global scope,offset,formal_parameter_list
    list_of_arguments = []
    in_reference = cimple_lexer.current_token.token_string
    if cimple_lexer.current_token.token_string == 'in':
        formal_parameter_list.append(in_reference)
        cimple_lexer.lex()
        parameter_name = ID()
        parameter1 = (parameter_name, offset[scope], "cv")
        symbol_table[scope].append(parameter1)
        list_of_arguments.append("in")
        offset[scope] += 4
        while cimple_lexer.current_token.token_string == ',':
            cimple_lexer.lex()
            in_reference = cimple_lexer.current_token.token_string
            if cimple_lexer.current_token.token_string == 'in':
                formal_parameter_list.append(in_reference)
                cimple_lexer.lex()
                parameter_name = ID()
                parameter2 = (parameter_name, offset[scope], "cv")
                exists = check_multiple_variable_names_exist_at_the_same_scope_in_symbol_table(symbol_table,scope,parameter_name)
                if not exists:
                    symbol_table[scope].append(parameter2)
                    list_of_arguments.append("in")
                    offset[scope] += 4
                else:
                    sys.exit("Redefinition of parameter " + str(parameter_name) + "in line " + str(cimple_lexer.current_token.line_number))
            elif cimple_lexer.current_token.token_string == 'inout':
                inout_reference = cimple_lexer.current_token.token_string
                formal_parameter_list.append(inout_reference)
                cimple_lexer.lex()
                parameter_name = ID()
                parameter3 = (parameter_name, offset[scope], "ref")
                exists = check_multiple_variable_names_exist_at_the_same_scope_in_symbol_table(symbol_table, scope, parameter_name)                # Each variable on the same scope must not have the same name
                if not exists:
                    symbol_table[scope].append(parameter3)
                    list_of_arguments.append("inout")
                    offset[scope] += 4
                else:
                    sys.exit("Redefinition of parameter " + str(parameter_name) + ", line: " + str(cimple_lexer.current_token.line_number))
            else:
                sys.exit("Error. 'in'/'inout' was expected. line " + str(cimple_lexer.current_token.line_number))
    elif cimple_lexer.current_token.token_string == 'inout':
        inout_reference = cimple_lexer.current_token.token_string
        formal_parameter_list.append(inout_reference)
        cimple_lexer.lex()
        parameter_name = ID()
        parameter1 = (parameter_name, offset[scope], "ref")
        symbol_table[scope].append(parameter1)
        list_of_arguments.append("inout")
        offset[scope] += 4
        while cimple_lexer.current_token.token_string == ',':
            cimple_lexer.lex()
            if cimple_lexer.current_token.token_string == 'in':
                in_reference = cimple_lexer.current_token.token_string
                formal_parameter_list.append(in_reference)
                cimple_lexer.lex()
                parameter_name = ID()
                parameter2 = (parameter_name, offset[scope], "cv")
                exists = check_multiple_variable_names_exist_at_the_same_scope_in_symbol_table(symbol_table,scope,parameter_name)
                if not exists:
                    symbol_table[scope].append(parameter2)
                    list_of_arguments.append("in")
                    offset[scope] += 4
                else:
                    sys.exit("Redefinition of parameter " + str(parameter_name) + ", line: " + str(cimple_lexer.current_token.line_number))
            elif cimple_lexer.current_token.token_string == 'inout':
                inout_reference = cimple_lexer.current_token.token_string
                formal_parameter_list.append(inout_reference)
                cimple_lexer.lex()
                parameter_name = ID()
                parameter3 = (parameter_name, offset[scope], "ref")
                exists = check_multiple_variable_names_exist_at_the_same_scope_in_symbol_table(symbol_table,scope,parameter_name)
                if not exists:
                    symbol_table[scope].append(parameter3)               # Each variable on the same scope should not be the same
                    list_of_arguments.append("inout")
                    offset[scope] += 4
                else:
                    # Else error if multiple defined names occur
                    sys.exit("Redefinition of parameter " + str(parameter_name) + ", line: " + str(cimple_lexer.current_token.line_number))
            else:
                sys.exit("Error. 'in'/'inout' was expected. line: " + str(cimple_lexer.current_token.line_number))
    else:
        sys.exit("Error. 'in'/'inout' was expected. line " + str(cimple_lexer.current_token.line_number))
    return list_of_arguments

def statements(function_flag):  # done
    return_flag = False
    if cimple_lexer.current_token.token_string == '{':
        cimple_lexer.lex()
        if statement(function_flag):
            return_flag = True
        while cimple_lexer.current_token.token_string == ';':
            cimple_lexer.lex()
            if statement(function_flag):
                return_flag = True
        if cimple_lexer.current_token.token_string == '}':
            cimple_lexer.lex()
        else:
            sys.exit("Error. '}' was expected in line " + str(cimple_lexer.current_token.line_number))
    else:
        if statement(function_flag):
            return_flag = True
        cimple_lexer.lex()
        if cimple_lexer.current_token.token_string == ';':
            cimple_lexer.lex()
        else:
            sys.exit("Error. ';' was expected in line " + str(cimple_lexer.current_token.line_number))
    return return_flag

#All cimple statements
def statement(function_flag):  # done
    global startQuad
    startQuad = quad_label
    return_flag = False
    if cimple_lexer.current_token.token_type == TOKEN_TYPES["IDENTIFIER"]:
        name = cimple_lexer.current_token.token_string
        line = cimple_lexer.current_token.line_number
        cimple_lexer.lex()
        assign_stat(name, line)
    elif cimple_lexer.current_token.token_string == 'if':
        cimple_lexer.lex()
        return_flag = if_stat(function_flag)
    elif cimple_lexer.current_token.token_string == 'while':
        cimple_lexer.lex()
        return_flag = while_stat(function_flag)
    elif cimple_lexer.current_token.token_string == 'forcase':
        cimple_lexer.lex()
        return_flag = forcase_stat(function_flag)
    elif cimple_lexer.current_token.token_string == 'switchcase':
        cimple_lexer.lex()
        return_flag = switchcase_stat(function_flag)
    elif cimple_lexer.current_token.token_string == 'incase':
        cimple_lexer.lex()
        return_flag = incase_stat(function_flag)
    elif cimple_lexer.current_token.token_string == 'print':
        cimple_lexer.lex()
        print_stat()
    elif cimple_lexer.current_token.token_string == 'return':
        if function_flag:
            return_flag = True
            cimple_lexer.lex()
            return_stat()
        else:
            sys.exit("Unexpected return token in line " + str(cimple_lexer.current_token.line_number))
    elif cimple_lexer.current_token.token_string == 'call':
        cimple_lexer.lex()
        call_stat()
    elif cimple_lexer.current_token.token_string == 'input':
        cimple_lexer.lex()
        input_stat()
    return return_flag

#If statement
def if_stat(function_flag):  # done
    return_flag = False
    if cimple_lexer.current_token.token_string == '(':
        cimple_lexer.lex()
        B_true, B_false = condition()
        backpatch(B_true, nextquad())
        if cimple_lexer.current_token.token_string == ')':
            cimple_lexer.lex()
            if statements(function_flag):
                return_flag = True
            ifList = makelist(nextquad())
            backpatch(B_false, nextquad() + 1)
            if elsepart(ifList, function_flag):
                return_flag = True
        else:
            sys.exit("Error. ')' was expected. line:" + str(cimple_lexer.current_token.line_number))
    else:
        sys.exit("Error. '(' was expected. line:" + str(cimple_lexer.current_token.line_number))
    return return_flag

#Else part of the if statement
def elsepart(ifList, function_flag):  # done
    return_flag = False
    if cimple_lexer.current_token.token_string == 'else':
        genquad("jump", "_", "_", "_")
        cimple_lexer.lex()
        return_flag = statements(function_flag)
        backpatch(ifList, nextquad())
    return return_flag

#A condition in a logical operation between two or more boolterms/boolfactors
def condition(): #done
    Q1_true, Q1_false = boolterm()
    B_true = Q1_true
    B_false = Q1_false
    while cimple_lexer.current_token.token_string == 'or':
        backpatch(B_false, nextquad())
        cimple_lexer.lex()
        Q2_true, Q2_false = boolterm()
        B_true = merge(B_true, Q2_true)
        B_false = Q2_false
    return B_true, B_false

def boolterm(): #done
    R1_true, R1_false = boolfactor()
    Q_true = R1_true
    Q_false = R1_false
    while cimple_lexer.current_token.token_string == 'and':
        backpatch(Q_true, nextquad())
        cimple_lexer.lex()
        R2_true, R2_false = boolfactor()
        Q_false = merge(Q_false, R2_false)
        Q_true = R2_true
    return Q_true, Q_false

def boolfactor(): #done
    if cimple_lexer.current_token.token_string == 'not':
        cimple_lexer.lex()
        if cimple_lexer.current_token.token_string == '[':
            cimple_lexer.lex()
            B_true, B_false = condition()
            R_true = B_false
            R_false = B_true
            if cimple_lexer.current_token.token_string == ']':
                cimple_lexer.lex()
            else:
                sys.exit("Error. ']' was expected. line:" + str(cimple_lexer.current_token.line_number))
        else:
            sys.exit("Error. '[' was expected. line:" + str(cimple_lexer.current_token.line_number))
    elif cimple_lexer.current_token.token_string == '[':
        cimple_lexer.lex()
        B_true, B_false = condition()
        R_true = B_true
        R_false = B_false
        if cimple_lexer.current_token.token_string == ']':
            cimple_lexer.lex()
        else:
            sys.exit("Error. ']' was expected. line:" + str(cimple_lexer.current_token.line_number))
    else:
        E1_place = expression()
        if cimple_lexer.current_token.token_type == TOKEN_TYPES["REL_OPERATOR"]:
            relop = cimple_lexer.current_token.token_string
            cimple_lexer.lex()
            E2_place = expression()
        else:
            sys.exit("Error. relational operator was expected. line:" + str(cimple_lexer.current_token.line_number))
        R_true = makelist(nextquad())
        genquad(relop, E1_place, E2_place, "_")  # {P1}
        R_false = makelist(nextquad())
        genquad("jump", "_", "_", "_")
    return R_true, R_false

#While statement
def while_stat(function_flag):  # done
    return_flag = False
    if cimple_lexer.current_token.token_string == '(':
        cimple_lexer.lex()
        B_quad = nextquad()
        B_true, B_false = condition()
        backpatch(B_true, nextquad())
        if cimple_lexer.current_token.token_string == ')':
            cimple_lexer.lex()
            if statements(function_flag):
                return_flag = True
            genquad("jump", "_", "_", B_quad)
            backpatch(B_false, nextquad())
        else:
            sys.exit("Error. ')' was expected. line:" + str(cimple_lexer.current_token.line_number))
    else:
        sys.exit("Error. '(' was expected. line:" + str(cimple_lexer.current_token.line_number))
    return return_flag

#Forcase statement
def forcase_stat(function_flag):  # done
    return_flag = False
    p1_quad = nextquad()
    while cimple_lexer.current_token.token_string == 'case':
        cimple_lexer.lex()
        if cimple_lexer.current_token.token_string == '(':
            cimple_lexer.lex()
            cond_true, cond_false = condition()
            backpatch(cond_true, nextquad())
            if cimple_lexer.current_token.token_string == ')':
                cimple_lexer.lex()
                if statements(function_flag):
                    return_flag = True
                genquad("jump", "_", "_", p1_quad)
                backpatch(cond_false, nextquad())
            else:
                sys.exit("Error. ')' was expected. line:" + str(cimple_lexer.current_token.line_number))
        else:
            sys.exit("Error. '(' was expected. line:" + str(cimple_lexer.current_token.line_number))
    if cimple_lexer.current_token.token_string == 'default':
        cimple_lexer.lex()
        if statements(function_flag):
            return_flag = True
    else:
        sys.exit("Error. 'default' was expected. line:" + str(cimple_lexer.current_token.line_number))
    return return_flag

#Switchcase statement
def switchcase_stat(function_flag):  # done
    return_flag = False
    exitlist = emptylist()
    while cimple_lexer.current_token.token_string == 'case':
        cimple_lexer.lex()
        if cimple_lexer.current_token.token_string == '(':
            cimple_lexer.lex()
            cond_true, cond_false = condition()
            backpatch(cond_true, nextquad())
            if cimple_lexer.current_token.token_string == ')':
                cimple_lexer.lex()
                if statements(function_flag):
                    return_flag = True
                e = makelist(nextquad())
                genquad("jump", "_", "_", "_")
                merge(exitlist, e)
                backpatch(cond_false, nextquad())
            else:
                sys.exit("Error. ')' was expected. line:" + str(cimple_lexer.current_token.line_number))
        else:
            sys.exit("Error. '(' was expected. line:" + str(cimple_lexer.current_token.line_number))
    if cimple_lexer.current_token.token_string == 'default':
        cimple_lexer.lex()
        if statements(function_flag):
            return_flag = True
        backpatch(exitlist, nextquad())
    else:
        sys.exit("Error. 'default' was expected. line:" + str(cimple_lexer.current_token.line_number))
    return return_flag

#Incase statement
def incase_stat(function_flag):  # done
    return_flag = False
    w = newtemp()
    p1_quad = nextquad()
    genquad(":=", "1", "_", w)
    while cimple_lexer.current_token.token_string == 'case':
        cimple_lexer.lex()
        if cimple_lexer.current_token.token_string == '(':
            cimple_lexer.lex()
            cond_true, cond_false = condition()
            backpatch(cond_true, nextquad())
            genquad(":=", "0", "_", w)
            if cimple_lexer.current_token.token_string == ')':
                cimple_lexer.lex()
                if statements(function_flag):
                    return_flag = True
                backpatch(cond_false, nextquad())
            else:
                sys.exit("Error. ')' was expected. line:" + str(cimple_lexer.current_token.line_number))
        else:
            sys.exit("Error. '(' was expected. line:" + str(cimple_lexer.current_token.line_number))
    genquad("=", w, "0", p1_quad)
    return return_flag

#Takes an input from the user
def input_stat(): #done
    if cimple_lexer.current_token.token_string == '(':
        cimple_lexer.lex()
        id_place = ID()
        if not program_variables.__contains__(id_place):
            program_variables.append(id_place)
        exists = check_if_exists_in_symbol_table(symbol_table,id_place)
        if not exists:
            sys.exit("Use of undeclared variable "+str(id_place)+" in line "+str(cimple_lexer.current_token.line_number))
        else:
            genquad("inp", id_place, "_", "_")
        if cimple_lexer.current_token.token_string == ')':
            cimple_lexer.lex()
        else:
            sys.exit("Error. ')' was expected. line:" + str(cimple_lexer.current_token.line_number))
    else:
        sys.exit("Error. '(' was expected. line:" + str(cimple_lexer.current_token.line_number))

#Prints an expression
def print_stat(): #done
    if cimple_lexer.current_token.token_string == '(':
        cimple_lexer.lex()
        E_place = expression()
        genquad("out", E_place, "_", "_")
        if cimple_lexer.current_token.token_string == ')':
            cimple_lexer.lex()
        else:
            sys.exit("Error. ')' was expected. line:" + str(cimple_lexer.current_token.line_number))
    else:
        sys.exit("Error. '(' was expected. line:" + str(cimple_lexer.current_token.line_number))

#Returns an expression
def return_stat(): #done
    if cimple_lexer.current_token.token_string == '(':
        cimple_lexer.lex()
        E_place = expression()
        genquad("retv", E_place, "_", "_")
        if cimple_lexer.current_token.token_string == ')':
            cimple_lexer.lex()
        else:
            sys.exit("Error. ')' was expected. line:" + str(cimple_lexer.current_token.line_number))
    else:
        sys.exit("Error. '(' was expected. line:" + str(cimple_lexer.current_token.line_number))

#calls a function name with his actual list of parameters
def call_stat(): #done
    global scope,symbol_table,total_actual_parameters , procedure_list , actual_parameter_list
    procedure_name = ID()
    line = cimple_lexer.current_token.line_number
    if cimple_lexer.current_token.token_string == '(':
        cimple_lexer.lex()
        actualparlist()
        if cimple_lexer.current_token.token_string == ')':
            exists = check_if_exists_in_symbol_table(symbol_table,procedure_name)
            if not exists:
                sys.exit("Use of undeclared procedure "+str(procedure_name)+", line "+str(line))
            procedure_name_exists_in_subprogram_list = False
            for i in range(len(procedure_list)):
                if procedure_list[i] == procedure_name:
                    procedure_name_exists_in_subprogram_list = True
            if not procedure_name_exists_in_subprogram_list:
                function_name = procedure_name
                sys.exit("procedure call "+str(function_name)+" is not allowed, line "+str(line))
            for i in range(len(symbol_table)):              #Here we check if the procedure call has too many or too few parameters so the call stat can not be executed
                for j in range(len(symbol_table[i])):
                    if len(symbol_table[i][j]) < 3:
                        continue
                    elif not isinstance(symbol_table[i][j][2], list):
                        continue
                    elif symbol_table[i][j][0] == procedure_name:        #We found the subprogram's name into the symbol table
                        if total_actual_parameters > len(symbol_table[i][j][2]):
                            sys.exit("Too many arguments for procedure call " + str(procedure_name) +", expected " + str(len(symbol_table[i][j][2])) +" , have " + str(total_actual_parameters) + " , line " + str(line))
                        elif total_actual_parameters < len(symbol_table[i][j][2]):
                            sys.exit("Too few arguments for procedure call " + str(procedure_name) + ", expected " + str(len(symbol_table[i][j][2])) + " , have " + str(total_actual_parameters) + " , line " + str(line))
                        else:
                            for k in range(len(symbol_table[i][j][2])):
                                if not actual_parameter_list[k] == symbol_table[i][j][2][k]:
                                    sys.exit("Error in procedure call "+str(procedure_name)+".Expected "+str(symbol_table[i][j][2][k])+" , got "+str(actual_parameter_list[k])+" , line "+str(line))
            genquad("call", procedure_name, "_", "_")
            total_actual_parameters = 0         #Reset count after each call stat
            actual_parameter_list.clear()       #Clear actual_parameter_list for further use
            cimple_lexer.lex()
        else:
            sys.exit("Error. ')' was expected. line:" + str(cimple_lexer.current_token.line_number))
    else:
        sys.exit("Error. '(' was expected. line:" + str(cimple_lexer.current_token.line_number))

#Assign the expression to a name,eg x:=1
def assign_stat(variable,line): #done
    global scope,symbol_table
    if cimple_lexer.current_token.token_string == ':=':
        cimple_lexer.lex()
        E_place = expression()
        genquad(":=", E_place, "_", variable)
        exists = check_if_exists_in_symbol_table(symbol_table, variable)
        if not exists:
            sys.exit("Use of undeclared variable " + str(variable) + ", line " + str(line))
    else:
        sys.exit("Error. ':=' was expected on line " + str(cimple_lexer.current_token.line_number))

#An arithmetic expressions between two terms or two factors
def expression():#done
    global startQuad
    startQuad = quad_label
    o_sign = optional_sign()
    f1_place = term()
    if o_sign == "-":
        w = newtemp()
        genquad("-", "0", f1_place, w)
        f1_place = w
    while cimple_lexer.current_token.token_type == TOKEN_TYPES["ADD_OPERATOR"]:
        sign = cimple_lexer.current_token.token_string
        cimple_lexer.lex()
        f2_place = term()
        w = newtemp()
        genquad(sign, f1_place, f2_place, w)
        f1_place = w
    return f1_place


#The first number of an expression can have an optional sign
def optional_sign(): #done
    o_sign = ""
    if cimple_lexer.current_token.token_type == TOKEN_TYPES["ADD_OPERATOR"]:
        o_sign = cimple_lexer.current_token.token_string
        cimple_lexer.lex()
    return o_sign

# term * term
def term(): #done
    f1_place = factor()
    while cimple_lexer.current_token.token_type == TOKEN_TYPES["MUL_OPERATOR"]:
        sign = cimple_lexer.current_token.token_string
        cimple_lexer.lex()
        f2_place = factor()
        w = newtemp()
        genquad(sign, f1_place, f2_place, w)
        f1_place = w
    return f1_place

#A factor can be a name or an expression or an identifier
def factor(): #done
    if cimple_lexer.current_token.token_type == TOKEN_TYPES["NUMBER"]:
        number = cimple_lexer.current_token.token_string
        cimple_lexer.lex()
        return number
    elif cimple_lexer.current_token.token_string == '(':
        cimple_lexer.lex()
        ex = expression()
        if cimple_lexer.current_token.token_string == ')':
            cimple_lexer.lex()
            return ex
        else:
            sys.exit("Error. ')' was expected in line: " + str(cimple_lexer.current_token.line_number))
    elif cimple_lexer.current_token.token_type == TOKEN_TYPES["IDENTIFIER"]:
        id_name = cimple_lexer.current_token.token_string
        line = cimple_lexer.current_token.line_number
        exists = check_if_exists_in_symbol_table(symbol_table, id_name)
        if not exists:
            sys.exit("Use of undeclared variable " + str(id_name) + ", line " + str(line))
        cimple_lexer.lex()
        w = idtail(id_name,line)
        if w:
            return w
        else:
            return id_name
    else:
        sys.exit("Error. unexpected token in line" + str(cimple_lexer.current_token.line_number))

def idtail(name,line): #done
    global total_actual_parameters,formal_parameter_list
    if cimple_lexer.current_token.token_string == '(':
        cimple_lexer.lex()
        w = actualparlist()
        for i in range(len(symbol_table)):
            for j in range(len(symbol_table[i])):
                if (len(symbol_table[i][j]) < 3):
                    continue
                elif not isinstance(symbol_table[i][j][2] , list):
                    continue
                elif symbol_table[i][j][0] == name:       #If the name from the symbol table matches with the name we want
                    if total_actual_parameters > len(symbol_table[i][j][2]):
                        sys.exit("Too many arguments to procedure call " + str(name) + ", expected " + str(len(symbol_table[i][j][2])) + " , have " + str(total_actual_parameters) + " , line " + str(line))
                    elif total_actual_parameters < len(symbol_table[i][j][2]):
                        sys.exit("Too less arguments to procedure call " + str(name) + ", expected " + str(len(symbol_table[i][j][2])) + " , have " + str(total_actual_parameters) + " , line " + str(line))
                    else:
                        for k in range(len(symbol_table[i][j][2])):
                            if not actual_parameter_list[k] == symbol_table[i][j][2][k]:
                                sys.exit("Error in function call " + str(name) + ".Expected " + str(symbol_table[i][j][2][k]) + " , got " + str(actual_parameter_list[k]) + " , line " + str(line))
        genquad("call", name, "_", "_")
        total_actual_parameters = 0
        actual_parameter_list.clear()  # Clear actual_parameter_list for further use
        if cimple_lexer.current_token.token_string == ')':
            cimple_lexer.lex()
            return w
        else:
            sys.exit("Error. ')' was expected in line: " + str(cimple_lexer.current_token.line_number))

#List with the actual parameters
def actualparlist(): #done
    if cimple_lexer.current_token.token_string == 'in' or cimple_lexer.current_token.token_string == 'inout':
        actualparitem()
        while cimple_lexer.current_token.token_string == ',':
            cimple_lexer.lex()
            actualparitem()
        w = newtemp()
        genquad("par", w,"RET","_")
        return w

#Actual parameter names used to call statements
def actualparitem(): #done
    global total_actual_parameters , actual_parameter_list
    if cimple_lexer.current_token.token_string == 'in':
        in_reference = cimple_lexer.current_token.token_string   #Store in value
        cimple_lexer.lex()
        call_by_value_paremeter = expression()
        call_by_value_paremeter_line = cimple_lexer.current_token.line_number
        exists = check_if_exists_in_symbol_table(symbol_table, call_by_value_paremeter)
        if not exists:
            sys.exit("Use of undeclared identifier "+str(call_by_value_paremeter)+" in procedure call,line "+str(call_by_value_paremeter_line))
        actual_parameter_list.append(in_reference)
        genquad("par", call_by_value_paremeter, "CV", "_")
        total_actual_parameters += 1
    elif cimple_lexer.current_token.token_string == 'inout':
        inout_reference = cimple_lexer.current_token.token_string
        cimple_lexer.lex()
        call_by_reference_paremeter = ID()
        call_by_reference_paremeter_line = cimple_lexer.current_token.line_number
        exists = check_if_exists_in_symbol_table(symbol_table,call_by_reference_paremeter)
        if not exists:
            sys.exit("Use of undeclared identifier "+str(call_by_reference_paremeter)+" in procedure call,line "+str(call_by_reference_paremeter_line))
        actual_parameter_list.append(inout_reference)
        genquad("par", call_by_reference_paremeter, "REF", "_")
        total_actual_parameters += 1
    else:
        sys.exit("Error. 'in'/'inout' was expected. line" + str(cimple_lexer.current_token.line_number))

#Checks if a name is an identifier
def ID(): #done
    if cimple_lexer.current_token.token_type == TOKEN_TYPES["IDENTIFIER"]:
        indentifier_name = cimple_lexer.current_token.token_string
        cimple_lexer.lex()
    else:
        sys.exit("Error. Identifier was expected. line:" + str(cimple_lexer.current_token.line_number))
    return indentifier_name

#Increments the global quad_label by 1
def nextquad():
    return quad_label + 1

#Creates a new quad with the elements referenced op,x,y,z
def genquad(op, x, y, z):
    global program_list
    global quad_label
    quad_label = quad_label + 1
    quad__label = str(quad_label)
    quad_list = [quad__label,op, x, y, z]
    program_list.append(quad_list)
    return program_list

#Creates a new temp variable for use in the intermediate code
def newtemp():
    global temp_counter,program_variables,offset,scope
    temp_variable = "T_" + str(temp_counter)
    temp_counter = temp_counter + 1
    program_variables.append(temp_variable)
    temp_var = (temp_variable, offset[scope])       #For e.g (T_1,offset)
    symbol_table[scope].append(temp_var)
    offset[scope] += 4
    return temp_variable

#Creates an empty list
def emptylist():
    return []  # ["_","_","_","_"]

#Creates an empty list with only element been x
def makelist(x):
    temp_list = [x]  # [x]
    return temp_list

#Merges the two lists to one without making a new one
def merge(list1, list2):
    for items in list2:
        list1.append(items)
    return list1

#Fills the last element of the list with z
def backpatch(list, z):
    # Iterate over the list and change the last element from list to z
    for index in list:
        program_list[index][4] = z
    return list

#This function is created to search if a variable exists at any scope to the symbol_table because some functions could use global information
def check_if_exists_in_symbol_table(table,name):
    exists = False
    for i in range(len(table)):
        for j in range(len(table[i])):
            if table[i][j][0] == name:
                exists = True
    return exists

#This function is created to help functions gain the information needed for the symbol_table,e.g frameLength,list_arguments and startQuad
def insert_in_symbol_table(table,name,item):
    for i in range(len(table)):
        for j in range(len(table[i])):
            if table[i][j][0] == name:
                l = list(table[i][j])
                l.append(item)
                t = tuple(l)
                table[i].append(t)
                table[i].remove(table[i][j])  # Previous information not needed.

#This method checks if variables with the same name exist in the same scope.Variables with the same name in the same scope are not allowed
def check_multiple_variable_names_exist_at_the_same_scope_in_symbol_table(table,nestingLevel,name):
    exists = False
    for i in range(len(table[nestingLevel])):
        if table[nestingLevel][i][0] == name:
            exists = True
    return exists

#Get the offset bytes and the scope for that name existed in the symbol table
def get_scope(table,name):
    scopee = 0
    if name == main_name:
        scopee = 0
        return scopee
    for i in range(len(table)):
        for j in range(len(table[i])):
            if table[i][j][0] == name:
                scopee = i
    return scopee

#Get the offset of a variable from the symbol table
def get_offset(table,name):
    offsett = 0
    for i in range(len(table)):
        for j in range(len(table[i])):
            if table[i][j][0] == name:
                offsett = table[i][j][1]
    return offsett

#Get the frame length of the program name
def get_frame_length(table,subprogram_name):
    frame_length = 0
    for i in range(len(table)):
        for j in range(len(table[i])):
            if table[i][j][0] == subprogram_name:
                frame_length = table[i][j][3]
    return frame_length

#For par list.Check how a parameter is parsed,eg "cv" or "ref"
def check_if_a_parameter_is_cv_or_ref(table,name):
    parsing_method = "local variable"
    for i in range(len(table)):
        for j in range(len(table[i])):
            if len(table[i][j]) <= 2:
                continue
            else:
                if table[i][j][0] == name:
                    parsing_method = table[i][j][2]
    return parsing_method

#This method generates an equal c code from the .ci program
def c_file_generation(file):
    global program_list
    global program_variables
    label = 0  # For labels L_1,L_2,... etc
    with open(file,'w') as file_c:
        file_c.seek(0)
        file_c.truncate()
        counter = 1
        file_c.write("#include <stdio.h>\n")
        file_c.write("#include <stdlib.h>\n")
        file_c.write("int main()\n")
        file_c.write("{\n")
        file_c.write("int ")
        list_len = len(program_variables) #Get the length of the program_variables list
        for variable in program_variables:
            if counter == list_len:
                file_c.write(str(variable)+";\n")
            else:
                file_c.write(str(variable) +",")
                counter = counter + 1
            for item in program_list:
                if item[1] == "begin_block":
                    file_c.write("L_"+str(label)+":\n")
                    label += 1
                elif item[1] == "end_block":
                    file_c.write("L_" + str(label) + ":\n")
                    label += 1
                elif item[1] == ":=":
                    file_c.write("L_" + str(label) +": " + str(item[4]) + "=" + str(item[2]) + ";\n")
                    label += 1
                elif item[1] in addOperator or item[1] in mulOperator:
                    file_c.write("L_" + str(label) +": " + str(item[4]) + "=" + str(item[2]) + str(item[1]) + str(item[3]) + ";\n")
                    label += 1
                elif item[1] in relOperator:
                    if item[1] == "<>":
                        file_c.write("L_" + str(label) + ": " + "if (" + str(item[2]) + "!=" + str(item[3]) + ")" + " goto " + "L_" + str(item[4]) + ";\n")
                        label += 1
                    elif item[1] == "=":
                        file_c.write("L_" + str(label) + ": " + "if (" + str(item[2]) + "==" + str(item[3]) + ")" + " goto " + "L_" + str(item[4]) + ";\n")
                        label += 1
                    else:
                        file_c.write("L_" + str(label) +": " +"if (" + str(item[2]) + str(item[1]) + str(item[3]) + ")" + " goto " + "L_" + str(item[4]) + ";\n")
                        label += 1
                elif item[1] == "jump":
                    file_c.write("L_" + str(label) +": " +"goto L_" + str(item[4]) + ";\n")
                    label += 1
                elif item[1] == "inp":
                    file_c.write("L_" + str(label) +": " +"scanf(\"%d\",&" + str(item[2]) + ");\n")
                    label += 1
                elif item[1] == "out":
                    file_c.write("L_" + str(label) + ": " + "printf(\"%d\""","+str(item[2])+");\n")
                    label += 1
        file_c.write("return 0;\n")
        file_c.write("}\n")

def asm_file_generation(file):
    global program_list
    framelengthOfMainProgram = 0
    name = ""
    L_index = ""
    name_and_label_number_list_tuple = []      #Store the name and the number of the L_number that specific name is
    label = 1   #count labels
    flag = 0 #The first parameter of a function/procedure changes the flag to 1 and does addi,$fp,$sp,framelength
    count_parameters = 0
    scope_of_function_or_procedure , scope_of_v = 0,0
    with open(file,"w") as file_asm:
        file_asm.write("Lbegin:j Lmain\n")
        for variable in program_list:
            if variable[1] == "begin_block":                        #begin_block
                name = variable[2]                           #Store the function/procedure name.It will help in the loadvr method.
                if name == main_name:                        #Main block
                    file_asm.write("Lmain:\n")
                    framelengthOfMainProgram = get_frame_length(symbol_table, variable[2])
                    file_asm.write("L" + str(variable[0]) +": addi $sp,$sp," + str(offset[0]) + "\n"
                                                            "\tmove $s0,$sp\n")
                    label += 1
                else:                                               #Function / Procedure blocks
                    L_index = variable[0]                           #Store the number of the function/procedure label so that in a call we can jump back to that specific label
                    name_and_label_number = (name,L_index)
                    name_and_label_number_list_tuple.append(name_and_label_number)
                    file_asm.write("L"+str(variable[0])+": sw $ra,0($sp)\n")
                    label += 1
            elif variable[1] == "halt":
                file_asm.write("L" + str(variable[0])+":\n")
            elif variable[1] == "end_block":                         #end_block
                if variable[2] == main_name:
                    file_asm.write("L" + str(variable[0])+  ":li $v0,10\n"
                                                            "\tsyscall\n")
                    label += 1
                else:
                    name = variable[2]
                    file_asm.write("L" + str(variable[0])+": lw $ra,($sp)\n"
                                                            "\tjr $ra\n")
                    label += 1
            elif variable[1] == "jump":                             #"jump"
                file_asm.write("L"+str(variable[0])+": j L"+str(variable[4])+"\n")
            elif variable[1] == "out":                              #"out"
                t1 = loadvr(variable[2], "$t1", name)
                offsetvar = get_offset(symbol_table, variable[2])
                file_asm.write("L" + str(variable[0]) +": li $v0,1\n"
                                "\tlw $a0,-"+str(offsetvar)+"($sp)\n"
                                "\tsyscall\n")
                label += 1
            elif variable[1] == "inp":                               #"inp"
                z = storerv("$v0", variable[2] , name)
                file_asm.write("L"+str(variable[0])+":li $v0,5\n"
                                "\tsyscall\n"
                                "\t"+z+"\n")
                label += 1
            elif variable[1] in addOperator:                        # add/sub/ t1,t2,z
                file_asm.write("L"+str(variable[0])+":")
                t1 = loadvr(variable[2],"$t1" , name)
                t2 = loadvr(variable[3],"$t2" , name)
                file_asm.write( t1+"\n"
                                "\t"+t2+"\n")
                if variable[1] == "+":
                    file_asm.write("\tadd $t1,$t1,$t2\n")
                else:
                    file_asm.write("\tsub $t1,$t1,$t2\n")
                z = storerv("$t1",variable[4] , name)
                file_asm.write("\t" + z + "\n")
                label += 1
            elif variable[1] in mulOperator:                        # mul/div/ t1,t2,z
                file_asm.write("L" + str(variable[0])+":")
                t1 = loadvr(variable[2], "$t1" , name)
                t2 = loadvr(variable[3], "$t2" , name)
                file_asm.write( t1 + "\n"
                        "\t" + t2 + "\n")
                if variable[1] == "*":
                    file_asm.write("\tmul $t1,$t1,$t2\n")
                else:
                    file_asm.write("\tdiv $t1,$t1,$t2\n")
                z = storerv("$t1",variable[4] , name)
                file_asm.write("\t" + z + "\n")
                label += 1
            elif variable[1] == ":=":                                   #:=
                t1 = loadvr(variable[2], "$t1" , name)
                z = storerv("$t1", variable[4] , name)
                file_asm.write("L" + str(variable[0])+":"+ t1 +"\n"
                                "\t" + z + "\n")
                label += 1
            elif variable[1] in relOperator:
                file_asm.write("L" + str(variable[0])+":")              #<,>,>=,<=,<>
                t1 = loadvr(variable[2],"$t1" , name)
                t2 = loadvr(variable[3],"$t2" , name)
                file_asm.write(" "+t1 + "\n"
                            "\t" + t2 + "\n")
                if variable[1] == ">":
                    file_asm.write("\tbgt $t1,$t2,L" + str(variable[4])+"\n")
                elif variable[1] == "<":
                    file_asm.write("\tblt $t1,$t2,L" + str(variable[4])+"\n")
                elif variable[1] == ">=":
                    file_asm.write("\tbge $t1,$t2,L" + str(variable[4])+"\n")
                elif variable[1] == "<=":
                    file_asm.write("\tble $t1,$t2,L" + str(variable[4])+"\n")
                elif variable[1] == "<>":
                    file_asm.write("\tbne $t1,$t2,L" + str(variable[4])+"\n")
            elif variable[1] == "retv":                             # retv
                file_asm.write("L"+str(variable[0])+":")
                t1 = loadvr(variable[2], "$t1" , name)
                file_asm.write( "\t"+t1+"\n"
                               "\tlw $t0,-8($sp)\n"
                               "\tsw $t1,($t0)\n")
                label += 1
            elif variable[1] == "call":                             #call
                count_parameters = 0
                file_asm.write("L" + str(variable[0])+":sw $sp,-4($fp)\n")
                frame = get_frame_length(symbol_table,variable[2])
                framelength = frame - 4
                file_asm.write("\taddi $sp,$sp,"+str(framelength)+"\n")
                for label in range(len(name_and_label_number_list_tuple)):
                    if variable[2] == name_and_label_number_list_tuple[label][0]:
                        file_asm.write("\tjal L" + str(L_index) + "\n")
                file_asm.write("\taddi $sp,$sp,-" + str(framelength) + "\n")
                label += 1
            elif variable[3] == "CV":                               #CV parameter
                count_parameters += 1
                if flag == 0:
                    flag = 1
                    frame = get_frame_length(symbol_table, name)
                    framelength = frame - 4  # Actual length of procedure / function frame
                    file_asm.write("L" + str(variable[0]) + ":addi $fp,$sp," + str(framelength) + "\n\t")
                else:
                    file_asm.write("L" + str(variable[0]))
                t0 = loadvr(variable[2], "$t0", name)              #Load the parameter into a register
                file_asm.write("\t"+t0+"\n"
                            "\tsw $t0,-"+str(12+4*count_parameters)+"($fp)\n")
                label += 1

            elif variable[3] == "REF":                             #REF parameter
                count_parameters += 1
                if flag == 0:
                    flag = 1
                    frame = get_frame_length(symbol_table, name)
                    framelength = frame - 4  # Actual length of procedure / function frame
                    file_asm.write("L" + str(variable[0]) + ":addi $fp,$sp," + str(framelength) + "\n\t")
                else:
                    file_asm.write("L" + str(variable[0]) +":")

                scope_of_v = get_scope(symbol_table,variable[2])
                scope_of_function_or_procedure = get_scope(symbol_table,name) + 1
                par_mode = check_if_a_parameter_is_cv_or_ref(symbol_table, variable[2])
                par_offset = get_offset(symbol_table, variable[2])
                if scope_of_v == scope_of_function_or_procedure:                  #If v exists in the same scope
                    if par_mode == "local variable" or par_mode == 'in':
                        file_asm.write("addi $t0,$sp,-" + str(par_offset) + "\n"+
                                      "\tsw $t0,-" + str(12+4*count_parameters) + "($fp)\n")
                    elif par_mode == 'inout':
                        file_asm.write("lw $t0,-" + str(par_offset) + "\n" +
                                     "\tsw $t0,-" + str(12+4*count_parameters) + "($fp)\n")
                else:
                    if par_mode == "local variable" or par_mode == 'in':
                        s = gnlvcode(variable[2] , name)
                        file_asm.write(s+"\tsw $t0,-" + str(12+4*count_parameters) + "($fp)\n")
                    elif par_mode == 'inout':
                        s = gnlvcode(variable[2] , name)
                        file_asm.write("lw $t0,($t0)\n" +
                                     "\tsw $t0,-" + str(12+4*count_parameters) + "($fp)\n")
                label += 1

            elif variable[3] == "RET":                              #Temp var RET
                temp_var_offset = get_offset(symbol_table,variable[2])
                file_asm.write("L"+str(variable[0])+":addi $t0,$sp,-"+str(temp_var_offset)+"\n"
                                                    "\tsw $t0,-8($fp)\n")

def gnlvcode(v, def_name):
    scope_of_v = get_scope(symbol_table, v)
    scope_of_def = get_scope(symbol_table, def_name) + 1
    offset_of_v = get_offset(symbol_table, v)

    lins = "lw $t0, -4($sp)\n"

    for i in range(scope_of_def - scope_of_v):
            lins += "\taddi $t0,$t0," + "-" + str(offset_of_v) + "\n"

    lins += "\tlw $t0, -4($t0)\n"
    return lins

def loadvr(v, r, function_name):
    if v.isdigit():
        return "li " + str(r) + "," + v  # li $tr,v
    scope_of_v = get_scope(symbol_table, v)  # Know the scope of the variable in the symbol table
    scope_of_def = get_scope(symbol_table,
                             function_name) + 1  # Know the scope of the funcion / procedure in the symbol table
    offset_of_v = get_offset(symbol_table, v)  # Get the offset of the variable from the symbol table
    parsing_method_of_v = check_if_a_parameter_is_cv_or_ref(symbol_table,
                                                            v)  # If v is a parameter,store the its parsing method
    if scope_of_v == 0:  # If v is global
        return "lw " + str(r) + ",-" + str(offset_of_v) + "($s0)"
    else:
        if scope_of_v == scope_of_def:  # If v exists in the same scope
            if parsing_method_of_v == "cv":
                return "lw " + str(r) + ",-" + str(offset_of_v) + "($sp)"
            elif parsing_method_of_v == "ref":
                return "lw $t0,-" + str(offset_of_v) + "($sp)\n"\
                "\t" + "lw " + str(r) + ",($t0)"
            else:
                return "lw " + str(r) + ",-" + str(offset_of_v) + "($sp)"
        else:  # If v does not exist in the current scope
            if parsing_method_of_v == "cv":
                s = gnlvcode(v, function_name)
                s += "lw " + str(r) + ", ($t0)"
                return s
            elif parsing_method_of_v == "ref":
                s = gnlvcode(v, function_name)
                s += "lw $t0,($t0)\n"\
                     "\t" + "lw " + str(r) + ",($t0)"
                return s
            else:
                s = gnlvcode(v, function_name)
                s += "lw " + str(r) + ", ($t0)"
                return s

def storerv(r,v,function_name):
    scope_of_v = get_scope(symbol_table, v)  # Know the scope of the variable in the symbol table
    scope_of_def = get_scope(symbol_table,function_name) + 1  # Know the scope of the funcion / procedure in the symbol table
    offset_of_v = get_offset(symbol_table, v)  # Get the offset of the variable from the symbol table
    parsing_method_of_v = check_if_a_parameter_is_cv_or_ref(symbol_table,
                                                            v)  # If v is a parameter,store the its parsing method
    if scope_of_v == 0:  # If v is global
        return "sw "+ str(r) + ",-" + str(offset_of_v) + "($s0)"
    else:
        if scope_of_v == scope_of_def:  # If v exists in the same scope
            if parsing_method_of_v == "cv":
                return "sw " + str(r) + ",-" + str(offset_of_v) + "($sp)"
            elif parsing_method_of_v == "ref":
                return "lw $t0,-" + str(offset_of_v) + "($sp)\n""\t" + "sw " + str(r) + ",($t0)"
            else:
                return "lw " + str(r) + ",-" + str(offset_of_v) + "($sp)"
        else:  # If v does not exist in the current scope
            if parsing_method_of_v == "cv":
                s = gnlvcode(v, function_name)
                s += "sw " + str(r) + ",-" + str(offset_of_v) + "($t0)"
                return s
            elif parsing_method_of_v == "ref":
                s = gnlvcode(v, function_name)
                s += "lw $t0,($t0)\n" + \
              "\t" + "sw " + str(r) + ",($t0)"
                return s
            else:
                s = gnlvcode(v, function_name)
                s += "lw " + str(r) + ",-" + str(offset_of_v) + "($sp)"
                return s

def print_symbol_table(table,file):
    with open(file, "w") as file_s:
        for i in range(len(table)):
            file_s.write("scope = "+str(i)+" , symbol_table = "+str(table[i])+"\n")
        file_s.write("symbol_table = "+str(symbol_table))

def parse_arguments():
    parser = argparse.ArgumentParser(description='Compile Cimple programs into intermediate, C, or assembly code.')
    parser.add_argument('source', help='The path to the Cimple source file')
    parser.add_argument('-o', '--output', default='output', help='The path to the output file (without extension)')
    parser.add_argument('--intermediate', action='store_true', help='Generate intermediate code (.int file)')
    parser.add_argument('--c', action='store_true', help='Generate C code (.c file)')
    parser.add_argument('--asm', action='store_true', help='Generate assembly code (.asm file)')
    parser.add_argument('--symbol-table', action='store_true', help='Generate symbol table (.symbol_table file)')
    
    args = parser.parse_args()
    return args

def main():
    global cimple_lexer
    args = parse_arguments()
    
    f = open(args.source, "r")
    testinput = f.read()
    
    cimple_lexer = Lexer(testinput)
    program()  # Assuming this populates global variables like program_list

    if args.intermediate:
        int_filename = f"{args.output}.int"
        with open(int_filename, "w") as int_file:
            for element in program_list:
                int_file.write(f"{element[0]} {element[1]} {element[2]} {element[3]} {element[4]}\n")
    
    if args.c:
        c_file_generation_flag = any(element[1] == 'call' for element in program_list)
        if not c_file_generation_flag:
            c_filename = f"{args.output}.c"
            c_file_generation(c_filename)
    
    if args.asm:
        asm_filename = f"{args.output}.asm"
        asm_file_generation(asm_filename)
    
    if args.symbol_table:
        symbol_table_file = f"{args.output}.symbol_table"
        print_symbol_table(symbol_table, symbol_table_file)

if __name__ == "__main__":
    main()

