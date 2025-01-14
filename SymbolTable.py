"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self.class_table = {}
        self.subroutine_table = {}
        self.field_count = 0
        self.static_count = 0
        self.arg_count = 0
        self.local_count = 0
    


    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        self.subroutine_table = {}
        self.arg_count = 0
        self.local_count = 0
        

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        if kind == "static":
            self.class_table[name] = {"type": type, "kind": kind, "index": self.static_count}
            self.static_count += 1
        elif kind == "field":
            self.class_table[name] = {"type": type, "kind": "this", "index": self.field_count}
            self.field_count += 1
        elif kind == "argument":
            self.subroutine_table[name] = {"type": type, "kind": kind, "index": self.arg_count}
            self.arg_count += 1
        elif kind == "var":
            self.subroutine_table[name] = {"type": type, "kind": "local", "index": self.local_count}
            self.local_count += 1

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        if kind == "static":
            return self.static_count
        elif kind == "field":
            return self.field_count
        elif kind == "arg":
            return self.arg_count
        elif kind == "var":
            return self.local_count

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        if name in self.subroutine_table:
            return self.subroutine_table[name]["kind"]
        elif name in self.class_table:
            return self.class_table[name]["kind"]

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        if name in self.subroutine_table:
            return self.subroutine_table[name]["type"]
        elif name in self.class_table:
            return self.class_table[name]["type"]


    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        if name in self.subroutine_table:
            return self.subroutine_table[name]["index"]
        elif name in self.class_table:
            return self.class_table[name]["index"]
