from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter

"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream, output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.tokenizer = JackTokenizer(input_stream)
        self.symbol_table = SymbolTable()
        self.vm_writer = VMWriter(output_stream)
        self.output_stream = output_stream
        self.current_token = ""
        self.class_name = ""

    def compile_class(self) -> None:
        """Compiles a complete class."""
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()
            self.current_token = self.tokenizer.current_token
            if self.current_token == "class":
                self.tokenizer.advance()
                self.current_token = self.tokenizer.current_token
                self.class_name = self.current_token
                if self.tokenizer.token_type() == 'IDENTIFIER':
                    class_name = self.current_token
                    self.tokenizer.advance()
                    self.current_token = self.tokenizer.current_token
                    if self.current_token == "{":
                        self.tokenizer.advance()
                        while self.tokenizer.keyword() == "static" or self.tokenizer.keyword() == "field":
                            self.compile_class_var_dec()
                        while self.tokenizer.keyword() == "constructor" or self.tokenizer.keyword() == "function" or self.tokenizer.keyword() == "method":
                            self.compile_subroutine(class_name)
                        self.current_token = self.tokenizer.current_token
                        if self.current_token == "}":
                            return

    def compile_class_var_dec(self) -> None:  # Naomi
        """Compiles a static declaration or a field declaration."""
        kind = self.tokenizer.current_token()
        self.tokenizer.advance()
        type = self.tokenizer.current_token()
        self.tokenizer.advance()
        name = self.tokenizer.current_token()
        self.symbol_table.define(name, type, kind)
        self.tokenizer.advance()
        while self.tokenizer.current_token() == ",":  # if there are more variables
            self.tokenizer.advance()
            name = self.tokenizer.current_token()
            self.symbol_table.define(name, type, kind)
            self.tokenizer.advance()
            # blah blah

    def compile_subroutine(self, class_name: str) -> None:
        """Compiles a complete method, function, or constructor."""
        subroutine_type = self.tokenizer.keyword()
        self.tokenizer.advance()
        if self.tokenizer.token_type() == 'KEYWORD':
            self.tokenizer.advance()
        elif self.tokenizer.token_type() == 'IDENTIFIER':
            self.tokenizer.advance()
        subroutine_name = self.tokenizer.identifier()
        self.tokenizer.advance()
        self.tokenizer.advance()
        self.compile_parameter_list()
        self.tokenizer.advance()
        self.tokenizer.advance()
        while self.tokenizer.keyword() == "var":
            self.compile_var_dec()
        self.vm_writer.write_function(f"{class_name}.{subroutine_name}", self.symbol_table.var_count("var"))
        if subroutine_type == "constructor":
            self.vm_writer.write_push("constant", self.symbol_table.var_count("field"))
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("pointer", 0)
        elif subroutine_type == "method":
            self.vm_writer.write_push("argument", 0)
            self.vm_writer.write_pop("pointer", 0)
        self.compile_statements()
        self.tokenizer.advance()

    def compile_parameter_list(self) -> None:  # Naomi
        """Compiles a (possibly empty) parameter list."""
        while self.tokenizer.current_token() != ")":
            type = self.tokenizer.current_token()
            self.tokenizer.advance()
            name = self.tokenizer.current_token()
            self.symbol_table.define(name, type, "ARG")
            self.tokenizer.advance()
            if self.tokenizer.current_token() == ",":
                self.tokenizer.advance()

    def compile_var_dec(self) -> None:  # Naomi
        """Compiles a var declaration."""
        type = self.tokenizer.current_token()
        self.tokenizer.advance()
        name = self.tokenizer.current_token()
        self.symbol_table.define(name, type, "VAR")
        self.tokenizer.advance()
        while self.tokenizer.current_token() == ",":  # if there are more variables
            self.tokenizer.advance()
            name = self.tokenizer.current_token()
            self.symbol_table.define(name, type, "VAR")
            self.tokenizer.advance()
        if self.tokenizer.current_token() == ";":
            self.tokenizer.advance()

    def compile_statements(self) -> None:
        """Compiles a sequence of statements."""
        while self.tokenizer.token_type() == 'KEYWORD':
            if self.tokenizer.keyword() == "let":
                self.compile_let()
            elif self.tokenizer.keyword() == "if":
                self.compile_if()
            elif self.tokenizer.keyword() == "while":
                self.compile_while()
            elif self.tokenizer.keyword() == "do":
                self.compile_do()
            elif self.tokenizer.keyword() == "return":
                self.compile_return()

    def compile_do(self) -> None:  # Naomi
        """Compiles a do statement."""
        self.tokenizer.advance()
        self.compile_expression()
        self.vm_writer.write_pop("temp", 0)
        self.tokenizer.advance()

    def compile_let(self) -> None:  # Naomi
        """Compiles a let statement."""
        self.output_stream.write("<letStatement>\n")
        self.output_stream.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")
        self.tokenizer.advance()
        self.output_stream.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
        self.tokenizer.advance()
        if self.tokenizer.symbol() == "[":
            self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
            self.tokenizer.advance()
            self.compile_expression()
            self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
            self.tokenizer.advance()
        self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")  # =
        self.tokenizer.advance()
        self.compile_expression()
        self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
        self.output_stream.write("</letStatement>\n")
        self.tokenizer.advance()

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.output_stream.write("<whileStatement>\n")
        self.output_stream.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")
        self.tokenizer.advance()
        self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
        self.tokenizer.advance()
        self.compile_expression()
        self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
        self.tokenizer.advance()
        self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
        self.tokenizer.advance()
        self.compile_statements()
        self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
        self.output_stream.write("</whileStatement>\n")
        self.tokenizer.advance()

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.tokenizer.advance()
        if self.tokenizer.current_token != ";":
            self.compile_expression()
        else:
            self.vm_writer.write_push("constant", 0)
        self.vm_writer.write_return()
        self.tokenizer.advance()

    def compile_if(self) -> None:
        """Compiles an if statement, possibly with a trailing else clause."""
        self.output_stream.write("<ifStatement>\n")
        self.output_stream.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")
        self.tokenizer.advance()
        self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
        self.tokenizer.advance()
        self.compile_expression()
        self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
        self.tokenizer.advance()
        self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
        self.tokenizer.advance()
        self.compile_statements()
        self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
        self.tokenizer.advance()
        if self.tokenizer.token_type() == 'KEYWORD' and self.tokenizer.keyword() == "else":
            self.output_stream.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")
            self.tokenizer.advance()
            self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
            self.tokenizer.advance()
            self.compile_statements()
            self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
            self.tokenizer.advance()
        self.output_stream.write("</ifStatement>\n")

    def compile_term(self) -> None:
        """Compiles a term and generates the corresponding VM code."""
        token_type = self.tokenizer.token_type()
        token_value = self.tokenizer.current_token
        if token_type == 'INT_CONST':
            self.vm_writer.write_push('constant', self.tokenizer.int_val())
            self.tokenizer.advance()
        elif token_type == 'STRING_CONST':
            string_value = self.tokenizer.string_val()
            self.vm_writer.write_push('constant', len(string_value))
            self.vm_writer.write_call('String.new', 1)
            for char in string_value:
                self.vm_writer.write_push('constant', ord(char))
                self.vm_writer.write_call('String.appendChar', 2)
            self.tokenizer.advance()
        elif token_type == 'KEYWORD':
            if token_value == 'true':
                self.vm_writer.write_push('constant', 0)
                self.vm_writer.write_arithmetic('not')
            elif token_value in ['false', 'null']:
                self.vm_writer.write_push('constant', 0)
            elif token_value == 'this':
                self.vm_writer.write_push('pointer', 0)
            self.tokenizer.advance()
        elif token_type == 'IDENTIFIER':
            self.tokenizer.advance()
            if self.tokenizer.symbol() == '[':
                self.tokenizer.advance()
                self.compile_expression()
                self.vm_writer.write_push('that', 0)
                self.vm_writer.write_arithmetic('add')
                self.vm_writer.write_pop('pointer', 1)
                self.vm_writer.write_push(self.symbol_table.kind_of(token_value),
                                          self.symbol_table.index_of(token_value))
                self.tokenizer.advance()

            elif self.tokenizer.symbol() in ['(', '.']:
                self.compile_subroutine_call(token_value)
            else:
                self.vm_writer.write_push(self.symbol_table.kind_of(token_value),
                                          self.symbol_table.index_of(token_value))
                self.tokenizer.advance()
        elif self.tokenizer.token_type() == "SYMBOL" :
            if self.tokenizer.symbol() == "(":
                self.tokenizer.advance()
                self.compile_expression()
                self.tokenizer.advance() # )
            elif self.tokenizer.symbol() in ["~", "-", "^", "#"]:
                self.tokenizer.advance()
                self.compile_term()
                if token_value == "-":
                    self.vm_writer.write_arithmetic("neg")
                elif token_value == "~":
                    self.vm_writer.write_arithmetic("not")
                elif token_value == "^":
                    self.vm_writer.write_arithmetic("shiftleft")
                elif token_value == "#":
                    self.vm_writer.write_arithmetic("shiftright")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.compile_term()
        while self.tokenizer.current_token in ["+", "-", "*", "/", "|", "=", "<", ">", "&"]:
            self.tokenizer.advance()
            self.compile_term()
            self.vm_writer.write_arithmetic(self.tokenizer.current_token)

    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        count = 0
        if self.tokenizer.token_type() != 'SYMBOL' or self.tokenizer.symbol() != ")":  # not empty expression list
            self.compile_expression()
            count += 1
            while self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == ",":
                self.tokenizer.advance()
                self.compile_expression()
                count += 1
        return count

    def compile_type_and_var_name(self) -> None:
        """Compiles type and variable name."""
        if self.tokenizer.token_type() == 'KEYWORD':
            self.output_stream.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")
        elif self.tokenizer.token_type() == 'IDENTIFIER':
            self.output_stream.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
        self.tokenizer.advance()
        self.output_stream.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
        self.tokenizer.advance()
        while self.tokenizer.symbol() == ",":
            self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
            self.tokenizer.advance()
            self.output_stream.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
            self.tokenizer.advance()
        self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
        self.tokenizer.advance()

    def compile_subroutine_call(self, subroutine_name):
        """Compiles a subroutine call and generates the corresponding VM code."""
        added_args = 0
        if self.tokenizer.symbol() == '.':
            self.tokenizer.advance()
            class_or_var_name = subroutine_name
            subroutine_name = self.tokenizer.identifier()
            self.tokenizer.advance()
            if self.symbol_table.kind_of(class_or_var_name):  # class_or_var_name is a variable
                self.vm_writer.write_push(self.symbol_table.kind_of(class_or_var_name),
                                          self.symbol_table.index_of(class_or_var_name))
                added_args = 1
                subroutine_name = f"{self.symbol_table.type_of(class_or_var_name)}.{subroutine_name}"
            else:  # class_or_var_name is a class
                subroutine_name = f"{class_or_var_name}.{subroutine_name}"
        else:
            self.vm_writer.write_push('pointer', 0)  # push this
            added_args = 1  # this is the first argument
            subroutine_name = f"{self.class_name}.{subroutine_name}"

        self.tokenizer.advance()  # (
        n_args = self.compile_expression_list() + added_args
        self.tokenizer.advance()  # )
        self.vm_writer.write_call(subroutine_name, n_args)
