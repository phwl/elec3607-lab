from scipy import signal, integrate
import matplotlib.pyplot as plt
import numpy as np
import math

# calculate the enbw for N
def enbw(N, f1=0.1, f2=1e6, doPlot=False):
    # a function that returns the power at angular frequency w1
    def H(b, a, w):
        wx, hx = signal.freqs(b, a, w)
        return abs(hx) ** 2.0

    # generate the filter
    b, a = signal.butter(N, 1, 'low', analog=True) 
    
    # compute the integral
    bw, err = integrate.quad(lambda w : H(b, a, w), 0, np.inf)  
    
    # optionally plot the result
    if doPlot:
        space=np.logspace(math.log10(f1), math.log10(f2), 5)
        w, h = signal.freqs(b, a, space)
        plt.semilogx(w, 20 * np.log10(abs(h)))
        plt.title('Butterworth filter frequency response')
        plt.xlabel('Frequency [rad/s]')
        plt.ylabel('Amplitude [dB]')
        plt.margins(0, 0.1)
        plt.grid(which='both', axis='both')
        plt.axvline(100, color='green') # cutoff frequency
        plt.show()
        
    return bw