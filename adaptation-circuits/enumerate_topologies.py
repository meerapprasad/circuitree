## todo: given the number of nodes, determine the number of topologies,
# Complexity: 3**N**2 , actions = inhibit, activate, none , N = number of nodes
from itertools import product, permutations
import networkx as nx
import numpy as np
import string


def generate_topologies_with_optional_pairs(nodes, actions):
    """
    Generate all possible topologies given a list of nodes and a set of actions, including an option for no interaction.

    Parameters:
    nodes (list): List of node names (strings).
    actions (set): Set of action characters (strings), where "None" indicates no interaction.

    Returns:
    list: List of all topology configurations as strings.
    """
    # Generate all possible pairs of nodes, including repeated pairs (self-loops)
    node_pairs = permutations(nodes, 2)  # Pairs where order matters
    all_pairs = list(node_pairs) + [(node, node) for node in nodes]  # Including repeated pairs

    # Generate all combinations of actions for the given pairs
    all_combinations = product(actions, repeat=len(all_pairs))

    # Create formatted strings representing each topology, excluding "None" interactions
    topologies = []
    for combination in all_combinations:
        topology = '_'.join([
            f"{src}{dst}{action}"
            for (src, dst), action in zip(all_pairs, combination)
            if action != "None"
        ])
        topologies.append(topology)

    return topologies


def filter_topologies_with_path(topologies, source, destination):
    """
    Filter the topologies that have a direct or indirect path between source and destination nodes.

    Parameters:
    topologies (list): List of topology strings.
    source (str): The source node name.
    destination (str): The destination node name.

    Returns:
    list: List of topology strings that have a path between the source and destination nodes.
    """
    valid_topologies = []

    for topology in topologies:
        graph = nx.DiGraph()
        # Split the topology string using the underscore to get each edge description
        pairs = topology.split('_')
        for pair in pairs:
            src = pair[0]
            dst = pair[1]
            graph.add_edge(src, dst)

        # Ensure the source and destination nodes are in the graph
        if source in graph and destination in graph:
            # Check if there's a path between the source and destination
            if nx.has_path(graph, source, destination):
                valid_topologies.append(topology)

    return valid_topologies


def filter_connected_topologies(topologies):
    """
    Filter the topologies that are fully connected (weakly connected if directed).

    Parameters:
    topologies (list): List of topology strings.

    Returns:
    list: List of topology strings that are fully connected.
    """
    valid_topologies = []

    for topology in topologies:
        if topology == '':
            continue
        graph = nx.DiGraph()
        # Split the topology string using the underscore to get each edge description
        pairs = topology.split('_')
        for pair in pairs:
            src = pair[0]
            dst = pair[1]
            graph.add_edge(src, dst)

        # Check if the entire graph is weakly connected
        if nx.is_weakly_connected(graph):
            valid_topologies.append(topology)

    return valid_topologies

# Example usage
# nodes = ['A', 'B', 'C']
# actions = {'a', 'i', 'None'}
# topologies = generate_topologies_with_optional_pairs(nodes, actions)
#
# # len(valid_topologies) = 16038
# # valid_topologies = filter_topologies_with_path(topologies[1:], 'A', 'C')
# # print(valid_topologies)
#
# valid_topologies = filter_connected_topologies(topologies[1:])
# print(len(valid_topologies))

# todo: I anticipate problems here bc there are several ways to build the topology where there is only a single node

def enumerate_connected_networks(nodes, actions={'a', 'i', 'None'}):
    # all_letters = string.ascii_uppercase
    # nodes = list(all_letters[:n_components])
    topologies = generate_topologies_with_optional_pairs(nodes, actions)
    empty_top = topologies[0]
    valid_topologies = filter_connected_topologies(topologies)
    return np.append(np.array(valid_topologies), empty_top).tolist()


# create a database with all topologies that has the index order for the topologies, also indexes the dict with the nodes
def build_param_idx_table(nodes, rg, n_samples=1e4):
    valid_topologies = enumerate_connected_networks(nodes)
    param_order = np.full((len(valid_topologies), int(n_samples)), np.arange(n_samples).astype(int))
    for row in param_order:
        rg.shuffle(row)
    return dict(zip(valid_topologies, param_order.tolist()))


def count_unique_uppercase_letters(input_str):
    """
    Count the number of unique uppercase letters in a given string.

    Parameters:
    input_str (str): The input string.

    Returns:
    int: The number of unique uppercase letters in the string.
    """
    # Create a set to hold unique uppercase letters
    unique_uppercase = set()

    # Loop through each character and collect uppercase letters
    for char in input_str:
        if char.isupper():
            unique_uppercase.add(char)

    # Return the number of unique uppercase letters
    return len(unique_uppercase)


def topologies_to_num_params(topologies):
    """
    Convert a list of topology strings to the number of parameters required to describe each topology.

    Parameters:
    topologies (list): List of topology strings.

    Returns:
    dict: Dictionary mapping each topology to the number of parameters required.
    """
    num_params = {}
    for topology in topologies:
        num_params[topology] = count_unique_uppercase_letters(topology)
    return num_params


def find_matching_topology(string, target_list):
    """
    Check if the items in a given string can be reordered to match any string in the provided list,
    and print the matching topology if one exists.

    Parameters:
    string (str): The string containing items separated by underscores.
    target_list (list): List of strings to compare against.

    Returns:
    str or None: The matching topology if the items can be reordered to match any string in the list,
    otherwise `None`.
    """
    # Split the input string into components
    h = string.split('::')[0]
    items = string.split('::')[1].split('_')
    # Sort the items for easier comparison
    sorted_items = sorted(items)

    # Compare against each target string
    for target in target_list:
        # Split the target string and sort its components
        sorted_target = sorted(target.split('_'))

        # Compare sorted versions
        if sorted_items == sorted_target:
            return '::'.join([h,target])  # Return the matching topology

    return string  # No match found