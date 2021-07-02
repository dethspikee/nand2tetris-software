from typing import Union


class SymbolTable:
    def __init__(self):
        """
        Creates a new empty symbol table.
        """
        self.table = dict()
    
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
        print(name, type, kind)

    def var_count(self, kind: str) -> int:
        """
        Returns the number of variables of the
        given kind already defined in the current
        scope.
        """
        pass

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
