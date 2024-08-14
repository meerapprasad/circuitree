import numpy as np
from scipy.integrate import odeint
from scipy.signal import find_peaks
import time
import matplotlib.pyplot as plt

def system_dynamics(pop0, t, components, activations, inhibitions, k_cat, K_hill, inpt=.5, basal=.5, input_node=0,):
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
                    print(i, act, pop0.shape, components)
                    raise
        # For each component that inhibits i, compute contribution to inhibition term.
        if len(inhibited_by) > 0:
            for inh in inhibited_by:
                try:
                    inhibition_term += pop0[inh] * k_cat[1,i, inh] * (pop0[i] / (pop0[i] + K_hill[1,i, inh]))
                except (IndexError):
                    print(i, inh, pop0.shape, components)
                    raise
        # Update the population of component i by calculating the net effect of activation and inhibition.
        pop_update[i] = activation_term.copy() - inhibition_term.copy()

    return pop_update


def solve_dynamics(pop0, time, components, activations, inhibitions, k_cat, K_hill, inpt):
    # todo: maybe cant have input as an array ...
    # print(k_cat.shape, K_hill.shape)
    result = odeint(system_dynamics, pop0, time,
                    args=(components, activations, inhibitions, k_cat, K_hill, inpt))
    return result


def nfblb2(pop, t, components, activations, inhibitions, k_cat, K_hill, inpt=.5, basal=.5):
  A, B, C = pop
  # print(k_cat.shape, K_hill.shape)
  da_dt = inpt * k_cat[0,0,-1] * (1- A) / ((1-A) + K_hill[0,0,-1]) - basal * k_cat[1,0,-1] * (A/ (A + K_hill[1,0,-1]))
  db_dt = C * k_cat[0,1,2] * (1- B) / ((1-B) + K_hill[0,1,2]) - basal * k_cat[1,1,-1] * (B/ (B + K_hill[1,1,-1]))
  dc_dt = A * k_cat[0,0,2] * (1- C) / ((1-C) + K_hill[0,0,2]) - B * k_cat[1,1,2] * (C / (C + K_hill[1,1,2]))

  return [da_dt, db_dt, dc_dt]


def solve_dynamics(pop0, time, components, activations, inhibitions, k_cat, K_hill, inpt):
    # todo: maybe cant have input as an array ...
    result = odeint(system_dynamics, pop0, time,
                    args=(components, activations, inhibitions, k_cat, K_hill, inpt))
    return result


A0 = 0.1
B0 = 0.1
C0 = 0.1
inpt=basal=.5
initial_conditions = [A0, B0, C0]
t_end = 500
t = np.linspace(0, t_end, t_end*10)  # from t=0 to t=50, with 500 points
t2 = np.linspace(0, t_end/2, t_end*10)  # from t=50 to t=100, with 500 points
activations = np.array([[0, 2], [2, 1]])
inhibitions = np.array([[1, 2]])
m=3

k_range = (.1, 10)
K_range = (.001, 100)
PARAM_RANGES= [k_range, K_range]

def latin_hypercube_sampling(n_samples, rg, n_params, param_ranges=PARAM_RANGES):  # n_params= forward and reverse
    # Check if param_ranges has the correct length
    if len(param_ranges) != n_params:
        raise ValueError("Length of param_ranges must match n_params")
    # Create an empty array to hold the parameter sets
    samples = np.zeros((n_samples, n_params))
    # Fill in the samples array with scaled Latin Hypercube samples
    for i in range(n_params):
        # Generate uniformly distributed samples within [0, 1]
        param_samples = rg.uniform(0,1, size=n_samples)
        # Scale and shift samples to the given range for the parameter
        min_val, max_val = param_ranges[i]
        param_samples = min_val + param_samples * (max_val - min_val)
        # Shuffle the samples to ensure Latin Hypercube property
        rg.shuffle(param_samples)
        # Assign the shuffled samples to the appropriate column in the samples array
        samples[:, i] = param_samples
    return samples


def make_input_vals(init_val=.5, perc_increase=.2):
    """returns a tuple of input vals"""
    inpt = (init_val, init_val+init_val*perc_increase)
    return inpt

# todo: how to tell when it has reached steady state? measure slopes of the curves and see if they are <.001 ?


def generate_samples(max_components, rg, n_samples, n_params=2):
    sample_per_component = {}
    for i in range(1, max_components+1):
        m = i+1
        sampling = latin_hypercube_sampling(n_samples*2*m*m, rg, n_params=n_params)  # consider forward and reverse rxn
        k_cat = sampling[:, 0].reshape(n_params,m,m, n_samples)[np.newaxis]
        K_thresh = sampling[:, 1].reshape(n_params,m,m, n_samples)[np.newaxis]
        sample_per_component[i] = np.vstack([k_cat, K_thresh])
    # access the params sample_per_component[i][:,0] and unlist k_cat, K_thresh
    return sample_per_component

rg = np.random.default_rng(2024)
inpt = [.5, .6]

sample_per_component_dict = generate_samples(3, rg, int(1e4))
results_dict = {}


from scipy.stats import qmc

# Define parameter ranges in log scale
PARAM_RANGES = [(np.log10(0.1), np.log10(10)), (np.log10(0.001), np.log10(100))]


def latin_hypercube_sampling2(n_samples, rg, n_params, param_ranges=PARAM_RANGES):
    # Check if param_ranges has the correct length
    if len(param_ranges) != n_params:
        raise ValueError("Length of param_ranges must match n_params")

    # Create a Latin Hypercube sampler
    sampler = qmc.LatinHypercube(d=n_params, seed=rg)

    # Generate uniformly distributed samples within [0, 1] using the sampler
    param_samples = sampler.random(n_samples)

    # Scale the samples to the given range for each parameter and exponentiate
    for i in range(n_params):
        min_val, max_val = param_ranges[i]
        param_samples[:, i] = np.power(10, min_val + param_samples[:, i] * (max_val - min_val))

    return param_samples


def generate_samples(max_components, rg, n_samples, n_params=2):
    sample_per_component = {}
    for i in range(1, max_components + 1):
        m = i + 1
        sampling = latin_hypercube_sampling2(n_samples * 2 * m * m, rg,
                                            n_params=n_params)  # consider forward and reverse rxn
        k_cat = sampling[:, 0].reshape(n_params, m, m, n_samples)[np.newaxis]
        K_thresh = sampling[:, 1].reshape(n_params, m, m, n_samples)[np.newaxis]
        sample_per_component[i] = np.vstack([k_cat, K_thresh])
    # access the params sample_per_component[i][:,0] and unlist k_cat, K_thresh
    return sample_per_component


# Example usage
rg = np.random.default_rng(seed=42)
sample_per_component_dict = generate_samples(max_components=3, rg=rg, n_samples=10000, n_params=2)

def plot_dynamics(out, out2):
    o3 = np.vstack([out, out2])
    plt.plot(o3[:,0], label='A')
    plt.plot(o3[:,1], label='B')
    plt.plot(o3[:,2], label='O')
    plt.legend()
    plt.show()


# if the precision is inverse sensitivity it means that there is no peak for the sensitivity -- why not ?
def compute_precision_sensitivity(inpt, out, out2, out_node=-1):
    """
    Precision: abs(((O_2 - O_1)/ O_1) / (I_2 - I_1)/I_1 )^-1
    Sensitivity: abs(((O_peak - O_1)/O_1) / (I_2 - I_1)/I_1)
    """
    # end of O_1 is steady state
    # O_peak1 = out[:,out_node][-1]
    O_1 = out[:,out_node][-1]
    O_peak1 = abs(np.max(out2[:,out_node]) - O_1)
    O_peak = abs(out2[:,out_node][-20:].max() - O_1)
    delta_I = abs(inpt[1] - inpt[0]) /inpt[0]
    precision = ((O_peak / O_1) / delta_I)**-1
    sensitivity = (O_peak1 / O_1) / delta_I
    # if (O_peak1 - O_peak >= .001):
    #     plot_dynamics(out, out2)
    return precision, sensitivity


def autocorr(x):
    x = x - x.mean(axis=0)
    result = np.correlate(x, x, mode='full')
    norm_result = result / np.max(result)
    return norm_result[norm_result.size//2:]

def plot_acorr(acorr):
    plt.plot(acorr[:,0])
    plt.plot(acorr[:,1])
    plt.plot(acorr[:,2])
    plt.show()

def sustained_oscillation(data):
    """Classify if there are sustained oscillations based on autocorrelation."""
    # Compute the autocorrelation
    acorr = np.apply_along_axis(autocorr, 0, data)
    if acorr.min() < -.4:
        plot_acorr(acorr)
        return True
    else:
        return False

# todo: make sure this works
def damped_oscillation(out, out2, out_node=-1, threshold=0.001):
    """Filter out damped oscillations from a dataset. evaluate from the second steady state, not the first"""
    steady_state = out[:, out_node][-1]
    peak_idx = find_peaks(out2[:, out_node])[0]
    # not enough peaks to determine oscillatory behavior or the peaks are too small
    if len(peak_idx) < 2 or (np.diff(peak_idx) <= .01).sum() == len(peak_idx):
        return True
    else:
        peak_values = out2[:, out_node][peak_idx]
        # todo: check if the first peak is 2x the second peak
        steady_state2 = out2[:, out_node][-1]
        trough_1 = out2[peak_idx[0]:peak_idx[1],out_node].min()
        O_peak1 = peak_values[0] - steady_state2
        O_peak2 = steady_state2 - trough_1
        return O_peak2 > .5 * O_peak1  # or abs(O_peak1 - O_peak2) <= threshold  # continue if criteria is passed


start_time = time.time()

for i in range(0, sample_per_component_dict[3].shape[-1]):
  m=3
  k_cat = sample_per_component_dict[3][0,:,:,:,i]
  K_hill = sample_per_component_dict[3][1,:,:,:,i]
  out = solve_dynamics(initial_conditions, t, m, activations, inhibitions, k_cat, K_hill, inpt=inpt[0])
  if sustained_oscillation(out):
    results_dict[i] = 0
  else:
    out2 = solve_dynamics(out[-1], t, m, activations, inhibitions, k_cat, K_hill, inpt=inpt[1])
    # check for sustained oscillation as well?
    if damped_oscillation(out, out2):
        precision, sensitivity = compute_precision_sensitivity(inpt, out, out2)
        results_dict[i] = [precision, sensitivity]
    else:
        results_dict[i] = 0

end_time = time.time()
elapsed_time = end_time - start_time
print(f"exhaustive search one topology: {elapsed_time}")




pos_top = 0
for i in range(0, sample_per_component_dict[3].shape[-1]):
    if results_dict[i] == 0:
        k_cat = sample_per_component_dict[3][0, :, :, :, i]
        K_hill = sample_per_component_dict[3][1, :, :, :, i]
        out = solve_dynamics(initial_conditions, t, m, activations, inhibitions, k_cat, K_hill, inpt=inpt[0])
        out2 = solve_dynamics(out[-1], t2, m, activations, inhibitions, k_cat, K_hill, inpt=inpt[1])
        plot_dynamics(out, out2)
    else:
        k_cat = sample_per_component_dict[3][0, :, :, :, i]
        K_hill = sample_per_component_dict[3][1, :, :, :, i]
        precision, sensitivity = np.log10(results_dict[i])
        if np.log10(precision) >= 1 and np.log10(sensitivity) >= -.01:
            pos_top += 1
            out = solve_dynamics(initial_conditions, t, m, activations, inhibitions, k_cat, K_hill, inpt=inpt[0])
            out2 = solve_dynamics(out[-1], t2, m, activations, inhibitions, k_cat, K_hill, inpt=inpt[1])
            # plot_dynamics(out, out2)
        else:
            continue

i= 987
k_cat = sample_per_component_dict[3][0, :, :, :, i]
K_hill = sample_per_component_dict[3][1, :, :, :, i]
out = solve_dynamics(initial_conditions, t, m, activations, inhibitions, k_cat, K_hill, inpt=inpt[0])
out2 = solve_dynamics(out[-1], t2, m, activations, inhibitions, k_cat, K_hill, inpt=inpt[1])
plot_dynamics(out, out2)

# todo: filter 0 values, and/or check if there are sustained oscillations with the 0 values


print('done')