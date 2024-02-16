# Lab1 gpio

In this lab you will learn how to manipulate GPIO output in two different
ways. 
    1. Using ```libgpiod```, this provides a hardware independent
technique to perform input and output via GPIO. 
    2. By directly controlling the registers on the microcontroller, this gives the highest performance and flexibility but is device-dependent. 

## 1. libgpiod (30%)
First install the libgpiod library using the ```apt``` command. This needs
to be run as a superuser via ```sudo``` since the library is installed in 
a system directory (```/usr/lib/libgpiod.so```). This is done as below:

```bash
elec3607@raspberrypi:~/elec3607-lab/labs/lab1-gpio $ sudo apt install libgpiod-dev
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
Suggested packages:
  libgpiod-doc
The following NEW packages will be installed:
  libgpiod-dev
0 upgraded, 1 newly installed, 0 to remove and 18 not upgraded.
Need to get 58.4 kB of archives.
After this operation, 352 kB of additional disk space will be used.
Get:1 http://deb.debian.org/debian bookworm/main arm64 libgpiod-dev arm64 1.6.3-1+b3 [58.4 kB]
Fetched 58.4 kB in 0s (140 kB/s)  
Selecting previously unselected package libgpiod-dev:arm64.
(Reading database ... 144701 files and directories currently installed.)
Preparing to unpack .../libgpiod-dev_1.6.3-1+b3_arm64.deb ...
Unpacking libgpiod-dev:arm64 (1.6.3-1+b3) ...
Setting up libgpiod-dev:arm64 (1.6.3-1+b3) ...
```

The code in ```lab1-gpio/lab1-gpio/lab1/libgpiod_blink.c``` is a skeleton code. 
Complete the parts labelled ```XXX``` to create a program that will 
output a square wave on GPIO 26. Using an oscilloscope, measure the
frequency of the square wave and put a screen shot in your lab book
together with an explanation of the changes that you needed to make.

It is compiled and executed as follows:
```bash
elec3607@raspberrypi:~/elec3607-lab/labs/lab1-gpio $ make
cc -c -Wall -g   libgpiod_blink.c -o libgpiod_blink.o
cc -o libgpiod_blink libgpiod_blink.o -lgpiod 
elec3607@raspberrypi:~/elec3607-lab/labs/lab1-gpio $ ./libgpiod_blink
```

## 2. mmap (40%)
The code in ```mmap_blink.c``` is similar to ```libgpiod_blink.c``` except
that it directly manipulates registers. Again, there are parts missing to
the program marked as ```XXX```. Fill them in and create a version that
produces a square wave at 50MHz +/- 20%. Make an oscilloscope screen shot of this version and write an explanation of the changes that you needed to make.

## 3. mmap (30%)
Modify the mmap version to produce the highest clock frequency square wave,
capture a screen shot and record the shortest period achieved. Try to get the best oscilloscope trace of the
output. If it doesn't look like a square wave, explain why.
