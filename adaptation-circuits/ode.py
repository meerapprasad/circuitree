import numpy as np
from typing import Optional
from scipy.integrate import odeint
import matplotlib.pyplot as plt


def system_dynamics(pop0, t, components, activations, inhibitions, k_cat, K_hill, inpt=.5, basal=.5, input_node=0,):
    # todo: dynamics is not correct, its saturating very quickly
    E = F = basal
    # number of components
    # store the updated population
    pop_update = np.zeros_like(pop0)
    # store the activation and inhibition terms
    for i in range(0, components):
        activation_term = 0
        inhibition_term = 0
        # Identify components activated by component i.
        activated_by = activations[np.where(activations[:,1] == i)[0]][:,0] if len(activations) > 0 else np.array([])
        # Identify components inhibited by component i.
        inhibited_by = inhibitions[np.where(inhibitions[:,1] == i)[0]][:,0] if len(inhibitions) > 0 else np.array([])

        # add the input term here if not added above
        if i == 0:
            activation_term += inpt * k_cat[0,i, -1] * ((1 - pop0[i]) / ((1 - pop0[i]) + K_hill[0,i, -1]))
        # add basal activation if not components activate the current component i
        if len(activated_by) == 0 and i > input_node:
            activation_term += E * k_cat[0,i, -1] * (1-pop0[i])/ ((1-pop0[i]) + K_hill[0,i, -1])
        # Calculate the inhibition term if no components inhibit the current component i.
        if len(inhibited_by) == 0:
            inhibition_term += F * k_cat[1,i, -1] * pop0[i]/ (pop0[i]+K_hill[1,i, -1])  #if k_hill small, then this>1
        # For each component that activates i, compute contribution to activation term.
        if len(activated_by) > 0:
            for act in activated_by:
                try:
                    activation_term += pop0[act] * k_cat[0,i, act] * ((1-pop0[i]) / ((1-pop0[i]) + K_hill[0,i, act]))
                except (IndexError):
                    print(i, act, components, k_cat.shape, K_hill.shape)
                    raise
        # For each component that inhibits i, compute contribution to inhibition term.
        if len(inhibited_by) > 0:
            for inh in inhibited_by:
                inhibition_term += pop0[inh] * k_cat[1,i, inh] * (pop0[i] / (pop0[i] + K_hill[1,i, inh]))
        # Update the population of component i by calculating the net effect of activation and inhibition.
        pop_update[i] = activation_term.copy() - inhibition_term.copy()

    return pop_update


def solve_dynamics(pop0, time, components, activations, inhibitions, k_cat, K_hill, inpt):
    # todo: maybe cant have input as an array ...
    # print(k_cat.shape, K_hill.shape)
    result = odeint(system_dynamics, pop0, time,
                    args=(components, activations, inhibitions, k_cat, K_hill, inpt))
    return result


