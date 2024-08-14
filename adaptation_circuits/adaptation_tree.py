import numpy as np
from circuitree import CircuiTree
from circuitree.models import SimpleNetworkGrammar
from adaptation_circuits.tf_network import TFNetworkModel
from adaptation_circuits.sample_params import generate_samples
from collections import Counter
from adaptation_circuits.enumerate_topologies import build_param_idx_table, topologies_to_num_params
# from time import sleep
import sys
from pathlib import Path
from datetime import datetime
import pickle

today = datetime.now().strftime("%y%m%d")

grammar = SimpleNetworkGrammar(
    components=["A", "B", "O"], interactions=["activates", "inhibits"],
)
# fixed_components=["A", "O"],

class AdaptationTree(CircuiTree):
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

    def __init__(self, grammar: SimpleNetworkGrammar, *args, **kwargs) -> None:
        super().__init__(grammar=grammar, enumerate_topologies=True, *args, **kwargs)
        self.grammar = grammar
        # if args.seed is not None:
        #     self.rg = np.random.default_rng(args.seed)
        # else:
        self.rg = np.random.default_rng(2024)
        self.n_samples = int(kwargs.get('n_samples', 1e3))
        self.visit_counter = Counter()
        self.Q_threshold = .01
        self.successful_params = {}

        # param_table: dict[str, tuple] = ...
        # param dict -- gives parameters for each topology, order to index the param table
        if kwargs.get('generate_param_sets'):
            # order with which parameters should be sampled
            self.param_table = build_param_idx_table(self.grammar.components, self.rg, self.n_samples, top=self.unique_topologies)
            self.topology_size_table = topologies_to_num_params(self.param_table.keys())
            self.param_sets = generate_samples(len(self.grammar.components), self.rg, self.n_samples)
        # todo: save to reload later
        else:
            # load from file
            pass

    def get_param_set_index(self, state: str, visit: int) -> int:
        """Get the index of the parameter set to use for this state and visit number."""
        return self.param_table[state][visit]

    # todo: save params for topologies that work
    def get_reward(self, state: str, expensive: bool = False) -> float:
        """Returns a reward value for the given state (topology)"""
        if state is None:
            return 0
        else:
            # print(state)
            state2 = self.convert_state(state)  # if state is not None else ''
            # todo: this will not be tractable if there are more nodes
            # state = find_matching_topology(state, self.param_table.keys())
            visit_num = self.visit_counter[state2]
            self.visit_counter[state] += 1

            param_set_idx = self.get_param_set_index(state2, visit_num)
            # index param table with 1. number of params and 2. the param set index
            param_set = self.param_sets[self.topology_size_table[state2]][:, :, :, :, param_set_idx]

            model = TFNetworkModel(self.rg, state, params=param_set)
            # todo: param_set needs to be a list of k_cat, K_thresh
            reward = model.run_ode_with_params()
            # save param and topology if successful
            if reward > 0:
                if state2 not in self.successful_params.keys():
                    self.successful_params[state2] = []
                else:
                    self.successful_params[state2].append(param_set_idx)
            print(reward)
            return reward

    def get_mean_reward(self, state: str) -> float:
        if state is None:
            return 0
        else:
            state = self.convert_state(state)
            # state = find_matching_topology(state, self.param_table.keys())
            return self.graph.nodes[state].get("reward", 0) / self.graph.nodes[state].get(
                "visits", 1
            )

    def is_success(self, state: str) -> bool:
        """Returns True if the state is terminal and a successful bistable
        circuit. The cumulative reward and number of visits are stored in the
        `reward` and `visits` attributes of each node in the graph.

        A state with no visits is assumed to have a mean reward of 0."""
        # if not self.grammar.is_terminal(state):
        #     return False
        reward = self.graph.nodes[state]["reward"]
        visits = self.graph.nodes[state]["visits"]
        return visits > 0 and reward / visits >= self.Q_threshold

    # todo: maybe build the database from the tree to avoid searching for matching topologies each time
    def convert_state(self, state: str) -> str:
        # state = find_matching_topology(state, self.param_table.keys())
        return state.split('::')[1]


# tree = AdaptationTree(root='ABO::AOa_BOi_OBa', grammar=grammar, n_samples=1e4, generate_param_sets=True)
tree = AdaptationTree(root='ABO::ABi_BOi_OAi', grammar=grammar, n_samples=1e4, generate_param_sets=True)
# from enumerate_topologies import filter_topologies_with_path
# f_top = filter_topologies_with_path(np.array(tree.unique_topologies)[1:], 'A', 'O')

# Make a backup folder
save_dir = Path("./tree-backups")
save_dir.mkdir(exist_ok=True)

def save_tree_callback(tree: AdaptationTree, iteration: int, *args, **kwargs):
    """Saves the BistabilityTree to two files, a `.gml` file containing the
    graph and a `.json` file with the other attributes."""
    if iteration % 1_000 == 0:
        stem = f"{today}_adaptation_search_{iteration}"
        gml_file = save_dir.joinpath(f"{stem}.gml")
        json_file = save_dir.joinpath(f"{stem}.json")
        tree.to_file(gml_file, json_file)
        # todo: might be a duplicate
        with open(save_dir.joinpath(f"{stem}_successful_params_dict.pkl"), 'wb') as pickle_file:
            pickle.dump(tree.successful_params, pickle_file)


tree.search_mcts_parallel(
    n_steps=10_000,
    n_threads=1,
    callback=save_tree_callback,
    callback_every=500,
    # run_kwargs=dict(expensive=True),
)
print("Done!")

