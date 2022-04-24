"""
Measurements on correlation traces used in noisi
:copyright:
    noisi development team
:license:
    GNU Lesser General Public License, Version 3 and later
    (https://www.gnu.org/copyleft/lesser.html)
"""

import numpy as np
from scipy.signal import hilbert
from noisi.util.windows import get_window
from math import log
try:
    from noisi.util.plot import plot_window
except ImportError:
    pass


def square_envelope(correlation, window, g_speed, window_params):

    square_envelope = correlation.data**2 + \
        np.imag(hilbert(correlation.data))**2
    if window_params['plot']:
        plot_window(correlation, square_envelope, np.nan)

    return square_envelope


def envelope(correlation, window, g_speed, window_params):
    
    envelope = np.sqrt(correlation.data ** 2 + np.imag(hilbert(correlation.data)) ** 2)
    
    if window_params['plot']:
        plot_window(correlation, envelope, np.nan)
        
    return envelope



def windowed_waveform(correlation, window, g_speed, window_params):
    win = window[0]
    if window[2]:
        win_caus = (correlation.data * win)
        win_acaus = (correlation.data * win[::-1])
        msr = win_caus + win_acaus
    else:
        msr = win - win + np.nan
    return msr


def full_waveform(correlation, window, **kwargs):
    return(correlation.data)


def energy(correlation, window, g_speed, window_params):

    msr = [np.nan, np.nan]
    win = window[0]

    if window[2]:
        # causal
        E = np.trapz((correlation.data * win)**2)
        msr[0] = E
        if window_params['plot']:
            plot_window(correlation, win, E)

        # acausal
        win = win[::-1]
        E = np.trapz((correlation.data * win)**2)
        msr[1] = E
        if window_params['plot']:
            plot_window(correlation, win, E)

    return np.array(msr)


def log_en_ratio(correlation, window, g_speed, window_params):
    delta = correlation.stats.delta
    win = window[0]

    if window[2]:

        wl = window_params['waterlevel_perc']
        
        sig_c = correlation.data * win
        sig_a = correlation.data * win[::-1]
        E_plus = np.trapz(np.power(sig_c, 2)) * delta
        E_minus = np.trapz(np.power(sig_a, 2)) * delta
        #msr = log(E_plus / (E_minus + np.finfo(E_minus).tiny))

        #msr = log((E_plus/(E_minus+wl)))
        msr = log((E_plus/(E_minus+(wl*E_plus))))

        #if E_plus > E_minus:
        #    msr = log(E_plus/(E_minus + (wl*E_plus)))
        #else:
        #    msr = log((E_plus+(wl*E_minus))/(E_minus))
        
        if window_params['plot']:
            plot_window(correlation, win, msr)
    else:
        msr = np.nan
    return msr


def log_en_ratio_sqr(correlation, window, g_speed, window_params):
    delta = correlation.stats.delta
    win = window[0]

    if window[2]:

        wl = window_params['waterlevel_perc']
        
        sig_c = correlation.data * win
        sig_a = correlation.data * win[::-1]
        E_plus = np.trapz(np.power(sig_c, 2)) * delta
        E_minus = np.trapz(np.power(sig_a, 2)) * delta
        msr = log(E_plus / (E_minus + np.finfo(E_minus).tiny))**2

        #msr = log((E_plus/(E_minus+wl)))
        #msr = log((E_plus/(E_minus+(wl*E_plus))))

        #if E_plus > E_minus:
        #    msr = log(E_plus/(E_minus + (wl*E_plus)))
        #else:
        #    msr = log((E_plus+(wl*E_minus))/(E_minus))
        
        if window_params['plot']:
            plot_window(correlation, win, msr)
    else:
        msr = np.nan
    return msr

def log_en_ratio_cube(correlation, window, g_speed, window_params):
    delta = correlation.stats.delta
    win = window[0]

    if window[2]:

        wl = window_params['waterlevel_perc']
        
        sig_c = correlation.data * win
        sig_a = correlation.data * win[::-1]
        E_plus = np.trapz(np.power(sig_c, 2)) * delta
        E_minus = np.trapz(np.power(sig_a, 2)) * delta
        msr = log(E_plus / (E_minus + np.finfo(E_minus).tiny))**3

        #msr = log((E_plus/(E_minus+wl)))
        #msr = log((E_plus/(E_minus+(wl*E_plus))))

        #if E_plus > E_minus:
        #    msr = log(E_plus/(E_minus + (wl*E_plus)))
        #else:
        #    msr = log((E_plus+(wl*E_minus))/(E_minus))
        
        if window_params['plot']:
            plot_window(correlation, win, msr)
    else:
        msr = np.nan
    return msr



# This is a bit problematic cause here the misfit already needs
# to be returned (for practical reasons) -- ToDo think about
# how to organize this better
# def inst_mf(corr_obs, corr_syn, g_speed, window_params):
#     window = get_window(corr_obs.stats, g_speed, window_params)
#     win = window[0]

#     if window[2]:

#         sig1 = corr_obs.data * (win + win[::-1])
#         sig2 = corr_syn.data * (win + win[::-1])
#     # phase misfit .. try instantaneous phase
#     # hilbert gets the analytic signal (only the name is confusing)
#         a1 = hilbert(sig1)
#         a2 = hilbert(sig2)

#         cc = a1 * np.conjugate(a2)

#         boxc = np.clip((win + win[::-1]), 0, 1)
#         dphase = 0.5 * np.trapz(np.angle(cc * boxc)**2)

#         if window_params['plot']:
#             plot_window(corr_obs, win, dphase)
#     else:
#         dphase = np.nan

#     return dphase


def get_measure_func(mtype):

    if mtype == 'ln_energy_ratio':
        func = log_en_ratio
    elif mtype == 'ln_energy_ratio_sqr':
        func = log_en_ratio_sqr
    elif mtype == 'ln_energy_ratio_cube':
        func = log_en_ratio_cube
        
        
    elif mtype == 'energy_diff':
        func = energy
    elif mtype == 'square_envelope':
        func = square_envelope
    elif mtype == 'windowed_waveform':
        func = windowed_waveform
    elif mtype == 'full_waveform':
        func = full_waveform
    elif mtype == 'envelope':
        func = envelope   
    else:
        msg = 'Measurement functional %s not currently implemented.' % mtype
        raise ValueError(msg)
    return func
