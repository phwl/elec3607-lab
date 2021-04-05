The following files and directories make a wspr decoder environment.

Makefile	- builds everything
data		- contains a wav file with inphase/quadrature samples from an SDR
qemu		- place the qemu files here
rec			- an alsa sound card capture program to be modified
wsprcan 	- a wspr decoder

If you type ```make wspr```, you should see the following output:
```
(cd wsprcan; make)
make[1]: Nothing to be done for `all'.
sox data/iq-16b.wav -c 1 -t wav -r 12000 -b 16 mono.wav
wsprcan/k9an-wsprd mono.wav
mono  -1 -1.3   0.001437 -1  VK2RG QF56 30 
mono -19 -1.0   0.001455 -1  VK3GOD QF23 23 
mono -20 -1.1   0.001478 -1  VK4YEH QG62 37 
<DecodeFinished>
rm mono.wav
```
