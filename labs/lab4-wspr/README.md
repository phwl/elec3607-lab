# SDR Software
This lab involves installing software defined radio (SDR) software on the RPi including
 * pulseaudio, a library which will allow you to access the audio features of Linux
 * the wspr decoder

First cd to your ```elec3607-lab``` directory and type ```git pull``` to ensure you have the latest version of the lab. Then update apt and install ```pavucontrol```.
```bash
elec3607@raspberrypi:~/elec3607-lab/labs/lab4-wspr $ sudo apt update
Hit:1 http://deb.debian.org/debian bookworm InRelease
Hit:2 http://deb.debian.org/debian-security bookworm-security InRelease
Hit:3 http://deb.debian.org/debian bookworm-updates InRelease                  
Hit:4 http://archive.raspberrypi.com/debian bookworm InRelease                 
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
139 packages can be upgraded. Run 'apt list --upgradable' to see them.
elec3607@raspberrypi:~/elec3607-lab/labs/lab4-wspr $ sudo apt install pavucontrol
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
The following packages were automatically installed and are no longer required:
  catch2 libcppunit-1.15-0 libcppunit-dev libeigen3-dev libfmt-dev libglfw3
  libgmp-dev libgmpxx4ldbl libgnuradio-fosphor3.9.0 libgsm1-dev
  libraspberrypi0 libspdlog-dev libthrift-dev pybind11-dev
Use 'sudo apt autoremove' to remove them.
The following additional packages will be installed:
  libcanberra-gtk3-0 libcanberra-gtk3-module libcanberra0
  libpulse-mainloop-glib0 sound-theme-freedesktop
Suggested packages:
  libcanberra-gtk0 libcanberra-pulse
The following NEW packages will be installed:
  libcanberra-gtk3-0 libcanberra-gtk3-module libcanberra0
  libpulse-mainloop-glib0 pavucontrol sound-theme-freedesktop
0 upgraded, 6 newly installed, 0 to remove and 139 not upgraded.
Need to get 641 kB of archives.
After this operation, 2,131 kB of additional disk space will be used.
Do you want to continue? [Y/n] 
Get:1 http://deb.debian.org/debian bookworm/main arm64 sound-theme-freedesktop all 0.8-2 [384 kB]
Get:2 http://deb.debian.org/debian bookworm/main arm64 libcanberra0 arm64 0.30-10 [38.3 kB]
Get:3 http://deb.debian.org/debian bookworm/main arm64 libcanberra-gtk3-0 arm64 0.30-10 [12.3 kB]
Get:4 http://deb.debian.org/debian bookworm/main arm64 libcanberra-gtk3-module arm64 0.30-10 [14.2 kB]
Get:5 http://deb.debian.org/debian bookworm/main arm64 pavucontrol arm64 5.0-2 [166 kB]
Get:6 http://archive.raspberrypi.com/debian bookworm/main arm64 libpulse-mainloop-glib0 arm64 16.1+dfsg1-2+rpt1 [26.8 kB]
Fetched 641 kB in 1s (565 kB/s)                   
Selecting previously unselected package sound-theme-freedesktop.
(Reading database ... 197408 files and directories currently installed.)
Preparing to unpack .../0-sound-theme-freedesktop_0.8-2_all.deb ...
Unpacking sound-theme-freedesktop (0.8-2) ...
Selecting previously unselected package libcanberra0:arm64.
Preparing to unpack .../1-libcanberra0_0.30-10_arm64.deb ...
Unpacking libcanberra0:arm64 (0.30-10) ...
Selecting previously unselected package libcanberra-gtk3-0:arm64.
Preparing to unpack .../2-libcanberra-gtk3-0_0.30-10_arm64.deb ...
Unpacking libcanberra-gtk3-0:arm64 (0.30-10) ...
Selecting previously unselected package libcanberra-gtk3-module:arm64.
Preparing to unpack .../3-libcanberra-gtk3-module_0.30-10_arm64.deb ...
Unpacking libcanberra-gtk3-module:arm64 (0.30-10) ...
Selecting previously unselected package libpulse-mainloop-glib0:arm64.
Preparing to unpack .../4-libpulse-mainloop-glib0_16.1+dfsg1-2+rpt1_arm64.deb ..
.
Unpacking libpulse-mainloop-glib0:arm64 (16.1+dfsg1-2+rpt1) ...
Selecting previously unselected package pavucontrol.
Preparing to unpack .../5-pavucontrol_5.0-2_arm64.deb ...
Unpacking pavucontrol (5.0-2) ...
Setting up libpulse-mainloop-glib0:arm64 (16.1+dfsg1-2+rpt1) ...
Setting up sound-theme-freedesktop (0.8-2) ...
Setting up libcanberra0:arm64 (0.30-10) ...
Setting up libcanberra-gtk3-0:arm64 (0.30-10) ...
Setting up libcanberra-gtk3-module:arm64 (0.30-10) ...
Setting up pavucontrol (5.0-2) ...
Processing triggers for libc-bin (2.36-9+rpt2+deb12u4) ...
Processing triggers for man-db (2.11.2-2) ...
Processing triggers for mailcap (3.70+nmu1) ...
Processing triggers for desktop-file-utils (0.26-1) ...
Processing triggers for gnome-menus (3.36.0-1.1) ...
```
## Question 1 -  Pipewire (10\%)

In this question, you will explore some of the features of [Pipewire](https://docs.pipewire.org/).  Plug in your USB sound card. It should appear if you type the following:
```bash
elec3607@raspberrypi:~/elec3607-lab/labs/lab4-wspr $ wpctl status
PipeWire 'pipewire-0' [0.3.65, elec3607@raspberrypi, cookie:4100166877]
 └─ Clients:
        31. pipewire                            [0.3.65, elec3607@raspberrypi, pid:943]
        33. WirePlumber                         [0.3.65, elec3607@raspberrypi, pid:942]
        34. WirePlumber [export]                [0.3.65, elec3607@raspberrypi, pid:942]
        83. xdg-desktop-portal-wlr              [0.3.65, elec3607@raspberrypi, pid:1284]
        84. xdg-desktop-portal                  [0.3.65, elec3607@raspberrypi, pid:1215]
        85. unknown                             [0.3.65, elec3607@raspberrypi, pid:1119]
        86. wpctl                               [0.3.65, elec3607@raspberrypi, pid:8977]

Audio
 ├─ Devices:
 │      54. Plugable USB Audio Device           [alsa]
 │      55. Built-in Audio                      [alsa]
 │      56. Built-in Audio                      [alsa]
 │      57. Built-in Audio                      [alsa]
 │  
 ├─ Sinks:
 │      32. Built-in Audio Digital Stereo (HDMI) [vol: 0.40]
 │  *   70. Plugable USB Audio Device Analog Stereo [vol: 0.40]
 │      72. Built-in Audio Stereo               [vol: 0.40]
 │  
 ├─ Sink endpoints:
 │  
 ├─ Sources:
 │  *   71. Plugable USB Audio Device Analog Stereo [vol: 1.00]
 │  
 ├─ Source endpoints:
 │  
 └─ Streams:

Video
 ├─ Devices:
 │      40. rpivid                              [v4l2]
 │      41. bcm2835-codec-decode                [v4l2]
 │      42. bcm2835-codec-encode                [v4l2]
 │      43. bcm2835-codec-isp                   [v4l2]
 │      44. bcm2835-codec-image_fx              [v4l2]
 │      45. bcm2835-codec-encode_image          [v4l2]
 │      46. bcm2835-isp                         [v4l2]
 │      47. bcm2835-isp                         [v4l2]
 │      48. bcm2835-isp                         [v4l2]
 │      49. bcm2835-isp                         [v4l2]
 │      50. bcm2835-isp                         [v4l2]
 │      51. bcm2835-isp                         [v4l2]
 │      52. bcm2835-isp                         [v4l2]
 │      53. bcm2835-isp                         [v4l2]
 │  
 ├─ Sinks:
 │  
 ├─ Sink endpoints:
 │  
 ├─ Sources:
 │      58. bcm2835-isp (V4L2)                 
 │      60. bcm2835-isp (V4L2)                 
 │      62. bcm2835-isp (V4L2)                 
 │      64. bcm2835-isp (V4L2)                 
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
elec3607@raspberrypi:~/elec3607-lab/labs/lab4-wspr $ pactl info
Server String: /run/user/1000/pulse/native
Library Protocol Version: 35
Server Protocol Version: 35
Is Local: yes
Client Index: 217
Tile Size: 65472
User Name: elec3607
Host Name: raspberrypi
Server Name: PulseAudio (on PipeWire 0.3.65)
Server Version: 15.0.0
Default Sample Specification: float32le 2ch 48000Hz
Default Channel Map: front-left,front-right
Default Sink: alsa_output.usb-Plugable_Plugable_USB_Audio_Device_000000000000-00.analog-stereo
Default Source: alsa_input.usb-Plugable_Plugable_USB_Audio_Device_000000000000-00.analog-stereo
Cookie: f463:94dd
```

We are going to create a virtual audio sink which is mono and 12000 samples a second. This is done using:
```bash
elec3607@raspberrypi:~/.config $ pactl load-module module-null-sink sink_name=MySink format=s16le channels=1 rate=12000
536870913
```

Now let's list the sources and sinks:
```bash
elec3607@raspberrypi:~/elec3607-lab/labs/lab4-wspr $ pactl list short sources
70	alsa_output.usb-Plugable_Plugable_USB_Audio_Device_000000000000-00.analog-stereo.monitor	PipeWire	s16le 2ch 48000Hz	RUNNING
71	alsa_input.usb-Plugable_Plugable_USB_Audio_Device_000000000000-00.analog-stereo	PipeWire	s16le 2ch 48000Hz	RUNNING
72	alsa_output.platform-bcm2835_audio.stereo-fallback.monitor	PipeWirs16le 2ch 48000Hz	RUNNING
73	alsa_output.platform-fef00700.hdmi.hdmi-stereo.monitor	PipeWire	s32le 2ch 48000Hz	RUNNING
176	MySink.monitor	PipeWire	float32le 1ch 12000Hz	RUNNING
elec3607@raspberrypi:~/.config $ pactl list short sinks
70	alsa_output.usb-Plugable_Plugable_USB_Audio_Device_000000000000-00.analog-stereo	PipeWire	s16le 2ch 48000Hz	IDLE
72	alsa_output.platform-bcm2835_audio.stereo-fallback	PipeWire	s16le 2ch 48000Hz	IDLE
73	alsa_output.platform-fef00700.hdmi.hdmi-stereo	PipeWire	s32le 2ch 48000Hz	IDLE
176	MySink	PipeWire	float32le 1ch 12000Hz	IDLE
```
You can see that MySink.monitor and MySink are available.

You should now be able to play a file using ```paplay``` and display the level graphically with ```pavucontrol```:

```bash
elec3607@raspberrypi:~/elec3607-lab/labs/lab4-wspr $ paplay data/iq-16b.wav &
[1] 2823
elec3607@raspberrypi:~/elec3607-lab/labs/lab4-wspr $ pavucontrol&
[2] 2824
```

This should result in the display below and the VU meter will display the level of the file ```data/iq-16b.wav``` as it plays.

![](pavucontrol.png)

## Question 2 - Compiling wsprd (10\%)
```wsprd``` is a program that decodes baseband wspr files (i.e. wspr files that have been downconverted). You can compile with the following ```make``` command but unfortunately, it is missing the fft3 library.

```bash
elec3607@raspberrypi:~/elec3607-lab/labs/lab4-wspr $ make wspr
(cd wsprcan; make)
make[1]: Entering directory '/home/elec3607/elec3607-lab/labs/lab4-wspr/wsprcan'
gcc -c -o wsprd.o wsprd.c -I/usr/local/include -Wall -Wextra -std=c99 -pedantic -O3 -ffast-math
wsprd.c:37:10: fatal error: fftw3.h: No such file or directory
   37 | #include <fftw3.h>
      |          ^~~~~~~~~
compilation terminated.
make[1]: *** [Makefile:8: wsprd.o] Error 1
make[1]: Leaving directory '/home/elec3607/elec3607-lab/labs/lab4-wspr/wsprcan'
make: *** [Makefile:5: wspr] Error 2
```

Figure out how to fix this issue by installing the appropriate Debian libraries. When successful ```make wpsr``` should compile and run successfully.

```bash
elec3607@raspberrypi:~/elec3607-lab/labs/lab4-wspr $ make wspr
(cd wsprcan; make)
make[1]: Entering directory '/home/elec3607/elec3607-lab/labs/lab4-wspr/wsprcan'
make[1]: Nothing to be done for 'all'.
make[1]: Leaving directory '/home/elec3607/elec3607-lab/labs/lab4-wspr/wsprcan'
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
In the parecfile directory, parecfile.c is a program that records some data via pulseaudio, and then writes it to stdout. As its name suggests, the pulseaudio simple interface is very simple and its documentation is available [here](https://www.freedesktop.org/wiki/Software/PulseAudio/Documentation/).

Unfortunately, it doesn't compile
```bash
elec3607@raspberrypi:~/elec3607-course/labs/lab4-wspr $ cd parecfile
elec3607@raspberrypi:~/elec3607-course/labs/lab4-wspr/parecfile $ make
gcc -Wall -g  -c parecfile.c  -o parecfile.o
parecfile.c:29:10: fatal error: pulse/simple.h: No such file or directory
   29 | #include <pulse/simple.h>
      |          ^~~~~~~~~~~~~~~~
compilation terminated.
make: *** [Makefile:62: parecfile.o] Error 1
```
Fix this problem by figuring out the appropriate libraries and packages to install. 
Study what this program does as you will need it for the following question.

## Question 4 - Modifying wsprcan/wsprd.c (70\%)

Modify ```wsprcan/wsprd.c``` so that it takes input from pulseaudio instead of the file.
