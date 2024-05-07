## todo: given the number of nodes, determine the number of topologies,
# Complexity: 3**N**2 , actions = inhibit, activate, none , N = number of nodes
from itertools import product, permutations
import networkx as nx
import numpy as np

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

# Example usage
nodes = ['A', 'B', 'C']
actions = {'a', 'i', 'None'}
topologies = generate_topologies_with_optional_pairs(nodes, actions)

# len(valid_topologies) = 16038
valid_topologies = filter_topologies_with_path(topologies[1:], 'A', 'C')
print(valid_topologies)


# todo: create a database with all topologies that has the index order for the topologies,
#  also indexes the dict with the nodes

n_samples = 1e4
param_order = np.full((len(topologies[1:]), int(n_samples)), np.arange(n_samples).astype(int))
# todo: use the rg here for reproducibility
for row in param_order:
    np.random.shuffle(row)

param_table_order = dict(zip(topologies[1:], param_order.tolist()))

# todo: make sure to split the ABC:: and the topology when indexing

# todo: make a counter for visiting each topology


import networkx as nx
from itertools import permutations, product

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

# def filter_connected_topologies_with_path(topologies, source, destination, nodes):
#     """
#     Filter the topologies that have a direct or indirect path between source and destination nodes and ensure all graphs are connected.
#
#     Parameters:
#     topologies (list): List of topology strings.
#     source (str): The source node name.
#     destination (str): The destination node name.
#     nodes (list): List of all nodes in the graph.
#
#     Returns:
#     list: List of topology strings that have a path between the source and destination nodes.
#     """
#     valid_topologies = []
#
#     for topology in topologies:
#         graph = nx.DiGraph()
#         # Split the topology string using the underscore to get each edge description
#         pairs = topology.split('_')
#         for pair in pairs:
#             src = pair[0]
#             dst = pair[1]
#             graph.add_edge(src, dst)
#
#         # Check if all nodes are included and the graph is strongly connected
#         if set(graph.nodes()) == set(nodes) and nx.is_strongly_connected(graph):
#             # Check if there's a path between the source and destination
#             if nx.has_path(graph, source, destination):
#                 valid_topologies.append(topology)
#
#     return valid_topologies
#
# # Example usage
# nodes = ['A', 'B', 'C']
# actions = {'a', 'i', 'None'}
# topologies = generate_topologies_with_optional_pairs(nodes, actions)
#
# # Filter for strongly connected graphs with a path between A and C
# valid_topologies = filter_connected_topologies_with_path(topologies[1:], 'A', 'C', nodes)
# print(valid_topologies)