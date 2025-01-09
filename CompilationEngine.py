from JackTokenizer import JackTokenizer

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
        self.output_stream = output_stream
        self.current_token = ""
        # self.indent = 0

    def compile_class(self) -> None:
        """Compiles a complete class."""
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()
            self.current_token = self.tokenizer.current_token
            if self.current_token == "class":
                self.output_stream.write("<class>\n")
                self.output_stream.write("<keyword> class </keyword>\n")
                self.tokenizer.advance()
                self.current_token = self.tokenizer.current_token
                if self.tokenizer.token_type() == 'IDENTIFIER':
                    self.output_stream.write(f"<identifier> {self.current_token} </identifier>\n")
                    self.tokenizer.advance()
                    self.current_token = self.tokenizer.current_token
                    if self.current_token == "{":
                        self.output_stream.write("<symbol> { </symbol>\n")
                        self.tokenizer.advance()
                        while self.tokenizer.keyword() == "static" or self.tokenizer.keyword() == "field":
                            self.compile_class_var_dec()
                        while self.tokenizer.keyword() == "constructor" or self.tokenizer.keyword() == "function" or self.tokenizer.keyword() == "method":
                            self.compile_subroutine()
                        self.current_token = self.tokenizer.current_token
                        if self.current_token == "}":
                            self.output_stream.write("<symbol> } </symbol>\n")
                            self.output_stream.write("</class>\n")
                            return

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        self.output_stream.write("<classVarDec>\n")
        self.output_stream.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")
        self.tokenizer.advance()
        self.compile_type_and_var_name()
        self.output_stream.write("</classVarDec>\n")

    def compile_subroutine(self) -> None:
        """Compiles a complete method, function, or constructor."""
        self.output_stream.write("<subroutineDec>\n")
        self.output_stream.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")
        self.tokenizer.advance()
        if self.tokenizer.token_type() == 'KEYWORD':
            self.output_stream.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")
        elif self.tokenizer.token_type() == 'IDENTIFIER':
            self.output_stream.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
        self.tokenizer.advance()
        self.output_stream.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
        self.tokenizer.advance()
        self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
        self.tokenizer.advance()
        self.compile_parameter_list()
        self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
        self.tokenizer.advance()
        self.output_stream.write("<subroutineBody>\n")
        self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
        self.tokenizer.advance()
        while self.tokenizer.keyword() == "var":
            self.compile_var_dec()
        self.compile_statements()
        self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
        self.output_stream.write("</subroutineBody>\n")
        self.output_stream.write("</subroutineDec>\n")
        self.tokenizer.advance()

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list."""
        self.output_stream.write("<parameterList>\n")
        while self.tokenizer.token_type() != 'SYMBOL' :
            if self.tokenizer.token_type() == 'KEYWORD':
                self.output_stream.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")
            elif self.tokenizer.token_type() == 'IDENTIFIER':
                self.output_stream.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
            self.tokenizer.advance()
            self.output_stream.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
            self.tokenizer.advance()
            if self.tokenizer.symbol() == ",":
                self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
                self.tokenizer.advance()
        self.output_stream.write("</parameterList>\n")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.output_stream.write("<varDec>\n")
        self.output_stream.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")
        self.tokenizer.advance()
        self.compile_type_and_var_name()
        self.output_stream.write("</varDec>\n")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements."""
        self.output_stream.write("<statements>\n")
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
        self.output_stream.write("</statements>\n")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.output_stream.write("<doStatement>\n")
        self.output_stream.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")
        self.tokenizer.advance()
        self.output_stream.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
        self.tokenizer.advance()
        if self.tokenizer.symbol() == ".":
            self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
            self.tokenizer.advance()
            self.output_stream.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
            self.tokenizer.advance()
        self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
        self.tokenizer.advance()
        self.compile_expression_list()
        self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
        self.tokenizer.advance()
        self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
        self.output_stream.write("</doStatement>\n")
        self.tokenizer.advance()

    def compile_let(self) -> None:
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
        self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n") # =
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
        self.output_stream.write("<returnStatement>\n")
        self.output_stream.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")
        self.tokenizer.advance()
        if self.tokenizer.current_token != ";":
            self.compile_expression()
        self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
        self.output_stream.write("</returnStatement>\n")
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
        """Compiles a term."""
        self.output_stream.write("<term>\n")
        if self.tokenizer.token_type() == 'INT_CONST':
            self.output_stream.write(f"<integerConstant> {self.tokenizer.int_val()} </integerConstant>\n")
            self.tokenizer.advance()
        elif self.tokenizer.token_type() == 'STRING_CONST':
            # Handle string constants
            string_value = self.tokenizer.string_val()
            # Escape special XML characters in the string
            escaped_string = (string_value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
            self.output_stream.write(f"<stringConstant> {escaped_string} </stringConstant>\n")
            self.tokenizer.advance()
        elif self.tokenizer.token_type() == 'KEYWORD':
            self.output_stream.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")
            self.tokenizer.advance()
        elif self.tokenizer.token_type() == 'IDENTIFIER':
            self.output_stream.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
            self.tokenizer.advance()
            if self.tokenizer.symbol() == "[":
                self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
                self.tokenizer.advance()
                self.compile_expression()
                self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
                self.tokenizer.advance()
            elif self.tokenizer.symbol() == ".":
                self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
                self.tokenizer.advance()
                self.output_stream.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
                self.tokenizer.advance()
                self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
                self.tokenizer.advance()
                self.compile_expression_list()
                self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
                self.tokenizer.advance()
            elif self.tokenizer.symbol() == "(":
                self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
                self.tokenizer.advance()
                self.compile_expression_list()
                self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
                self.tokenizer.advance()
        elif self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == "(":
            self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
            self.tokenizer.advance()
            self.compile_expression()
            self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
            self.tokenizer.advance()
        elif self.tokenizer.symbol() in ["~", "-"]:
            self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
            self.tokenizer.advance()
            self.compile_term()
        self.output_stream.write("</term>\n")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.output_stream.write("<expression>\n")
        self.compile_term()
        while self.tokenizer.current_token in ["+", "-", "*", "/", "|", "=","<", ">", "&"]:
            self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
            self.tokenizer.advance()
            self.compile_term()
        self.output_stream.write("</expression>\n")

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.output_stream.write("<expressionList>\n")
        if self.tokenizer.token_type() != 'SYMBOL' or self.tokenizer.symbol() != ")":
            self.compile_expression()
            while self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == ",":
                self.output_stream.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
                self.tokenizer.advance()
                self.compile_expression()
        self.output_stream.write("</expressionList>\n")

    def compile_type_and_var_name(self) -> None:
        """Compiles type and variable name."""
        if self.tokenizer.token_type() == 'KEYWORD':
            self.output_stream.write(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")
        elif self.tokenizer.token_type() =='IDENTIFIER':
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
