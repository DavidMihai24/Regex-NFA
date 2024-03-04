class CharType:
    def __init__(self, char: str):
        self.char = char

    def __repr__(self) -> str:
        return f'C: {self.char}'
    
class OperationType:
    def __init__(self, operation: str):
        self.op = operation

    def __eq__(self, other: object) -> bool:
        if isinstance(other, OperationType):
            return self.op == other.op
        return False
    
class ParanthesisType:
    def __init__(self, par: str):
        self.par = par

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ParanthesisType):
            return self.par == other.par
        return False