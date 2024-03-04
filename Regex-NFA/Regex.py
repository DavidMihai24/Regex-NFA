from .NFA import NFA, EPSILON
from dataclasses import dataclass
from .Tokens import CharType, OperationType, ParanthesisType

class Regex:
    def thompson(self) -> NFA[int]:
        raise NotImplementedError('the thompson method of the Regex class should never be called')

# you should extend this class with the type constructors of regular expressions and overwrite the 'thompson' method
# with the specific nfa patterns. for example, parse_regex('ab').thompson() should return something like:

# >(0) --a--> (1) -epsilon-> (2) --b--> ((3))

# extra hint: you can implement each subtype of regex as a @dataclass extending Regex


def getState():
    state = 0
    while True:
        state += 1
        yield state

@dataclass
class Character(Regex):
    c: str

    def thompson(self) -> NFA[int]:
        start = getState()
        end = getState()
        S = set()
        K = set()
        q0 = 0
        D = dict()
        F = set()

        S.add(self.c)

        K.add(start)
        K.add(end)        
        
        q0 = start
        
        D[(start, self.c)] = {end}
        
        F.add(end)

        return NFA(S, K, q0, D, F)

@dataclass
class Concatenation(Regex): # .
    r1: Regex
    r2: Regex

    def thompson(self) -> NFA[int]:
        nfa1 = self.r1.thompson()
        nfa2 = self.r2.thompson()

        S = nfa1.S.union(nfa2.S)
        K = nfa1.K.union(nfa2.K)
        q0 = nfa1.q0
        D = nfa1.d.copy()
        D.update(nfa2.d)
        F = nfa2.F

        for state in nfa1.F:
            D[(state, EPSILON)] = {nfa2.q0}

        return NFA(S, K, q0, D, F)

@dataclass
class Union(Regex): # |
    r1: Regex
    r2: Regex

    def thompson(self) -> NFA[int]:
        nfa1 = self.r1.thompson()
        nfa2 = self.r2.thompson()
        start = getState()
        end = getState()
        
        S = nfa1.S.union(nfa2.S)

        K = nfa1.K.union(nfa2.K)
        K.add(start)
        K.add(end)

        q0 = start

        d = nfa1.d.copy()
        d.update(nfa2.d)

        d[start, EPSILON] = {nfa1.q0, nfa2.q0}

        for state in nfa1.F:
            d[(state, EPSILON)] = {end}

        for state in nfa2.F:
            d[(state, EPSILON)] = {end}

        F = {end}

        return NFA(S, K, q0, d, F)

@dataclass
class KleeneStar(Regex): # *
    r: Regex
    
    def thompson(self) -> NFA[int]:
        nfa = self.r.thompson()
        start = getState()
        end = getState()

        S = nfa.S

        K = nfa.K
        K.add(start)
        K.add(end)

        q0 = start

        d = nfa.d.copy()

        d[start, EPSILON] = {nfa.q0, end}

        for state in nfa.F:
            d[(state, EPSILON)] = {nfa.q0, end}

        F = {end}

        return NFA(S, K, q0, d, F)

@dataclass
class OneOrNone(Regex): # ?
    r: Regex

    def thompson(self) -> NFA[int]:
        regexForEPS = Character(EPSILON)

        return Union(self.r, regexForEPS).thompson()

@dataclass
class OneOrMore(Regex): # +
    r: Regex

    def thompson(self) -> NFA[int]:
        return Concatenation(self.r, KleeneStar(self.r)).thompson()

def priority(char: str) -> int:
    if char == OperationType('+'):
        return 3
    elif char == OperationType('*'):
        return 3
    elif char == OperationType('?'):
        return 3
    elif char == OperationType('.'):
        return 2
    elif char == OperationType('|'):
        return 1
    return 0

def shuntingYard(tokens: list) -> list:
    tokens.reverse()
    
    for i in range(len(tokens)):
        if isinstance(tokens[i], ParanthesisType):
            if tokens[i].par == '(':
                tokens[i].par = ')'
            elif tokens[i].par == ')':
                tokens[i].par = '('

    tokens.insert(0, ParanthesisType('('))
    tokens.append(ParanthesisType(')'))

    stack = []
    prefix_form = []

    for token in tokens:

        if isinstance(token, CharType):
            prefix_form.append(token)

        elif token == ParanthesisType('('):
            stack.append(token)

        elif token == ParanthesisType(')'):
            while stack[-1] != ParanthesisType('('):
                prefix_form.append(stack.pop())
            stack.pop()

        else:
            if isinstance(stack[-1], OperationType):
                while priority(token) <= priority(stack[-1]):
                    prefix_form.append(stack.pop())

            else:
                while priority(token) <= priority(stack[-1]):
                    prefix_form.append(stack.pop())
            
            stack.append(token)

    while stack:
        prefix_form.append(stack.pop())

    prefix_form.reverse()

    return prefix_form

def getRegex(regex: list):
    token = regex.pop(0)

    if isinstance(token, CharType):
        return Character(token.char)
    
    elif isinstance(token, OperationType):
        if token.op == '?':
            return OneOrNone(getRegex(regex))    

        if token.op == '*':
            return KleeneStar(getRegex(regex))
        
        if token.op == '+':
            return OneOrMore(getRegex(regex))
        
        if token.op == '.':
            return Concatenation(getRegex(regex), getRegex(regex))
        
        if token.op == '|':
            return Union(getRegex(regex), getRegex(regex))

def parse_regex(regex: str) -> Regex:
    regex = list(regex)
    tokens = []

    pos = 0
    while pos < len(regex):
        char = regex[pos]

        if char == '[':
            start = ord(regex[pos + 1])
            end = ord(regex[pos + 3])
            
            tokens.append(ParanthesisType('('))
            for i in range(start, end + 1):
                tokens.append(CharType(chr(i)))
                if i != end:
                    tokens.append(OperationType('|'))
                else:
                    tokens.append(ParanthesisType(')'))        
            pos += 4

        elif char == '\\':
            tokens.append(CharType(regex[pos + 1]))
            pos += 1
        
        elif char == '(' or char == ')':
            tokens.append(ParanthesisType(regex[pos]))
        
        elif char == '|' or char == '*' or char == '?' or char == '+':
            tokens.append(OperationType(regex[pos]))
        
        elif char != ' ':
            tokens.append(CharType(regex[pos]))
        
        pos += 1

    pos = 0
    while pos < len(tokens) - 1:
        current = tokens[pos]
        next_token = tokens[pos + 1]

        if isinstance(current, CharType) and (isinstance(next_token, CharType) or next_token == ParanthesisType('(')):
            tokens.insert(pos + 1, OperationType('.'))
            pos += 1
        
        elif current == ParanthesisType(')') and isinstance(next_token, CharType):
            tokens.insert(pos + 1, OperationType('.'))
            pos += 1

        elif current in [OperationType('*'), OperationType('?'), OperationType('+')] and (isinstance(next_token, CharType) or next_token == ParanthesisType('(')):
            tokens.insert(pos + 1, OperationType('.'))
            pos += 1

        elif current == ParanthesisType(')') and next_token == ParanthesisType('('):
            tokens.insert(pos + 1, OperationType('.'))
            pos += 1
        
        pos += 1

    prefix = shuntingYard(tokens)

    return getRegex(prefix)