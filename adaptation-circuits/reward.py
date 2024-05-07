import scipy.signal

# todo: smooth the values instead of min/max
def compute_precision_sensitivity(inpt, out, out2, out_node=-1):
    """
    Precision: abs(((O_2 - O_1)/ O_1) / (I_2 - I_1)/I_1 )^-1
    Sensitivity: abs(((O_peak - O_1)/O_1) / (I_2 - I_1)/I_1)
    """
    # end of O_1 is steady state
    O_peak1 = out[:,out_node][-1]
    O_peak2 = out2[:,out_node][-20:].min()
    O_peak = out2[:,out_node].max()
    I_1 = inpt[0]
    I_2 = inpt[1]
    precision = abs(((O_peak2 - O_peak1)/ O_peak1) / ((I_2 - I_1)/I_1) )**-1
    sensitivity = abs(((O_peak - O_peak1)/O_peak1) / ((I_2 - I_1)/I_1))
    return precision, sensitivity


