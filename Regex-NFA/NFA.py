from .DFA import DFA

from dataclasses import dataclass
from collections.abc import Callable

EPSILON = ''  # this is how epsilon is represented by the checker in the transition function of NFAs


@dataclass
class NFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], set[STATE]]
    F: set[STATE]

    def epsilon_closure(self, state: STATE) -> set[STATE]:
        # compute the epsilon closure of a state (you will need this for subset construction)
        # see the EPSILON definition at the top of this file
        closure = set()
        visited = set()

        # Depth-First Search
        def dfs(current_state):
            visited.add(current_state)
            closure.add(current_state)

            # Setul starilor in care putem ajunge cu tranzitie epsilon
            epsilon_transitions = self.d.get((current_state, EPSILON), set())

            for next_state in epsilon_transitions:
                if next_state not in visited:
                    dfs(next_state)

        dfs(state)
        return closure

    def subset_construction(self) -> DFA[frozenset[STATE]]:
        # convert this nfa to a dfa using the subset construction algorithm
        alphabet = self.S
        dfa_initial_state = frozenset(self.epsilon_closure(self.q0))
        dfa_transitions = {}
        dfa_final_states = set()

        unmarked_states = [dfa_initial_state]
        marked_states = set()

        while unmarked_states:
            current_states = unmarked_states.pop()
            marked_states.add(current_states)

            for symbol in alphabet:
                next_states = set()
                # Gasim tranzitiile pentru fiecare stare din setul curent
                for nfa_state in current_states:
                    transitions = self.d.get((nfa_state, symbol), set())
                    # Updatam setul starilor urmatoare
                    for state in transitions:
                        next_states.update(self.epsilon_closure(state))

                next_states_frozen = frozenset(next_states)

                # Daca setul starilor urmatoare nu a fost deja procesat, il adaugam in coada
                if next_states_frozen not in marked_states.union(unmarked_states):
                    unmarked_states.append(next_states_frozen)

                # Adaugam tranzitia in DFA
                dfa_transitions[(current_states, symbol)] = next_states_frozen

                # Vedem care stari din cele procesate sunt finale
                for state in marked_states:
                    if self.F.intersection(state):
                        dfa_final_states.add(state)

        return DFA(S=alphabet, K=marked_states, q0=dfa_initial_state, d=dfa_transitions, F=dfa_final_states)

    def remap_states[OTHER_STATE](self, f: 'Callable[[STATE], OTHER_STATE]') -> 'NFA[OTHER_STATE]':
        # optional, but may be useful for the second stage of the project. Works similarly to 'remap_states'
        # from the DFA class. See the comments there for more details.
        remapped_states = {f(state) for state in self.K}
        remapped_initial_state = f(self.q0)
        remapped_final_states = {f(state) for state in self.F}
        remapped_transitions = {(f(state), symbol): {f(next_state) for next_state in next_states} for (state, symbol),
                                next_states in self.d.items()}

        return NFA(S=self.S, K=remapped_states, q0=remapped_initial_state, d=remapped_transitions,
                   F=remapped_final_states)
