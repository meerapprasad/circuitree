import numpy as np
from numpy.fft import fft, ifft
from scipy.signal import find_peaks


# def autocorrelation(data):
#     """Compute the autocorrelation of a signal."""
#     n = len(data)
#     data -= np.mean(data)
#     autocorr_f = fft(data, n=2 * n)
#     result = ifft(autocorr_f * np.conjugate(autocorr_f))[:n].real
#     result /= result[0]  # Normalize
#     return result


def autocorr(x):
    x = x - x.mean(axis=0)
    result = np.correlate(x, x, mode='full')
    return result[result.size//2:]

def sustained_oscillation(data):
    """Classify if there are sustained oscillations based on autocorrelation."""
    # Compute the autocorrelation
    acorr = np.apply_along_axis(autocorr, 0, data)
    if acorr.min() < -.04:
        return True
    else:
        return False
    # Detect peaks in the autocorrelation to identify oscillatory patterns
    # peaks = np.apply_along_axis(find_peaks, acorr, axis=1)  # Detect peaks with positive values

    # # If there are fewer than 3 peaks, it's unlikely to be oscillatory
    # if len(peaks) < 3:
    #     return False  # Not enough peaks to classify sustained oscillations
    #
    # # Analyze the decay between peaks
    # peak_values = acorr[peaks]
    # decay_rate = np.diff(np.log(np.abs(peak_values)))
    #
    # # Determine if decay rates suggest sustained oscillations
    # is_sustained = np.all(decay_rate > -0.1)  # Adjust threshold as needed
    #
    # return is_sustained

# def sustained_oscillation(data):
#     """Classify the oscillation type based on autocorrelation."""
#     # acorr = autocorrelation(data)
#     # n = len(acorr)
#     # todo: do I need to mean center?
#     acorr = np.apply_along_axis(autocorr, 0, data)
#     n = acorr.shape[0]
#     # Check for oscillatory behavior by detecting periodic peaks
#     # peaks = np.diff(np.sign(np.diff(acorr)))  # Second derivative (change of slope)
#     # todo: this is a problem
#     # peak_indices = np.where(peaks == -2)[0] + 1  # +1 to correct the index shift caused by diff
#
#     if len(peak_indices) < 1:
#         return False  # Not enough peaks to determine oscillatory behavior
#
#     # Examine decay of peaks
#     peak_values = acorr[peak_indices]
#     # todo: detect if the peak is flat?
#     if len(peak_values) < 1:
#         return False  # Not enough peak data to analyze
#
#     decay_rate = np.diff(np.log(np.abs(peak_values)))  # Log to linearize exponential decay
#
#     # Threshold values to determine the type of damping
#     is_oscillating = np.any(decay_rate > -0.1)
#     mean_decay = np.mean(decay_rate)
#
#     # Classify based on decay rate and peak persistence
#     if is_oscillating:
#         return True  # Sustained oscillations
#     else:
#         return False
#     # elif mean_decay > -0.5 and mean_decay < 0:
#     #     return 'Underdamped'  # Underdamped oscillations
#     # elif mean_decay < -1.0:
#     #     return 'Overdamped'  # Overdamped oscillations
#     # elif mean_decay >= -0.5 and mean_decay <= -0.1:
#     #     return 'Critically Damped'  # Critically Damped oscillations
import matplotlib.pyplot as plt

# todo: add checks if there is no oscillation
def damped_oscillation(out, out2, out_node=-1):
    """Filter out damped oscillations from a dataset."""
    steady_state = out[:, out_node][-1]
    peak_idx = find_peaks(out2[:, out_node])[0]
    if len(peak_idx) < 2:
        return True  # Not enough peaks to determine oscillatory behavior
    else:
        peak_values = out2[:, out_node][peak_idx]
        # todo: check if the first peak is 2x the second peak
        trough_1 = np.minimum(out2[:,out_node][peak_idx[0]], out2[:,out_node][peak_idx[0]])
        O_peak1 = peak_values[0] - steady_state
        O_peak2 = np.abs(trough_1 - steady_state)
        return O_peak1 > 2 * O_peak2  # continue if criteria is passed

