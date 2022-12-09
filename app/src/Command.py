from types import FunctionType

class Command():
    def __init__(self, command: str, handler: FunctionType, syntax: str) -> None:
        self.command = command
        self.handler = handler
        self.syntax = syntax