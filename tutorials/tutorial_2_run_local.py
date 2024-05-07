from tutorial_2_parallel_example import ParallelBistabilityTree

if __name__ == "__main__":

    tree = ParallelBistabilityTree(root="ABC::")

    tree.search_mcts_parallel(
        n_steps=10_000,
        n_threads=10,
        run_kwargs=dict(expensive=True),
    )
    print("Done!")
