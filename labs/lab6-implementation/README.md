# WSPR Implementation

## Introduction

This lab involves integrating the components from all the previous labs.  After completing this lab, you should have a working WSPR decoder.

## Part 1 - Carrier Frequency Adjustment (20%)
Using a frequency counter, accurately record your carrier frequency. Note that to be accurate to say 1 Hz, you will need approximately 1/7 parts per million accuracy (which is beyond the specification of the crystal used). Thus you
will need to trim the frequency of the crystal oscillator on the Si5351 so it is very close to the expected frequency. Do this by slightly changing the frequency that you select on the Si5351 to compensate for the difference and record your new carrier frequency. Explain the process that you used to do this.

## Part 2 - Verification of the Analog Chain (20%)
In the lab, we will provide a strong WSPR beacon for you to receive. Create a receiving antenna for your WSPR decoder and verify that you can receive a signal at the correct WSPR frequency. Recall that WSPR uses a carrier frequency of 7.0386 MHz with a bandwidth of 200 Hz. The upper and lower frequencies are 7.0400-7.0402 MHz so we expect the downconverted signal to be centered around 1.5 kHz. Using a oscilloscope, verify that the signal can be seen at the audio output of the ELEC3607SDR printed circuit board. 

## Part 3 - Integrating all parts of the WSPR Receiver (40%)
Now integrate your WSPR decoding software with the hardware. You will need to solder the audio jack to your board. 

Think about how you should use ```pactl set-default-source``` to set it to the USB sound card microphone. Then use the WSPR decoder that you have developed to decode WSPR packets. Note that transmissions start every 2 minutes and you need to have your Linux system clock set properly and use ```wsprwait``` for synchronisation.

We will be running a wspr beacon in the lab and a correct output will look something like this:
```
elec3607@raspberrypi:~/elec3607-lab/labs/lab4-wspr $ ./wsprwait
Executing wspr_decode Tue 15 Apr 15:38:00 AEST 2025
mode -24 -1.1   0.001473 -1  VX2TXH QF56  7 
<DecodeFinished,data/wf-1744695594.wav,1>
```

## Part 4 - Band Pass Filter (Optional 20%)

This part of the lab is optional and should be only be attempted if you
can finish the other two parts before the deadline. Using [these
toroid ferrite cores](https://au.element14.com/fair-rite/5961001101/ferrite-core-toroid-61/dp/1781375) and based on [this similar design](BPF-40m.pdf] (that design uses a different toroid core), build and test the band pass filter (BPF) circuit
on the ELEC3608SDR board. Create your own methodology to test the BPF and test whether or note it improves the ability of your WSPR receiver in part 2 to decoder WSPR signals. Explain why the answer to this question will be dependent on the prevailing radio frequency environment.
