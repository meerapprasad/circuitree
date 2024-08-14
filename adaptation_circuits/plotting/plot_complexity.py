from adaptation_circuits.adaptation_tree import AdaptationTree, grammar
import matplotlib.pyplot as plt
from circuitree.viz import plot_network
from circuitree.models import SimpleNetworkGrammar

tree = AdaptationTree.from_file(graph_gml="../tree-backups/240518_adaptation_search_0.gml",
                                attrs_npz="../tree-backups/240518_adaptation_search_0.npz",
                                grammar_cls=SimpleNetworkGrammar)
# Top 10 designs with at least 10 visits
def robustness(state):
    r = tree.graph.nodes[state].get("reward", 0)
    v = tree.graph.nodes[state].get("visits", 1)
    return r / v


# Recall that only the "terminal" states are fully assembled circuits
states = [s for s in tree.terminal_states if tree.graph.nodes[s]["visits"] > 10]
top_10_states = sorted(states, key=robustness, reverse=True)[:10]

# Plot the top 10
fig = plt.figure(figsize=(12, 5))
plt.suptitle("Top 10 bistable circuits and their robustness")
for i, state in enumerate(top_10_states):
    ax = fig.add_subplot(2, 5, i + 1)

    # Plots the network diagram
    plot_network(
        *grammar.parse_genotype(state),
        ax=ax,
        plot_labels=False,
        node_shrink=0.6,
        auto_shrink=0.8,
        offset=0.75,
        padding=0.4
    )
    r = tree.graph.nodes[state]["reward"]
    v = tree.graph.nodes[state]["visits"]
    ax.set_title(f"{r / v:.2f} (n={v})")
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.0, 1.8)
    plt.savefig('test/t1.png')

from circuitree.viz import plot_complexity

# Plotting options
plot_kwargs = dict(
    tree=tree,
    aspect=1.5,
    alpha=0.25,  # transparency of edges
    n_to_highlight=10,  # number of states to highlight with orange circles
    highlight_min_visits=10,  # only highlight states with 10+ visits
)
min_visits_per_move = 10

## Plot
fig = plt.figure(figsize=(15, 5))
plt.suptitle("Search space for the Bistability game")

ax1 = fig.add_subplot(1, 2, 1)
plt.title("All moves")
plot_complexity(fig=fig, ax=ax1, **plot_kwargs)

ax2 = fig.add_subplot(1, 2, 2)
plt.title(f"Moves with {min_visits_per_move}+ visits")
plot_complexity(vlim=(min_visits_per_move, None), fig=fig, ax=ax2, **plot_kwargs)
plt.savefig('test/t2.png')

print('done')
