import scipy.signal
import numpy as np
import matplotlib.pyplot as plt

# todo: smooth the values instead of min/max
def compute_precision_sensitivity(inpt, out, out2, out_node=-1):
    """
    Precision: abs(((O_2 - O_1)/ O_1) / (I_2 - I_1)/I_1 )^-1
    Sensitivity: abs(((O_peak - O_1)/O_1) / (I_2 - I_1)/I_1)
    """
    # end of O_1 is steady state
    # O_peak1 = out[:,out_node][-1]
    O_1 = out[:,out_node][-1]
    O_peak1 = abs(np.max(out2[:,out_node]) - O_1)
    O_peak = abs(out2[:,out_node][-20:].min() - O_1)
    delta_I = abs(inpt[1] - inpt[0]) /inpt[0]
    precision = ((O_peak / O_1) / delta_I )**-1
    sensitivity = (O_peak1 / O_1) / delta_I
    return precision, sensitivity


