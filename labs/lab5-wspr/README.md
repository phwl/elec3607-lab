# WSPR Decoder

This lab involves modifying a WSPR-decoder to use pulseaudio. Once this is done, the WSPR-decoder can not only access local audio peripherals under Linux, it can also use network-based audio souces. 

After completing this lab, you should understand how to capture i/q samples from your radio, convert them to the right format for the k9an-wsprd program, and decode WSPR. You will have developed a working WSPR decoder, interfaced to pulseaudio.

First cd to your ```elec3607-lab``` directory and type ```git pull``` to ensure you have the latest version of the lab. 

## Question 1 -  Pulseaudio (10\%)

You can check that pulseaudio is working with ```pactl```:
```
petalinux-8GB:~$ pactl info
Server String: /run/user/1000/pulse/native
Library Protocol Version: 35
Server Protocol Version: 35
Is Local: yes
Client Index: 5
Tile Size: 65472
User Name: petalinux
Host Name: petalinux-8GB
Server Name: pulseaudio
Server Version: 16.1
Default Sample Specification: s16le 2ch 44100Hz
Default Channel Map: front-left,front-right
Default Sink: alsa_output.usb-Plugable_Plugable_USB_Audio_Device_000000000000-00.analog-stereo
Default Source: alsa_input.usb-Plugable_Plugable_USB_Audio_Device_000000000000-00.analog-stereo
Cookie: d24c:3937
```
Note that the above tells us that the Default Sink and Source are set to the USB sound card.

Now let's list the sources and sinks:
```bash
petalinux-8GB:~$ pactl list short sources
0       alsa_output.usb-Plugable_Plugable_USB_Audio_Device_000000000000-00.analog-stereo.monitor        module-alsa-card.c      s16le 2ch 48000Hz       SUSPENDED
1       alsa_input.usb-Plugable_Plugable_USB_Audio_Device_000000000000-00.analog-stereo module-alsa-card.c      s16le 2ch 48000Hz       SUSPENDED
2       alsa_output.platform-xlnx_snd_card.1.auto.stereo-fallback.monitor       module-alsa-card.c      s24-32le 2ch 44100Hz    SUSPENDED
petalinux-8GB:~$ pactl list short sinks
0       alsa_output.usb-Plugable_Plugable_USB_Audio_Device_000000000000-00.analog-stereo        module-alsa-card.c      s16le 2ch 48000Hz       SUSPENDED
1       alsa_output.platform-xlnx_snd_card.1.auto.stereo-fallback       module-alsa-card.c      s24-32le 2ch 44100Hz    SUSPENDED
```
Do the following and explain the purpose of these commands which utilise
a very powerful feature of pulseaudio.
```bash
petalinux-8GB:~$ pactl set-default-sink 0
petalinux-8GB:~$ pactl set-default-source 0
petalinux-8GB:~$ pactl info
Server String: /run/user/1000/pulse/native
Library Protocol Version: 35
Server Protocol Version: 35
Is Local: yes
Client Index: 11
Tile Size: 65472
User Name: petalinux
Host Name: petalinux-8GB
Server Name: pulseaudio
Server Version: 16.1
Default Sample Specification: s16le 2ch 44100Hz
Default Channel Map: front-left,front-right
Default Sink: alsa_output.usb-Plugable_Plugable_USB_Audio_Device_000000000000-00.analog-stereo
Default Source: alsa_output.usb-Plugable_Plugable_USB_Audio_Device_000000000000-00.analog-stereo.monitor
Cookie: d24c:3937
```

## Question 2 - Compiling wsprd (10\%)
A brief description of WSPR is available at
<https://www.arrl.org/files/file/History/History%20of%20QST%20Volume%201%20-%20Technology/QS11-2010-Taylor.pdf>.
```wsprcan/k9an-wsprd``` is a program that decodes baseband wspr files (i.e. wspr files that have been downconverted). You can compile with the following ```make``` command 

```bash
petalinux-8GB:~/elec3607-lab-main/labs/lab5-wspr$ make wspr
(cd wsprcan; make)
make[1]: Entering directory '/home/petalinux/elec3607-lab-main/labs/lab5-wspr/wsprcan'
make[1]: Nothing to be done for 'all'.
make[1]: Leaving directory '/home/petalinux/elec3607-lab-main/labs/lab5-wspr/wsprcan'
sox data/iq-16b.wav -c 1 -t wav -r 12000 -b 16 mono.wav
wsprcan/k9an-wsprd mono.wav
mono  -1 -1.3   0.001437 -1  VK2RG QF56 30 
mono -19 -1.0   0.001455 -1  VK3GOD QF23 23 
mono -20 -1.1   0.001478 -1  VK4YEH QG62 37 
<DecodeFinished>
rm mono.wav
```

In your lab book, explain what is being done by this program. Also explain the role of the ```sox``` command.

## Question 3 -  Compiling ```parec``` (10\%)
In the parecfile directory, ```parecfile.c``` is a program that records some data via pulseaudio, and then writes it to stdout. As its name suggests, the pulseaudio simple interface is very simple and its documentation is available [here](https://www.freedesktop.org/wiki/Software/PulseAudio/Documentation/).

```bash
petalinux-8GB:~/elec3607-lab-main/labs/lab5-wspr$ cd parecfile
petalinux-8GB:~/elec3607-lab-main/labs/lab5-wspr/parecfile$ make
gcc -Wall -g  -c parecfile.c  -o parecfile.o
gcc -Wall -g  -o parecfile parecfile.o  -lpulse-simple -lpulse
```
Study what this program does as you will need it for the following question.

## Question 4 - Modifying wsprcan/wsprd.c (60\%)


Using the ```parecfile/parecfile.c``` code as an example,
modify ```wsprcan/wsprd.c``` so that it takes input from pulseaudio instead of the file (do this in a copy of the wsprcan directory called pa-wsprcan that can be made using ```cp -r wsprcan pa-wsprcan```). 

We suggest you do this by:
 1. creating the following function in pa-wsprcan/parec.c (this decouples the pulseaudio stuff from wspr)
```C
	int parec(char *fnamep[], short *pabuf, int npoints)
```
 2. Think about how to set the format, rate and channels in  
```C
	static const pa_sample_spec ss
```
 3. Call ```parec()``` from ```readwavfile()``` in ```wsprd.c```.
 4. Change the command line handling in ```wsprd.c``` (as there is no wavfile) 
 5. Think carefully how to test it (don’t just hope it works first go as it won’t)!
 6. Don’t rush - it takes twice as long if you do!

Demonstrate that your program works by playing a file in the background and decoding it with your modified program. The supplied script, wspr-test does this for you:
```bash
petalinux-8GB:~/elec3607-lab-main/labs/lab5-wspr$ cat wspr-test
#!/bin/bash

# this plays an audio file in the background and runs pa-wsprcan
echo -n "running paplay at "
date
paplay data/iq-16b.wav &
./pa-wsprcan/k9an-wsprd 
date
petalinux-8GB:~/elec3607-lab-main/labs/lab5-wspr$ chmod +x wspr-test
petalinux-8GB:~/elec3607-lab-main/labs/lab5-wspr$ ./wspr-test
running paplay at Thu Apr  2 05:48:30 UTC 2026
mode  -1 -1.4   0.001437 -1  VK2RG QF56 30 
mode -19 -1.2   0.001455 -1  VK3GOD QF23 23 
mode -20 -1.3   0.001478 -1  VK4YEH QG62 37 
<DecodeFinished>
Wavfilename based on current time: data/wf-1775109024.wav
Unique Decodes: 3
Thu Apr  2 05:50:26 UTC 2026
```
## Question 5 - wsprwait (10\%)
Study the bash script wsprwait. In your lab book, provide an annotated listing of what this does and why it might be useful in this project.
