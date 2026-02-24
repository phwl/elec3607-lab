# Lab1 gpio

In this lab you will learn how to manipulate GPIO output in two different
ways ([libgpiod](https://libgpiod.readthedocs.io/en/latest/index.html) and [mmap](https://linux.die.net/man/2/mmap)).

## 1. Installation (20%)
To start, you should download all the lab materials for this course. With your 
AUP-ZU3 connected to the internet, use the following command:
```bash
petalinux-8GB:~$ git clone https://github.com/phwl/elec3607-lab.git
Cloning into 'elec3607-lab'...
remote: Enumerating objects: 1596, done.
remote: Counting objects: 100% (43/43), done.
remote: Compressing objects: 100% (26/26), done.
remote: Total 1596 (delta 29), reused 29 (delta 17), pack-reused 1553 (from 1)
Receiving objects: 100% (1596/1596), 116.10 MiB | 12.53 MiB/s, done.
Resolving deltas: 100% (907/907), done.
Updating files: 100% (222/222), done.
petalinux-8GB:~$ 
```
This will create the directory ```elec3607-lab```. To go to the directory
for Lab 2:
```bash
petalinux-8GB:~$ cd elec3607-lab/labs/lab2-gpio/
petalinux-8GB:~/elec3607-lab/labs/lab2-gpio$ ls
Makefile  README.md  libgpiod-ref.pdf  libgpiod_blink.c  mmap_blink.c
petalinux-8GB:~/elec3607-lab/labs/lab2-gpio$ 
```

Finally, use superuser priviliges to modify the permissions of the gpio        
device so that it can be used by all users
```bash                                                                       
sudo chmod a+rw /dev/gpiochip6                                            
```

## 2. Libgpiod commands (30%)

Since Linux v4.8, the standard way of using Linux GPIO has been via libgpiod. Prior to the introduction of libgpiod, the sysfs interface was used, but sysfs is depreciated and was removed from the mainline Linux kernel in 2020. The library
provides a hardware independent technique to perform input and output via GPIO (see [the manual](./libgpiod-ref.pdf)). 

The library comes with a number of command line tools to manipulate GPIOs:
```
gpiodetect - list all gpiochips present on the system, their names, labels and number of GPIO lines

gpioinfo - list all lines of specified gpiochips, their names, consumers, direction, active state and additional flags

gpioget - read values of specified GPIO lines

gpioset - set values of specified GPIO lines, potentially keep the lines exported and wait until timeout, user input or signal

gpiofind - find the gpiochip name and line offset given the line name

gpiomon - wait for events on GPIO lines, specify which events to watch, how many events to process before exiting or if the events should be reported to the console.
```

Here are some usage examples from the Linux documentation (you need to do 
sudo to get permission to interrogate all the gpio chips whereas 
you don't need to do so for gpiochip6 because we gave global
access permission earlier)
```bash
petalinux-8GB:~/elec3607-lab/labs/lab2-gpio$ sudo gpioinfo
gpiochip0 - 4 lines:
        line   0:   "PS_MODE0"       unused   input  active-high 
        line   1:   "PS_MODE1"      "reset"  output   active-low [used]
...
gpiochip6 - 28 lines:
        line   0:  "RPI_GPIO0"       unused   input  active-high 
        line   1:  "RPI_GPIO1"       unused   input  active-high 
        line   2:  "RPI_GPIO2"       unused   input  active-high 
        line   3:  "RPI_GPIO3"       unused   input  active-high 
        line   4:  "RPI_GPIO4"       unused   input  active-high 
...
petalinux-8GB:~/elec3607-lab/labs/lab2-gpio$ sudo gpioget gpiochip6 2
1
petalinux-8GB:~/elec3607-lab/labs/lab2-gpio$ sudo gpioget --active-low gpiochip6 0 2
0 0
petalinux-8GB:~/elec3607-lab/labs/lab2-gpio$ sudo gpioset gpiochip6 4=1
0 0
petalinux-8GB:~/elec3607-lab/labs/lab2-gpio$ sudo gpioinfo gpiochip6
gpiochip6 - 28 lines:
        line   0:  "RPI_GPIO0"       unused   input  active-high 
        line   1:  "RPI_GPIO1"       unused   input  active-high 
        line   2:  "RPI_GPIO2"       unused   input  active-high 
        line   3:  "RPI_GPIO3"       unused   input  active-high 
        line   4:  "RPI_GPIO4"       unused  output  active-high 
...
```

In your lab book, explain what each of the commands above do, the return
values received, and how they affect the physical GPIO pin.

Using the above commands, demonstrate using an oscilloscope that you can control RPI_GPIO24 and make that pin high or low using the correct command-line command.
You will need to refer to the [Reference Manual](doc/ZU3_RM_A1.pdf) to find
the pin on the board.

## 3. Libgpiod C code (30%)

The code in ```lab1-gpio/lab1-gpio/lab1/libgpiod_blink.c``` is a skeleton code
that, when correctly completed, will output a square wave. 
Complete the parts labelled ```XXX``` to create a program that will 
output a 1 Hz square wave on RPI_GPIO24. 

The program is compiled and executed (but will show an error because 
the program hasn't been completed) as follows:
```bash
petalinux-8GB:~/elec3607-lab/labs/lab2-gpio$ make libpiod_blink
make: *** No rule to make target 'libpiod_blink'.  Stop.
petalinux-8GB:~/elec3607-lab/labs/lab2-gpio$ make libgpiod_blink
cc -c -Wall -g   libgpiod_blink.c -o libgpiod_blink.o
libgpiod_blink.c: In function 'gpio_init':
libgpiod_blink.c:34:27: error: 'XXX' undeclared (first use in this function)
   34 |         output_lines[i] = XXX;
      |                           ^~~
libgpiod_blink.c:34:27: note: each undeclared identifier is reported only once for each function it appears in
libgpiod_blink.c:18:9: warning: unused variable 'pins' [-Wunused-variable]
   18 |     int pins[] = { 26 };                // operate on all these pins
      |         ^~~~
libgpiod_blink.c: In function 'gpio_writer':
libgpiod_blink.c:52:13: error: 'XXX' undeclared (first use in this function)
   52 |             XXX;        // write v to line j
      |             ^~~
make: *** [Makefile:14: libgpiod_blink.o] Error 1
```

After fixing, you can execute it by typing:
```
petalinux-8GB:~/elec3607-lab/labs/lab2-gpio$ make libgpiod_blink
cc -c -Wall -g   libgpiod_blink.c -o libgpiod_blink.o
cc -o libgpiod_blink libgpiod_blink.o -lgpiod 
petalinux-8GB:~/elec3607-lab/labs/lab2-gpio$ ./libgpiod_blink
```

Using an oscilloscope, measure the
frequency of the square wave and put a screen shot in your lab book
together with an explanation of your changes.

## 4. mmap (20%)
Directly controlling the registers on the microcontroller via ```mmap(2)``` gives the highest flexibility but is device-dependent, dangerous (because buggy code could affect other peripherals) and insecure.

The code in ```mmap_blink.c``` is similar to ```libgpiod_blink.c``` except
that it directly manipulates registers. Again, there are parts missing to
the program marked as ```XXX```. Fill them in and create a version that
produces a square wave at the maximum possible frequency. Make an oscilloscope screen shot of this version and write an explanation of the changes that you needed to make. In addition, make a screen shot measuring the rise time of the square wave output.

