from types import FunctionType

class Command():
    def __init__(self, command: str, handler: FunctionType, description: str, syntax: str) -> None:
        self.command = command
        self.handler = handler
        self.description = description
        self.syntax = syntax