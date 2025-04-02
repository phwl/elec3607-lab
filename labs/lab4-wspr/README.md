# WSPR Decoder

This lab involves modifying a WSPR-decoder to use pulseaudio on a RPi4. Once this is done, the WSPR-decoder can not only access local audio peripherals on the RPi, it can also use network-based audio souces. 

After completing this lab, you should understand how to capture i/q samples from your radio, convert them to the right format for the k9an-wsprd program, and decode WSPR. You will have a working WSPR decoder, interfaced to pulseaudio.

First cd to your ```elec3607-lab``` directory and type ```git pull``` to ensure you have the latest version of the lab. Also, do a ```sudo apt update``` to make sure you have the latest Debian distribution files```.

## Question 1 -  Pipewire (10\%)

In this question, you will explore some of the features of [Pipewire](https://docs.pipewire.org/).  Plug in your USB sound card. It should appear if you type the following:
```bash
elec3607@raspberrypi:~ $ wpctl status
PipeWire 'pipewire-0' [1.2.4, elec3607@raspberrypi, cookie:1387283956]
 └─ Clients:
        33. pipewire                            [1.2.4, elec3607@raspberrypi, pid:771]
        35. WirePlumber                         [1.2.4, elec3607@raspberrypi, pid:770]
        36. WirePlumber [export]                [1.2.4, elec3607@raspberrypi, pid:770]
        85. xdg-desktop-portal-wlr              [1.2.4, elec3607@raspberrypi, pid:1112]
        86. xdg-desktop-portal                  [1.2.4, elec3607@raspberrypi, pid:1066]
        87. unknown                             [1.2.4, elec3607@raspberrypi, pid:989]
        89. pipewire                            [1.2.4, elec3607@raspberrypi, pid:771]
        92. wpctl                               [1.2.4, elec3607@raspberrypi, pid:3937]

Audio
 ├─ Devices:
 │      56. Plugable USB Audio Device           [alsa]
 │      57. Built-in Audio                      [alsa]
 │      58. Built-in Audio                      [alsa]
 │      59. Built-in Audio                      [alsa]
 │  
 ├─ Sinks:
 │      34. Built-in Audio Digital Stereo (HDMI) [vol: 0.40]
 │  *   72. Plugable USB Audio Device Analog Stereo [vol: 0.40]
 │      74. Built-in Audio Stereo               [vol: 0.40]
 │      90. MySink Audio/Sink sink              [vol: 1.00]
 │  
 ├─ Sink endpoints:
 │  
 ├─ Sources:
 │  *   73. Plugable USB Audio Device Analog Stereo [vol: 1.00]
 │  
 ├─ Source endpoints:
 │  
 └─ Streams:

Video
 ├─ Devices:
 │      42. rpivid                              [v4l2]
 │      43. bcm2835-codec-decode                [v4l2]
 │      44. bcm2835-codec-encode                [v4l2]
 │      45. bcm2835-codec-isp                   [v4l2]
 │      46. bcm2835-codec-image_fx              [v4l2]
 │      47. bcm2835-codec-encode_image          [v4l2]
 │      48. bcm2835-isp                         [v4l2]
 │      49. bcm2835-isp                         [v4l2]
 │      50. bcm2835-isp                         [v4l2]
 │      51. bcm2835-isp                         [v4l2]
 │      52. bcm2835-isp                         [v4l2]
 │      53. bcm2835-isp                         [v4l2]
 │      54. bcm2835-isp                         [v4l2]
 │      55. bcm2835-isp                         [v4l2]
 │  
 ├─ Sinks:
 │  
 ├─ Sink endpoints:
 │  
 ├─ Sources:
 │  *   60. bcm2835-isp (V4L2)                 
 │      62. bcm2835-isp (V4L2)                 
 │      64. bcm2835-isp (V4L2)                 
 │      66. bcm2835-isp (V4L2)                 
 │  
 ├─ Source endpoints:
 │  
 └─ Streams:

Settings
 └─ Default Configured Node Names:
```

Pipewire supports multiple interfaces (including pulseaudio which is the one we will be using). The [wiki](https://gitlab.freedesktop.org/pipewire/pipewire/-/wikis/Config-PulseAudio) explains the commands that are available.
You can also check that pulseaudio is working with ```pactl```:
```
elec3607@raspberrypi:~ $ pactl info
Server String: /run/user/1000/pulse/native
Library Protocol Version: 35
Server Protocol Version: 35
Is Local: yes
Client Index: 101
Tile Size: 65472
User Name: elec3607
Host Name: raspberrypi
Server Name: PulseAudio (on PipeWire 1.2.4)
Server Version: 15.0.0
Default Sample Specification: float32le 2ch 48000Hz
Default Channel Map: front-left,front-right
Default Sink: alsa_output.usb-Plugable_Plugable_USB_Audio_Device_000000000000-00.analog-stereo
Default Source: alsa_input.usb-Plugable_Plugable_USB_Audio_Device_000000000000-00.analog-stereo
Cookie: 52b0:45f4
```

We are going to create a virtual audio sink which is mono and 12000 samples a second. This is done using:
```bash
elec3607@raspberrypi:~ $ pactl load-module module-null-sink sink_name    =MySink format=s16le channels=1 rate=12000
```

Now let's list the sources and sinks:
```bash
elec3607@raspberrypi:~/lab4-wspr $ pactl list short sources
72	alsa_output.usb-Plugable_Plugable_USB_Audio_Device_000000000000-00.analog-stereo.monitor	PipeWire	s16le 2ch 48000Hz	SUSPENDED
73	alsa_input.usb-Plugable_Plugable_USB_Audio_Device_000000000000-00.analog-stereo	PipeWire	s16le 2ch 48000Hz	SUSPENDED
74	alsa_output.platform-bcm2835_audio.stereo-fallback.monitor	PipeWirs16le 2ch 48000Hz	SUSPENDED
75	alsa_output.platform-fef00700.hdmi.hdmi-stereo.monitor	PipeWire	s32le 2ch 48000Hz	SUSPENDED
96	MySink.monitor	PipeWire	s16le 1ch 12000Hz	SUSPENDED
elec3607@raspberrypi:~/lab4-wspr $ pactl list short sinks
72	alsa_output.usb-Plugable_Plugable_USB_Audio_Device_000000000000-00.analog-stereo	PipeWire	s16le 2ch 48000Hz	SUSPENDED
74	alsa_output.platform-bcm2835_audio.stereo-fallback	PipeWire	s16le 2ch 48000Hz	SUSPENDED
75	alsa_output.platform-fef00700.hdmi.hdmi-stereo	PipeWire	s32le 2ch 48000Hz	SUSPENDED
96	MySink	PipeWire	s16le 1ch 12000Hz	SUSPENDED
```
You can see that MySink.monitor and MySink are available. Note the sources and sinks are SUSPENDED but will change to Running when in use.

Do the following and explain the purpose of these commands.
```bash
elec3607@raspberrypi:~/lab4-wspr $ pactl set-default-sink 96
elec3607@raspberrypi:~/lab4-wspr $ pactl set-default-source 96
elec3607@raspberrypi:~/lab4-wspr $ pactl info  
Server String: /run/user/1000/pulse/native
Library Protocol Version: 35
Server Protocol Version: 35
Is Local: yes
Client Index: 105
Tile Size: 65472
User Name: elec3607
Host Name: raspberrypi
Server Name: PulseAudio (on PipeWire 1.2.4)
Server Version: 15.0.0
Default Sample Specification: float32le 2ch 48000Hz
Default Channel Map: front-left,front-right
Default Sink: MySink
Default Source: MySink.monitor
Cookie: 4b1b:6f37
```

## Question 2 - Compiling wsprd (10\%)
```wsprd``` is a program that decodes baseband wspr files (i.e. wspr files that have been downconverted). You can compile with the following ```make``` command but unfortunately, it is missing the fft3 library.

```bash
elec3607@raspberrypi:~/lab4-wspr $ make wspr
(cd wsprcan; make)
make[1]: Entering directory '/home/elec3607/lab4-wspr/wsprcan'
gcc -c -o wsprd.o wsprd.c -I/usr/local/include -Wall -Wextra -std=c99 -pedantic -O3 -ffast-math
wsprd.c:37:10: fatal error: fftw3.h: No such file or directory
   37 | #include <fftw3.h>
      |          ^~~~~~~~~
compilation terminated.
make[1]: *** [Makefile:8: wsprd.o] Error 1
make[1]: Leaving directory '/home/elec3607/lab4-wspr/wsprcan'
make: *** [Makefile:5: wspr] Error 2
```

Figure out how to fix this issue by installing the appropriate Debian libraries. When successful ```make wpsr``` should compile and run successfully.

```bash
elec3607@raspberrypi:~/lab4-wspr $ make wspr
(cd wsprcan; make)
make[1]: Entering directory '/home/elec3607/lab4-wspr/wsprcan'
make[1]: Nothing to be done for 'all'.
make[1]: Leaving directory '/home/elec3607/lab4-wspr/wsprcan'
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

Unfortunately, it doesn't compile
```bash
elec3607@raspberrypi:~/lab4-wspr $ cd parecfile
elec3607@raspberrypi:~/lab4-wspr/parecfile $ make
gcc -Wall -g  -c parecfile.c  -o parecfile.o
parecfile.c:29:10: fatal error: pulse/simple.h: No such file or directory
   29 | #include <pulse/simple.h>
      |          ^~~~~~~~~~~~~~~~
compilation terminated.
make: *** [Makefile:62: parecfile.o] Error 1
```
Fix this problem by figuring out the appropriate libraries and packages to install. 
Study what this program does as you will need it for the following question.

## Question 4 - Modifying wsprcan/wsprd.c (60\%)

Using the ```parecfile/parecfile.c``` code as an example,
modify ```wsprcan/wsprd.c``` so that it takes input from pulseaudio instead of the file. Demonstrate that your program works by playing a file in the background and decoding it with your modified program. The supplied script, wspr-test does this for you:
```bash
elec3607@raspberrypi:~/lab4-wspr $ cat wspr-test
#!/bin/bash

# this plays an audio file in the background and runs pa-wsprcan
echo -n "running paplay at "
date
paplay data/iq-16b.wav &
./pa-wsprcan/k9an-wsprd 
date
elec3607@raspberrypi:~/lab4-wspr $ ./wspr-test
running paplay at Wed  2 Apr 14:54:35 AEDT 2025
mode  -1 -2.0   0.001437 -2  VK2RG QF56 30 
mode -19 -1.8   0.001455 -1  VK3GOD QF23 23 
mode -20 -1.9   0.001478 -1  VK4YEH QG62 37 
<DecodeFinished,data/wf-1712294438.wav,3>
running paplay at Wed  2 Apr 14:56:30 AEDT 2025
```

## Question 5 - wsprwait (10\%)
Study the bash script wsprwait. In your lab book, provide an annotated listing of what this does and why it might be useful in this project.
