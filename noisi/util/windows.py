"""
Window functions for measurements

:copyright:
    noisi development team
:license:
    GNU Lesser General Public License, Version 3 and later
    (https://www.gnu.org/copyleft/lesser.html)
"""


import numpy as np
from warnings import warn
from obspy.signal.filter import envelope


def my_centered(arr, newsize):

    if newsize % 2 == 0:
        raise ValueError('Newsize must be odd.')

    # pad with zeros, if newsize > len(arr)
    newarr = np.zeros(newsize)

    # get the center portion of a 1-dimensional array correctly
    n = len(arr)
    i0 = (n - newsize) // 2
    #print(i0)
    if i0 < 0:
        i0 = (newsize - n) // 2
        newarr[i0: i0 + n] += arr

    else:
        if n % 2 == 0:
            # This is arbitrary
            # because the array has no 'center' sample
            i0 += 1
        newarr[:] += arr[i0: i0 + newsize]
    return newarr


def window_checks(i0, i1, i2, i3, n, win_overlap, verbose=False):

    if n % 2 == 0:
        print('Correlation length must be 2*n+1, otherwise arbitrary middle \
sample. This correlation has length 2*n.')
        return(False)

    # Check if this will overlap with acausal side
    if i0 < n / 2 - 1 and win_overlap:
        msg = 'Windows of causal and acausal side overlap. Set win_overlap==False to \
skip these correlations.'
        warn(msg)
    elif i0 < n / 2 - 1 and not win_overlap:
        if verbose:
            print('Windows overlap, skipping...')
        return(False)

    # Out of bounds?
    if i0 < 0 or i1 > n:
        if verbose:
            print('\nNo windows found: Time series is too short.')
        return(False)
    elif i2 < 0 or i3 > n:
        if verbose:
            print('\nNo windows found: Noise window not covered by data.')
        return(False)

    return(True)


def get_window(stats, g_speed, params):
    """
    Obtain a window centered at distance * g_speed
    stats: obspy Stats object
    params: dictionary containing 'hw' halfwidth in seconds,
    'sep_noise' separation of noise window in fraction/multiples of halfwidth,
    'wtype' window type (None,boxcar, hanning),
    'overlap' may signal windows overlap (Boolean)
    """

    # Properties of trace
    s_0 = int((stats.npts - 1) / 2)
    dist = stats.sac.dist
    Fs = stats.sampling_rate
    n = stats.npts

    # Find indices for window bounds
    if 'hw_variable' in params and params['hw_variable'] is not None:
        
        g_speed_1 = g_speed - params['hw_variable']
        g_speed_2 = g_speed + params['hw_variable']

        ind_lo = int((dist / g_speed_2 - params['hw']) * Fs) + s_0
        ind_hi = int((dist / g_speed_1 + params['hw']) * Fs) + s_0        

        ind_lo_n = ind_hi + int(params['sep_noise'] * 20 * Fs)
        ind_hi_n = ind_lo_n + (ind_hi-ind_lo)

    else:    
        ind_lo = int((dist / g_speed - params['hw']) * Fs) + s_0
        ind_hi = ind_lo + int(2 * params['hw'] * Fs) + 1
    
        ind_lo_n = ind_hi + int(params['sep_noise'] * params['hw'] * Fs)
        ind_hi_n = ind_lo_n + int(2 * params['hw'] * Fs) + 1

    # Checks..overlap, out of bounds
    scs = window_checks(ind_lo, ind_hi, ind_lo_n,
                        ind_hi_n, n, params['win_overlap'])

    if scs:
        # Fill signal window
        win_signal = window(params['wtype'], n, ind_lo, ind_hi)
        # Fill noise window
        win_noise = window(params['wtype'], n, ind_lo_n, ind_hi_n)

        return win_signal, win_noise, scs

    else:
        return np.zeros(n), np.zeros(n), scs


def get_window_peak_envelope(tr, minperiod, maxperiod, params):
    n = tr.stats.npts
    Fs = tr.stats.sampling_rate

    # window is computed on the causal branch and mirrored to the acausal
    branch_npts = int((tr.stats.npts - 1) / 2)
    maxlag = branch_npts * tr.stats.delta
    caus_branch = tr.slice(starttime=(tr.stats.starttime + maxlag),
                           endtime=tr.stats.endtime)

    # window is centered at maximum of envelope
    env = caus_branch.data ** 2.0
    idx = np.argmax(env)

    # window duration is 5 times central period
    T = (minperiod + maxperiod) / 2.
    half_win = 2.5 * T

    Tn = T // caus_branch.stats.delta
    half_win_n = int(2.5 * Tn)

    # get signal window limits
    ind_lo = np.maximum(idx - half_win_n + branch_npts, branch_npts + 1)
    ind_hi = idx + half_win_n + branch_npts

    # get noise window limits
    ind_lo_n = ind_hi + int(params['sep_noise'] * half_win * Fs)
    ind_hi_n = ind_lo_n + int(2 * half_win * Fs) + 1

    # Checks..overlap, out of bounds
    scs = window_checks(ind_lo, ind_hi, ind_lo_n,
                        ind_hi_n, n, params['win_overlap'])

    if scs:
        # Fill signal window
        win_signal = window(params['wtype'], n, ind_lo, ind_hi)
        # Fill noise window
        win_noise = window(params['wtype'], n, ind_lo_n, ind_hi_n)

        return win_signal, win_noise, scs

    else:
        return np.zeros(n), np.zeros(n), scs


def window(wtype, n, i0, i1):
    win = np.zeros(n)
    if wtype is None:
        win += 1.
    elif wtype == 'boxcar':
        win[i0:i1] += 1
    elif wtype == 'hann':
        win[i0: i1] += np.hanning(i1 - i0)
    else:
        msg = ('Window type \'%s\' is not implemented\nImplemented types:\
 boxcar, hann' % wtype)
        raise NotImplementedError(msg)
    return win


def snratio(correlation, g_speed, window_params):

    window = get_window(correlation.stats, g_speed, window_params)

    if not window_params['causal_side']:
        win_s = window[0][::-1]
        win_n = window[1][::-1]
    else:
        win_s = window[0]
        win_n = window[1]

    if window[2]:
        signl = np.sum((win_s * correlation.data) ** 2)
        noise = np.sum((win_n * correlation.data) ** 2)
        snr = signl / (noise + np.finfo(noise).tiny)
    else:
        snr = np.nan
    return snr
