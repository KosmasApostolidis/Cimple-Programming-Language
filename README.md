# Cimple-Programming-Language
This repository is created for the Compilers Course (ΜΥΥ802) at the **Department of Computer Science and Engineering at the University of Ioannina (UOI)**

## Overview
Cimple is a small, educational programming language designed to introduce programming concepts with simplicity. Inspired by C, it focuses on fundamental programming structures and capabilities, tailored for educational purposes.

## Features
- **Syntax and Structure**: Resembles **C**, offering a familiar ground with simpler constructs.
- **Educational Focus**: Ideal for teaching basic programming concepts such as loops (`while`, `forcase`, `incase`), conditional statements (`if-else`), and functions.
- **Unique Elements**: Introduces original constructs like `forcase` and `incase` for educational exploration.
- **Functionality**: Supports functions, procedures, parameter passing by reference and value, and recursive calls.
- **Limitations**: Excludes complex data types and structures like real numbers, strings, and arrays for simplicity.

## Getting Started
- Cimple files use the **.ci** extension.

# Types and Variable Declarations in Cimple
Cimple supports a single data type: integer numbers. Variables are declared using the `declare` command followed by the identifiers' names, separated by commas. Since all variables in Cimple are integers, no type specification is required. Declarations end with a Greek question mark. Multiple `declare` statements can be used consecutively for declaring different variables.

# Operators and Expressions in Cimple
Cimple defines a hierarchy of operators from highest to lowest precedence as follows:

- **Multiplicative Operators**: `*`, `/`
- **Additive Operators**: `+`, `-`
- **Relational Operators**: `=`, `<`, `>`, `<>`, `<=`, `>=`
- **Logical Operators**: `not`
- **Logical AND**: `and`
- **Logical OR**: `or`

## Cimple Program Structure

Every Cimple program starts with the keyword **program**, followed by an identifier (name) for the program itself. After this introduction, a Cimple program is divided into three main blocks:
- **Declarations**: This block contains the variable declarations.
- **Subprograms**: Functions and procedures that can be nested within each other.
- **Statements**: The main program commands.

The structure of a Cimple program is outlined below, noting the period at the end of the program:
```
program <identifier> 
<declarations> 
<subprograms> 
<statements> 
```

# Assignment
- Syntax: `ID := expression`
- Used for assigning the value of a variable, constant, or expression to a variable.

# Conditional if
Syntax:
```
if (condition)
    statements1
[else
    statements2]
```
Executes `statements1` if `condition` is `true`; otherwise, `statements2` is executed if specified.

# Loop while
Syntax:

```
while (condition)
    statements
```
Repeats `statements` as long as `condition` is `true`.

# Selection switchcase
Syntax:
```
switchcase
    (case (condition) statements1)
    *
    default statements2
```
Executes `statements1` for the first true `condition`; if no conditions are true, `default` `statements2` are executed.

# Repetition forcase
Syntax:

```
forcase
    (case (condition) statements1)
    *
    default statements2
```
Similar to `switchcase`, but returns to the start of `forcase` after executing `statements1`.

# Repetition incase
Syntax:
```
incase
    (case (condition) statements1)
    *
```
Checks each `condition` in sequence, executing corresponding `statements1` for each true condition.

# Function Return Value
Syntax `return (expression)
Returns the result of evaluating `expression` within a function.

# Output Data
- Syntax: `print (expression)
- Displays the result of `expression` evaluation.

# Input Data
- Syntax: `input (ID)`
- Requests a value from the user to be stored in the variable `ID`.

# Procedure Calls in Cimple
- Syntax for calling a procedure: `call functionName(actualParameters)`
- Used to invoke a procedure within the program.

# Functions and Procedures in Cimple
- Cimple supports both functions and procedures with similar structures but distinct purposes.
- **Functions** are defined for operations that return a value:

```
function ID (formalPars)
{
    declarations
    subprograms
    statements
}
```
- Functions can be called within arithmetic expressions, e.g., `D = a + f(in x)`, where `f` is the function and `x` is the parameter passed by value.

# **Procedures**
- Defined for operations that do not return a value:

```
procedure ID (formalPars)
{
    declarations
    subprograms
    statements
}
```
- Procedures are called using the `call` keyword, e.g., `call f(inout x)`, where `f` is the procedure and `x` is the parameter passed by reference.
- `formalPars` represents the list of formal parameters. Both functions and procedures can be nested within each other, and scope rules follow those of PASCAL.

# Parameter Passing in Cimple
Cimple supports two modes of parameter passing:

- **By Value**: Specified with the keyword `in`. Changes made to the parameter within the function do not affect the variable in the calling program.
- **By Reference**: Specified with the keyword `inout`. Any changes made to the parameter are reflected in the calling program.
Parameters are prefixed with `in` or `inout` in function calls, indicating whether they are passed by value or by reference, respectively.

# Variable Scope and Functionality in Cimple
- **Global Variables**: Declared in the main program and accessible everywhere within the program.
- **Local Variables**: Declared within a function or procedure and accessible only within that specific context.
- **Scope Overriding**: Cimple follows the common scoping rule where local variables and parameters overshadow those declared at a higher nesting level, which in turn overshadow global variables.
- **Function and Procedure Calls**: Functions and procedures can recursively call themselves and any function or procedure declared at the same nesting level that precedes them in the code.

# Cimple Grammar Specification

```php
// "program" is the starting symbol
program : program ID block .

// A block with declarations, subprograms, and statements
block : declarations subprograms statements

// Declaration of variables, zero or more "declare" allowed
declarations : ( declare varlist ; )*

// A list of variables following the declaration keyword
varlist : ID ( , ID )*

// Zero or more subprograms allowed
subprograms : ( subprogram )*

// A subprogram is a function or a procedure,
// followed by parameters and block
subprogram : function ID ( formalparlist ) block
            | procedure ID ( formalparlist ) block

// List of formal parameters
formalparlist : formalparitem ( , formalparitem )*

// A formal parameter ("in": by value, "inout" by reference)
formalparitem : in ID
              | inout ID

// One or more statements
statements : statement ;
           | { statement ( ; statement )* }

// One statement
statement : assignStat
          | ifStat
          | whileStat
          | switchcaseStat
          | forcaseStat
          | incaseStat
          | callStat
          | returnStat
          | inputStat
          | printStat

// Assignment statement
assignStat : ID := expression

// If statement
ifStat : if ( condition ) statements elsepart
elsepart : else statements
         | ε

// While statement
whileStat : while ( condition ) statements

// Switch statement
switchcaseStat: switchcase ( case ( condition ) statements )*
               default statements

// Forcase statement
forcaseStat : forcase ( case ( condition ) statements )*
             default statements

// Incase statement
incaseStat : incase ( case ( condition ) statements )*

// Return statement
returnStat : return( expression )

// Call statement
callStat : call ID( actualparlist )

// Print statement
printStat : print( expression )

// Input statement
inputStat : input( ID )

// List of actual parameters
actualparlist : actualparitem ( , actualparitem )*

// An actual parameter ("in": by value, "inout" by reference)
actualparitem : in expression
              | inout ID

// Boolean expression
condition : boolterm ( or boolterm )*

// Term in boolean expression
boolterm : boolfactor ( and boolfactor )*

// Factor in boolean expression
boolfactor : not [ condition ]
           | [ condition ]
           | expression REL_OP expression

// Arithmetic expression
expression : optionalSign term ( ADD_OP term )*

// Term in arithmetic expression
term : factor ( MUL_OP factor )*

// Factor in arithmetic expression
factor : INTEGER
       | ( expression )
       | ID idtail

// Follows a function of procedure (parentheses and parameters)
idtail : ( actualparlist )
       | ε

// Symbols "+" and "-" (are optional)
optionalSign : ADD_OP
             | ε

// Lexer rules: relational, arithmetic operations, integers, and ids
REL_OP : = | <= | >= | > | < | <>
ADD_OP : + | -
MUL_OP : * | /
INTEGER : [0-9]+
ID : [a-zA-Z][a-zA-Z0-9]*
```
