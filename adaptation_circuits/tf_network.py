import numpy as np
from adaptation_circuits.ode import solve_dynamics
from adaptation_circuits.reward import compute_precision_sensitivity
from adaptation_circuits.sample_params import make_input_vals, sample_ode_params
from adaptation_circuits.filter_oscillation import damped_oscillation, sustained_oscillation
from circuitree import SimpleNetworkGrammar
from adaptation_circuits.enumerate_topologies import count_unique_uppercase_letters, convert_to_sequential, filter_topology_with_path


class TFNetworkModel:
    def __init__(
            self,
            rg,
            genotype,
            # max_iter_per_timestep,  # makes sure it doesn't run forever, not implemented yet
            inpt_perc_increase=.2,
            params=None,
    ):

        self.genotype = genotype

        (
            self.components,
            self.activations,
            self.inhibitions,
        ) = SimpleNetworkGrammar.parse_genotype(genotype)
        self.n_species, self.components_as_num = count_unique_uppercase_letters(self.genotype.split("::")[1])
        # print(self.n_species, self.components_as_num)
        # print(self.activations, len(self.activations))
        # print(self.inhibitions, len(self.inhibitions))
        self.max_components = len(self.genotype.split("::")[0].split("*")[1])
        # print(self.n_species, self.max_components)
        self.stabilize_tp = np.linspace(0, 5000, 20000)
        self.eval_tp = np.linspace(0, 2500, 10000)
        # todo: need to reach steady state and then add the step function -- track the slope of the counts ?
        # todo: define the input globally
        self.inpt = make_input_vals(perc_increase=inpt_perc_increase)
        self.rg = rg
        # todo: index from a list of params
        if params is not None:
            self.k_cat, self.K_thresh = params
        else:
            self.k_cat, self.K_thresh = sample_ode_params(self.n_species, self.rg)
        self.pop0 = np.full(self.n_species, .05)

    def run_ode_with_params(self):
        # check that there is a connection bw input and output in the graph
        if filter_topology_with_path(self.genotype, source='A', destination='O'):
            print(self.genotype)
            # convert activations and inhibitions to numbers, # todo: still does not work
            activations = convert_to_sequential(self.activations, self.components_as_num, self.max_components) \
                if self.n_species < self.max_components else self.activations
            inhibitions = convert_to_sequential(self.inhibitions, self.components_as_num, self.max_components) \
                if self.n_species < self.max_components else self.inhibitions

            out = solve_dynamics(self.pop0, self.stabilize_tp, self.n_species, activations, inhibitions,
                                 self.k_cat, self.K_thresh, self.inpt[0])
            # exclude sustained oscillation -- todo: this doesnt work
            if sustained_oscillation(out):
                plot_dynamics(out)
                return 0
            # else:  # continue
            out2 = solve_dynamics(out[-1], self.eval_tp, self.n_species, activations, inhibitions, self.k_cat,
                                  self.K_thresh, self.inpt[1])
            # check for sustained oscillation as well?
            if damped_oscillation(out, out2):
                precision, sensitivity = compute_precision_sensitivity(self.inpt, out, out2)
                # todo: incorporate some saving
                # self.track_pop = np.concatenate([out, out2])
                # self.precision = precision
                # self.sensitivity = sensitivity
                print('precision: ', np.log10(precision), '\nsensitivity: ', np.log10(sensitivity))
                plot_dynamics2(out, out2)
                # todo: why is my sensitivity < 0???
                if np.log10(precision) >= 1 and np.log10(sensitivity) >= -5:
                    return 1
                else:
                    return 0
        # dont bother evaluating dynamics if there is not a direct path bw input and output nodes
        else:
            return 0

    def initialize_ode_params(self, n_species):
        self.k_cat, self.K_thresh = sample_ode_params(n_species, self.rg)

    def save_dynamics(self):
        # todo: include plotting
        pass


import matplotlib.pyplot as plt
def plot_dynamics(out):
    plt.plot(out[:,0], label='A')
    plt.plot(out[:,1], label='B')
    plt.plot(out[:,2], label='C')
    plt.xlabel('time')
    plt.ylabel('counts')
    plt.legend()
    plt.show()


def plot_dynamics2(out, out2):
    o3 = np.vstack([out, out2])
    plt.plot(o3[:,0], label='A')
    plt.plot(o3[:,1], label='B')
    plt.plot(o3[:,2], label='C')
    plt.xlabel('time')
    plt.ylabel('counts')
    plt.legend()
    plt.show()
