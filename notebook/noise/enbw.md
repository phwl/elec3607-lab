# Effective Noise Bandwidth for a Low Pass Filter

Consider an N-th order Butterworth filter with the frequency response:
$$H(j\omega)=\frac{1}{\sqrt(1+(\frac{s}{\omega_O})^{2N})}.$$
The  Equivalent Noise Bandwidth (ENBW) is the bandwidth of an equivalent rectangular (brick wall) filter that passes the same amount of noise power as the actual filter. It can be calculated using: 
$$\text{ENBW}=\int_{0}^{\infty} |H(j\omega)|^2 d\omega.$$
This notebook numerically computes the above for different $N$.


```python
import noiselib as nl
```


```python
# Show what is inside noiselib.py
from os import system
system("cat noiselib.py")
```

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
            
        




    0



    return bw


```python
from IPython.display import display, Markdown, Latex
out = f'''| Order | ENBW  |
|-------|-------|\n'''
for N in range(1, 5):
    out += f'| {N} | {nl.enbw(N):.4f} |\n'
display(Markdown(out))
```


| Order | ENBW  |
|-------|-------|
| 1 | 1.5708 |
| 2 | 1.1107 |
| 3 | 1.0472 |
| 4 | 1.0262 |




```python

```
