from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class DFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], STATE]
    F: set[STATE]

    def accept(self, word: str) -> bool:
        # simulate the dfa on the given word, and return True if the word is accepted and False otherwise
        current_state = self.q0
        for symbol in word:
            if symbol not in self.S:
                #print("Symbol not in alphabet!!")
                return False
            if (current_state, symbol) not in self.d:
                return False
            current_state = self.d[(current_state, symbol)]
        return current_state in self.F

    def remap_states[OTHER_STATE](self, f: Callable[[STATE], 'OTHER_STATE']) -> 'DFA[OTHER_STATE]':
        # optional, but might be useful for subset construction and the lexer to avoid state name conflicts.
        # this method generates a new dfa, with renamed state labels, while keeping the overall structure of the
        # automaton.

        # for example, given this dfa:

        # > (0) -a,b-> (1) ----a----> ((2))
        #               \-b-> (3) <-a,b-/
        #                   /     ⬉
        #                   \-a,b-/

        # applying the x -> x+2 function would create the following dfa:

        # > (2) -a,b-> (3) ----a----> ((4))
        #               \-b-> (5) <-a,b-/
        #                   /     ⬉
        #                   \-a,b-/

        remapped_states = {f(state) for state in self.K}
        remapped_initial_state = f(self.q0)
        remapped_final_states = {f(state) for state in self.F}
        remapped_transitions = {(f(state), symbol): f(self.d[(state, symbol)]) for state, symbol in self.d}

        return DFA(S=self.S, K=remapped_states, q0=remapped_initial_state, d=remapped_transitions,
                   F=remapped_final_states)
