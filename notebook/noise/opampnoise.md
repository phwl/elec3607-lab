# Noise Calculation

Notebook to make calculations in <https://www.renesas.com/ja/document/apn/r13an0010-noise-calculations-op-amp-circuits>


```python
import math
```


```python
# resistors in parallel
def rparallel(r1, r2): return (1.0 / (1.0/r1 + 1.0/r2))

# Thermal noise contribution
def tnoise(b, r): return math.sqrt(4.0 * k * T * b * r)
    
# 1/f noise contribution
def fnoise(f, n, fH, fL): return math.sqrt(f * math.log(fH / fL) + n * fH - fL)

# this is the standard RMS to peak-to-peak conversion of 6.6 sigma (pg 4 of Art Kay, "Operational Amplifier Noise")
def rmspp(v): return (v * 6.6)

# volts to dbV
def dbv(v): return (20.0 * math.log10(v))

T = 298       # temperature in K
k = 1.38e-23  # Boltzmann's constant

# For conversion from -dB bandwidth to white noise equivalent bandwidth NEB
narray = [0.0, 1.57, 1.22, 1.16, 1.13, 1.12]
order = 1        # filter order
n = narray[order]
print(f"n={n}")
```

    n=1.57



```python
# Do the noise analysis
def noisecalc(desc, GBW, fxe, fxi, enf, inf, enw, inw, R1, R2, R3, VOpp, Gn, Gs, fL, fH, verbose=False):
    print(f"*** {desc}\n")

    # Bandwidth Limits
    fce = fxe * ((enf / enw) ** 2.0 - 1.)
    fci = fxi * ((inf / inw)** 2.0 - 1.)
    NEB = n * fH - fL
    
    Rp = rparallel(R1, R2)
    ERp = tnoise(NEB, Rp)
    ER3 = tnoise(NEB, R3)
    
    Enn = Rp * inw * fnoise(fci, n, fH, fL)
    Enp = R3 * inw * fnoise(fci, n, fH, fL)
    
    # opamp noise voltage
    En = enw * fnoise(fce, n, fH, fL)

    # total noise
    Eni = math.sqrt(ERp * ERp + ER3 * ER3 + Enn * Enn + Enp * Enp + En * En)
    Eno = Eni * Gn
    Enipp = rmspp(Eni)   
    SNR = 20 * math.log10(VOpp / (2.0 * math.sqrt(2.0) * Eno))
    
    # simplified formula
    SEni = math.sqrt(ERp * ERp + ER3 * ER3 + En * En)
    err = (Eni - SEni) / Eni

    # print outputs
    if (verbose):
        print("-- Parameters")
        print(f"R1={R1:.3e} (R1)")
        print(f"R2={R2:.3e} (R2)")
        print(f"R3={R3:.3e} (R3)")
        print(f"Rp={Rp:.3e} (R1 || R2)")
        print(f"Gn={Gn:.3e} (noise gain)")
        print(f"Gs={Gs:.3e} (signal gain)")
        print(f"NEB={NEB:.3e} (bandwidth)")
        print(f"fce={fce:.3e} (voltage 1/f noise corner freq)")
        print(f"fci={fci:.3e} (current 1/f noise corner freq)")
    
        print("\n-- Components")
        print(f"ERp={ERp:.3e} (thermal noise negative terminal resistors)")
        print(f"ER3={ER3:.3e} (thermal noise positive terminal resistors)")
        print(f"Enn={Enn:.3e} (opamp current negative terminal)")
        print(f"Enp={Enp:.3e} (opamp current positive terminal)")
        print(f"En={En:.3e} (opamp input noise)")

    print(f"\n--Solution {desc}")
    # print(f"SEni={SEni:.3e}, err = {100. * err}%")
    print(f"Enipp={Enipp*1e6:.1f} uV {dbv(Enipp):.1f} dBV (Vpp in uV)")
    print(f"Eni={Eni:.3e} {dbv(Eni):.1f} dBV (noise at input)")
    print(f"Eno={Eno:.3e} {dbv(Eno):.1f} dBV (noise at output)")
    print(f"SNR={SNR:.3f} dB")
```


```python
desc = "Example in https://www.renesas.com/ja/document/apn/r13an0010-noise-calculations-op-amp-circuits"
# this reproduces the example in the app note
GBW = 5e6      # gain bandwith MHz
fxe = 10.      # frequency for specifying 1/f noise voltage
fxi = 1.       # frequency for specifying 1/f noise current
enf = 30e-9    # 1/f noise at 1 Hz
inf = 8e-12    # 1/f noise at 1 Hz
enw = 15e-9    # thermal noise voltage V/sqrt(Hz)
inw = 0.35e-12 # thermal noise current A/sqrt(Hz)

# Opamp circuit parameters
R1 = 1.01e3
R2 = 101e3
R3 = 1e3
Gn = 1 + R2 / R1    # noise gain
Gs = -(R2 / R1)     # signal gain

# frequencies
fL = 0.1       # -3dB low bandwidth Hz
fH = GBW / Gn  # -3dB upper bandwidth

VOpp = 4.6    # output signal range

noisecalc(desc, GBW, fxe, fxi, enf, inf, enw, inw, R1, R2, R3, VOpp, Gn, Gs, fL, fH)
```

    *** Example in https://www.renesas.com/ja/document/apn/r13an0010-noise-calculations-op-amp-circuits
    
    
    --Solution Example in https://www.renesas.com/ja/document/apn/r13an0010-noise-calculations-op-amp-circuits
    Enipp=29.6 uV -90.6 dBV (Vpp in uV)
    Eni=4.489e-06 -107.0 dBV (noise at input)
    Eno=4.534e-04 -66.9 dBV (noise at output)
    SNR=71.094 dB


We can calculate the 1/f noise voltage and current corner frequencies using:
$$f_{ce}=f_{xe} ((\frac{e_{nf(fe)}}{e_{nw}})^2-1)$$
$$f_{ci}=f_{xi} ((\frac{i_{nf(fi)}}{i_{nw}})^2-1)$$

The white noise equivalent bandwidth 

For thermal noise
$$E_R = \sqrt(4kTR(nf_H - f_L))$$

For opamp current
$$E_N = R i_{nw} \sqrt(f_{ci} \log(\frac{f_H}{f_L}+nf_H - f_L))$$


```python
desc = "RF amplifier in ELEC3607"
# ELEC3607
GBW = 900e6      # gain bandwith MHz
fxe = 1.      # frequency for specifying 1/f noise voltage
fxi = 1.       # frequency for specifying 1/f noise current
enf = 90e-9    # 1/f noise at 1 Hz
inf = 200e-12    # 1/f noise at 1 Hz
enw = 2.4e-9    # thermal noise voltage V/sqrt(Hz)
inw = 2.1e-12 # thermal noise current A/sqrt(Hz)

# Opamp circuit parameters
R1 = 47.
R2 = 220.
R3 = rparallel(50., 470.0 / 2.0)
VOpp = 3.3    # output signal range
Gn = 1 + R2 / R1    # noise gain
Gs = Gn     # signal gain

# frequencies
fL = 80e3       # -3dB low bandwidth Hz
fH = 110e6  # -3dB upper bandwidth

noisecalc(desc, GBW, fxe, fxi, enf, inf, enw, inw, R1, R2, R3, VOpp, Gn, Gs, fL, fH, verbose=True)
```

    *** RF amplifier in ELEC3607
    
    -- Parameters
    R1=4.700e+01 (R1)
    R2=2.200e+02 (R2)
    R3=4.123e+01 (R3)
    Rp=3.873e+01 (R1 || R2)
    Gn=5.681e+00 (noise gain)
    Gs=5.681e+00 (signal gain)
    NEB=1.726e+08 (bandwidth)
    fce=1.405e+03 (voltage 1/f noise corner freq)
    fci=9.069e+03 (current 1/f noise corner freq)
    
    -- Components
    ERp=1.049e-05 (thermal noise negative terminal resistors)
    ER3=1.082e-05 (thermal noise positive terminal resistors)
    Enn=1.069e-06 (opamp current negative terminal)
    Enp=1.138e-06 (opamp current positive terminal)
    En=3.153e-05 (opamp input noise)
    
    --Solution RF amplifier in ELEC3607
    Enipp=230.9 uV -72.7 dBV (Vpp in uV)
    Eni=3.498e-05 -89.1 dBV (noise at input)
    Eno=1.987e-04 -74.0 dBV (noise at output)
    SNR=75.374 dB



```python
desc = "RF amplifier in ELEC3607 with BPF (3.3V)"
# ELEC3607
GBW = 900e6      # gain bandwith MHz
fxe = 1.      # frequency for specifying 1/f noise voltage
fxi = 1.       # frequency for specifying 1/f noise current
enf = 90e-9    # 1/f noise at 1 Hz
inf = 200e-12    # 1/f noise at 1 Hz
enw = 2.4e-9    # thermal noise voltage V/sqrt(Hz)
inw = 2.1e-12 # thermal noise current A/sqrt(Hz)

# Opamp circuit parameters
R1 = 47.
R2 = 220.
R3 = rparallel(50., 470.0 / 2.0)
VOpp = 3.3    # output signal range
Gn = 1 + R2 / R1    # noise gain
Gs = Gn     # signal gain

# frequencies
fL = 6.8e6       # -3dB low bandwidth Hz
fH = 7.3e6  # -3dB upper bandwidth

noisecalc(desc, GBW, fxe, fxi, enf, inf, enw, inw, R1, R2, R3, VOpp, Gn, Gs, fL, fH)
```

    *** RF amplifier in ELEC3607 with BPF (3.3V)
    
    
    --Solution RF amplifier in ELEC3607 with BPF (3.3V)
    Enipp=37.9 uV -88.4 dBV (Vpp in uV)
    Eni=5.748e-06 -104.8 dBV (noise at input)
    Eno=3.266e-05 -89.7 dBV (noise at output)
    SNR=91.060 dB



```python

```
