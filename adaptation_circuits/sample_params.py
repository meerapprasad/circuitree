import numpy as np

# k ~ 0.1-10, K ~.001-100
k_range = (.1, 10)
K_range = (.001, 100)
PARAM_RANGES= [k_range, K_range]
# todo: sample with latin hypercube sampling, double check that these are correct

def sample_ode_params(components, seed):
    m = components
    # input takes the same index as E or F
    # k_F and k_E terms are at the end of the k_cat and K_thresh matrices
    # nfblb
    k_cat = np.full((2, m+1, m+1), 1e-1)
    K_thresh = np.full((2, m+1, m+1), 1e-2)
    # # ifflp
    # k_cat = np.full((2, m+1, m+1), .5)
    # k_cat[:,-1] = 10
    # k_cat[...,-1] = 10
    # K_thresh = np.full((2, m+1, m+1), 1e-3)
    # K_thresh[:,-1] = 100
    # K_thresh[...,-1] = 100

    return k_cat, K_thresh


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


# def make_param_db():

# print('done')






# def lhs_sample(components, k_range=(0.1, 10), K_range=(0.001, 100), n=10000):
#     # k ~ 0.1-10, K ~.001-100
#     dimensions = components + 1
#
#     # Generates LHS samples for each entry in the matrix over n samples
#     def generate_lhs_samples(lower_bound, upper_bound, size, n_samples):
#         range_size = upper_bound - lower_bound
#         step = range_size / n_samples
#
#         # Initialize the output samples array with extra dimension for n samples
#         samples = np.zeros((n_samples,) + size)
#
#         # LHS: Each sample must be unique across the sample space
#         for i in range(n_samples):
#             # Shuffle along each dimension to ensure each sample is from a unique 'slice' of the LHS
#             for dim in range(size[1]):  # Assuming size is (2, dimensions, dimensions)
#                 random_offset = np.random.rand(*size[1:]) * step
#                 indices = np.random.permutation(n_samples)
#                 samples[:, size[0]-1, dim, :] = lower_bound + (indices + random_offset) * step
#
#         return samples
#
#     matrix_shape = (2, dimensions, dimensions)
#
#     # Generate samples for k_cat and K_thresh
#     k_cat_samples = generate_lhs_samples(k_range[0], k_range[1], matrix_shape, n)
#     K_thresh_samples = generate_lhs_samples(K_range[0], K_range[1], matrix_shape, n)
#
#     return k_cat_samples, K_thresh_samples