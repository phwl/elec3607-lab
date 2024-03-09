# Lab 3 - Amplifier and Tayloe Detector

This lab involves simulation and testing of an RF amplifier and  Tayloe detector.

## Part A - RF Amplifier 
### Question 1 - RF Amplifier Initial Simulation (30%)

The LTspice simulator is available from https://www.analog.com/en/design-center/design-tools-and-calculators/ltspice-simulator.html for both Windows and MacOS. Download and install the binary directly on your machine. 

[This schematic](sdr-2022.pdf) shows the RF amplifier with input RFIN and output RFOUT. Draw an LTspice schematic of the circuit using the ideal single-pole operational amplifier model in place of the THS4304. Make a Bode plot of the frequency response, using ```.ac dec 20 1 10MEG``` (this specifies an AC analysis with 20 points per decade from 1 Hz to 10 MHz). Find the datasheet for the [THS4304](https://www.ti.com/product/THS4304). What are typical values for the open loop gain and the gain bandwidth product? Change your opamp model to use these values in place of the default ones for Aol and GBW. How does the frequency response of your amplifier change? Explain the reason that this happens. Also verify that the gain of the amplifier in the passband region is the correct value.

### Question 2 - Measurement (70%)
Now measure the frequency response of the amplifier on your PCB using a waveform generator and oscilloscope. What is the small-signal gain for a 1 mV peak-to-peak sine wave input at 7 MHz? Is it the expected value?

## Part B - Tayloe Detector 
### Question 1 - Tayloe Detector simulation (30%)

The Tayloe Detector simulation explained in the lectures is available in this directory as ```tayloe-ideal.asc```. 
Referring to the documentation, explain the purpose of the LTspice directive:
```
.step param FRQ 1005k 1007k 1k
```
in the simulation.

Run the simulation and display the voltage of nodes I_out and Q_out in a plot. Place these plots in your lab book and explain how they relate to the input signal created by V1. Also try View->FFT to obtain a frequency domain plot of V(I_out) and the input, V(n005) as shown below.

![](mixersim.png)

The initial simulation provided is for a simulation at 1 MHz. WSPR transmits a 4-FSK message. Change the simulation so fc=7.0386 MHz and FRQ will step from 7.04010 MHz over the exact range of values of a legal WSPR transmission (i.e. 4-FSK with a 1.4648 Hz tone separation). Make an fft plot of I_out and n005 similar to the one above. Explain the changes you made in your lab book. Note that I have had issues with LTSpice on the M1 Mac crashing but found that I could get it to work by changing the ```.step param FRQ``` command.

### Question 2 - Tayloe Detector (70%)
Now measure the mixer of the Tayloe detector on your PCB using a waveform generator and oscilloscope and confirm that it can perform downconversion. Describe the expected behaviour in your lab book and include screen shots to demonstrate that it was achieved. 

