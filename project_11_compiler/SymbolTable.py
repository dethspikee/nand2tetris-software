from typing import Union
from collections import namedtuple
import pprint


class SymbolTable:
    def __init__(self):
        """
        Creates a new empty symbol table.
        """
        self.table = dict()
        self.identifier = namedtuple("Identifier", ["name", "type", "kind", "index"])
    
    def start_subroutine(self) -> None:
        """
        Starts a new subroutine scope
        (i.e., resets the subroutine's
        symbol table).
        """
        pass

    def define(self, name: str, type: str, kind: str) -> None:
        """
        Defines a new identifier of a given name,
        type, and kind and assigns it a running index.
        STATIC and FIELD identifiers have a class scope,
        while ARG and VAR identifiers have a subroutine
        scope.
        """
        if name in self.table:
            # name already defined and in symbol table, throw error?
            pass
        else:
            count = self.var_count(kind)
            self.table[name] = self.identifier(name, type, kind, count)

    def var_count(self, kind: str) -> int:
        """
        Returns the number of variables of the
        given kind already defined in the current
        scope.
        """
        count = 0
        for var in self.table.values():
            if var.kind == kind:
                count += 1
        return count

    def kind_of(self, name: str) -> Union[str, None]:
        """
        Returns the kind of the named
        identifier in the current scope.
        If the identifier is unknown in
        the current scope, returns None.
        """
        pass

    def type_of(self, name: str) -> str:
        """
        Returns the type of the named
        identifier in the current scope.
        """
        pass

    def index_of(self, name: str) -> int:
        """
        Returns the index assigned to the 
        named identifier.
        """
        pass

    def show_table(self) -> None:
        """
        For debugging purposes print state
        of current symbol table to STDOUT.
        """
        pprint.pprint(self.table)
