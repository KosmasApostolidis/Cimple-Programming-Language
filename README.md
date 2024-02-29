# Cimple-Programming-Language
This repository is created for the Compilers Course (**ΜΥΥ802**) at the **Department of Computer Science and Engineering at the University of Ioannina (UOI)**

## Overview
Cimple is a small, educational programming language designed to introduce programming concepts with simplicity. Inspired by C, it focuses on fundamental programming structures and capabilities, tailored for educational purposes.

## Features
- **Syntax and Structure**: Resembles **C**, offering a familiar ground with simpler constructs.
- **Educational Focus**: Ideal for teaching basic programming concepts such as loops (while, forcase, incase), conditional statements (if-else), and functions.
- **Unique Elements**: Introduces original constructs like forcase and incase for educational exploration.
- **Functionality**: Supports functions, procedures, parameter passing by reference and value, and recursive calls.
- **Limitations**: Excludes complex data types and structures like real numbers, strings, and arrays for simplicity.

## Getting Started
- Cimple files use the **.ci** extension.

# Types and Variable Declarations in Cimple
Cimple supports a single data type: integer numbers. Variables are declared using the **declare** command followed by the identifiers' names, separated by commas. Since all variables in Cimple are integers, no type specification is required. Declarations end with a Greek question mark. Multiple **declare** statements can be used consecutively for declaring different variables.

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

# Conditional `if`

