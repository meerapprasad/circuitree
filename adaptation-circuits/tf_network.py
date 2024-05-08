import numpy as np
from ode import solve_dynamics
from reward import compute_precision_sensitivity
from sample_params import make_input_vals, sample_ode_params
from filter_oscillation import damped_oscillation, sustained_oscillation
from circuitree import SimpleNetworkGrammar


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
        self.n_species = len(self.components)

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
        self.pop0 = np.full(3, .05)

    def run_ode_with_params(self):
        out = solve_dynamics(self.pop0, self.stabilize_tp, self.n_species, self.activations, self.inhibitions,
                             self.k_cat, self.K_thresh, self.inpt[0])
        # exclude sustained oscillation
        if sustained_oscillation(out):
            return 1
        else:  # continue
            out2 = solve_dynamics(out[-1], self.eval_tp, self.n_species, self.activations, self.inhibitions, self.k_cat,
                                  self.K_thresh, self.inpt[1])
            if damped_oscillation(out, out2):
                return 1
            else:
                precision, sensitivity = compute_precision_sensitivity(self.inpt, out, out2)
                # todo: incorporate some saving
                self.track_pop = np.concatenate([out, out2])
                self.precision = precision
                self.sensitivity = sensitivity

                if np.log10(precision) >= 1 and np.log10(sensitivity) >= 0:
                    return 0
                else:
                    return 1

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
