import numpy as np
from circuitree import CircuiTree
from circuitree.models import SimpleNetworkGrammar
from time import sleep

grammar = SimpleNetworkGrammar(
    components=["A", "B", "C"], interactions=["activates", "inhibits"]
)


def get_bistability_reward(
    state: str, rg: np.random.Generator, grammar: SimpleNetworkGrammar
) -> float:
    """Returns a reward value for the given state (topology) based on
    whether it contains positive-feedback loops (PFLs)."""

    # All types of PFLs with up to 3 components
    patterns = [
        "AAa",  # PAR - "AAa" means "A activates A"
        "ABi_BAi",  # Mutual inhibition - "A inhibits B, B inhibits A"
        "ABa_BAa",  # Mutual activation
        "ABa_BCa_CAa",  # Cycle of all activation
        "ABa_BCi_CAi",  # Cycle with two inhibitions
    ]

    # Mean reward increases from 0.25 to 0.75 based on the number of PFLS.
    mean = 0.25
    for pattern in patterns:

        ## The "has_pattern" method returns whether state contains the pattern.
        ## It checks all possible symmetries, so we only need to specify
        ## each pattern once (i.e. 'AAa' is equivalent to 'BBa' and 'CCa')
        if grammar.has_pattern(state, pattern):
            mean += 0.1

    # The CircuiTree object has its own random number generator
    return rg.normal(loc=mean, scale=0.1)


class BistabilityTree(CircuiTree):
    """A subclass of CircuiTree that searches for positive feedback networks.
    Uses the SimpleNetworkGrammar to encode network topologies. In the
    SimpleNetworkGrammar, each topology or 'state' is specified using a 3-part
    string. For instance, a circuit with components 'A', 'B', and 'C' that
    repress each other in a cycle (i.e. the repressilator) would be represented
    as:

      *ABC::ABi_BCi_CA i

     - `::` separates circuit components from pairwise interactions
     - Components are uppercase letters, each type of interaction is a lowercase
       letter.
     - Pairwise interactions are 3-character strings. For exapmle, "ABi" means
       "A inhibits B"
     - A `*` at the beginning indicates that the state is terminal - the
       "termination" action was chosen, and the game has ended.

    The grammar can be accessed with the `self.grammar` attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(grammar=grammar, *args, **kwargs)

        vist_counter = Counter() # from collections import Counter
        param_table: dict[str, tuple] = ...
        # param dict -- gives parameters for each topology, order to index the param table

    def get_param_set_index(self, state: str, visit: int) -> int:
        """Get the index of the parameter set to use for this state and visit number."""

        # Get number of parameters for this state
        n_params = ...

        # Get parameter ranges
        param_ranges: np.array = ...

        # Draw a random parameter set
        rg = np.default_rng(...) # Should depend uniquely on both state and visit_num
        # params_uniform = rg.uniform(0, 1, size=n_params)
        param_set_index = rg.integer(0, self.n_param_sets) #Now, n_param_sets only has uniform random numbers
        param_set = param_ranges[:, 0] + (param_ranges[:, 1] - param_ranges[:, 0]) * params_uniform

        # Shuffle the param sets in a manner unique to each state
        param_set_indices = np.arange(self.n_param_sets)
        hash_val = hash(state) + sys.maxsize  # Make sure it's non-negative
        np.random.default_rng(hash_val).shuffle(param_set_indices)
        return param_set_indices[visit % self.n_param_sets]

    def get_reward(self, state: str, expensive: bool = False) -> float:
        """Returns a reward value for the given state (topology) based on
        whether it contains positive-feedback loops (PFLs)."""

        visit_num = self.visit_counter[state]
        visit_counter[state] += 1

        param_set_idx = self.get_param_set_index(state, visit_num)
        param_set = self.param_sets[param_set_idx]

        reward = get_bistability_reward(state, self.rg, self.grammar, param_set)

        # Simulate a more expensive reward calculation
        if expensive:
            sleep(0.1)

        return reward

    def get_mean_reward(self, state: str) -> float:
        return self.graph.nodes[state].get("reward", 0) / self.graph.nodes[state].get(
            "visits", 1
        )

    def is_success(self, state: str) -> bool:
        """Returns True if the state is terminal and a successful bistable
        circuit. The cumulative reward and number of visits are stored in the
        `reward` and `visits` attributes of each node in the graph.

        A state with no visits is assumed to have a mean reward of 0."""

        if not self.grammar.is_terminal(state):
            return False

        return self.get_mean_reward(state) > 0.5
