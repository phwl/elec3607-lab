# Lab1 gpio

In this lab you will learn how to manipulate GPIO output in two different
ways (libgpiod and mmap).

## 1. Installation (10%)
To start, you should download all the lab materials for this course. With your 
RPi connected to the internet, use the following command:
```bash
elec3607@raspberrypi:~ $ git clone https://github.com/phwl/elec3607-lab.git
Cloning into 'elec3607-lab'...
remote: Enumerating objects: 594, done.
remote: Counting objects: 100% (223/223), done.
remote: Compressing objects: 100% (165/165), done.
remote: Total 594 (delta 84), reused 185 (delta 51), pack-reused 371
Receiving objects: 100% (594/594), 53.54 MiB | 7.62 MiB/s, done.
Resolving deltas: 100% (230/230), done.
```
This will create the directory ```elec3607-lab```. To go to the directory
for Lab 1:
```bash
elec3607@raspberrypi:~ $ cd elec3607-lab/labs/lab1-gpio/
elec3607@raspberrypi:~/elec3607-lab/labs/lab1-gpio $ ls
libgpiod_blink.c  Makefile  mmap_blink.c  README.md
```

Install the libgpiod library using the ```apt``` command. This needs
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

## 2. Libgpiod (30%)

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

Here are some usage examples from the Linux documentation
```bash
elec3607@raspberrypi:~ $ gpioinfo
gpiochip0 - 58 lines:
	line   0:     "ID_SDA"       unused   input  active-high 
	line   1:     "ID_SCL"       unused   input  active-high 
	line   2:       "SDA1"       unused   input  active-high 
	line   3:       "SCL1"       unused   input  active-high 
	line   4:  "GPIO_GCLK"       unused   input  active-high 
	line   5:      "GPIO5"       unused   input  active-high 
	line   6:      "GPIO6"       unused   input  active-high 
	line   7:  "SPI_CE1_N"       unused   input  active-high 
	line   8:  "SPI_CE0_N"       unused   input  active-high 
	line   9:   "SPI_MISO"       unused   input  active-high 
	line  10:   "SPI_MOSI"       unused   input  active-high 
	line  11:   "SPI_SCLK"       unused   input  active-high 
	line  12:     "GPIO12"       unused   input  active-high 
	line  13:     "GPIO13"       unused   input  active-high 
	line  14:       "TXD1"       unused   input  active-high 
	line  15:       "RXD1"       unused   input  active-high 
	line  16:     "GPIO16"       unused   input  active-high 
	line  17:     "GPIO17"       unused   input  active-high 
	line  18:     "GPIO18"       unused   input  active-high 
	line  19:     "GPIO19"       unused   input  active-high 
	line  20:     "GPIO20"       unused   input  active-high 
	line  21:     "GPIO21"       unused   input  active-high 
	line  22:     "GPIO22"       unused   input  active-high 
	line  23:     "GPIO23"       unused   input  active-high 
	line  24:     "GPIO24"       unused   input  active-high 
	line  25:     "GPIO25"       unused   input  active-high 
	line  26:     "GPIO26"       unused   input  active-high 
	line  27:     "GPIO27"       unused   input  active-high 
	line  28: "RGMII_MDIO"       unused   input  active-high 
	line  29:  "RGMIO_MDC"       unused   input  active-high 
	line  30:       "CTS0"       unused   input  active-high 
	line  31:       "RTS0"       unused   input  active-high 
	line  32:       "TXD0"       unused   input  active-high 
	line  33:       "RXD0"       unused   input  active-high 
	line  34:    "SD1_CLK"       unused   input  active-high 
	line  35:    "SD1_CMD"       unused   input  active-high 
	line  36:  "SD1_DATA0"       unused   input  active-high 
	line  37:  "SD1_DATA1"       unused   input  active-high 
	line  38:  "SD1_DATA2"       unused   input  active-high 
	line  39:  "SD1_DATA3"       unused   input  active-high 
	line  40:  "PWM0_MISO"       unused   input  active-high 
	line  41:  "PWM1_MOSI"       unused   input  active-high 
	line  42: "STATUS_LED_G_CLK" "ACT" output active-high [used]
	line  43: "SPIFLASH_CE_N" unused input active-high 
	line  44:       "SDA0"       unused   input  active-high 
	line  45:       "SCL0"       unused   input  active-high 
	line  46: "RGMII_RXCLK" unused input active-high 
	line  47: "RGMII_RXCTL" unused input active-high 
	line  48: "RGMII_RXD0"       unused   input  active-high 
	line  49: "RGMII_RXD1"       unused   input  active-high 
	line  50: "RGMII_RXD2"       unused   input  active-high 
	line  51: "RGMII_RXD3"       unused   input  active-high 
	line  52: "RGMII_TXCLK" unused input active-high 
	line  53: "RGMII_TXCTL" unused input active-high 
	line  54: "RGMII_TXD0"       unused   input  active-high 
	line  55: "RGMII_TXD1"       unused   input  active-high 
	line  56: "RGMII_TXD2"       unused   input  active-high 
	line  57: "RGMII_TXD3"       unused   input  active-high 
gpiochip1 - 8 lines:
	line   0:      "BT_ON"   "shutdown"  output  active-high [used]
	line   1:      "WL_ON"       unused  output  active-high 
	line   2: "PWR_LED_OFF" "PWR" output active-low [used]
	line   3: "GLOBAL_RESET" unused output active-high 
	line   4: "VDD_SD_IO_SEL" "vdd-sd-io" output active-high [used]
	line   5:   "CAM_GPIO" "cam1_regulator" output active-high [used]
	line   6:  "SD_PWR_ON" "sd_vcc_reg"  output  active-high [used]
	line   7:    "SD_OC_N"       unused   input  active-high 
elec3607@raspberrypi:~ $ gpioget gpiochip0 2
1
elec3607@raspberrypi:~ $ gpioget --active-low gpiochip0 0 2
0 0
elec3607@raspberrypi:~ $ gpioset gpiochip0 4=1
elec3607@raspberrypi:~ $ gpioinfo
gpiochip0 - 58 lines:
	line   0:     "ID_SDA"       unused   input  active-high 
	line   1:     "ID_SCL"       unused   input  active-high 
	line   2:       "SDA1"       unused   input  active-high 
	line   3:       "SCL1"       unused   input  active-high 
	line   4:  "GPIO_GCLK"       unused  output  active-high 
	line   5:      "GPIO5"       unused   input  active-high 
	line   6:      "GPIO6"       unused   input  active-high 
	line   7:  "SPI_CE1_N"       unused   input  active-high 
	line   8:  "SPI_CE0_N"       unused   input  active-high 
	line   9:   "SPI_MISO"       unused   input  active-high 
	line  10:   "SPI_MOSI"       unused   input  active-high 
	line  11:   "SPI_SCLK"       unused   input  active-high 
	line  12:     "GPIO12"       unused   input  active-high 
	line  13:     "GPIO13"       unused   input  active-high 
	line  14:       "TXD1"       unused   input  active-high 
	line  15:       "RXD1"       unused   input  active-high 
	line  16:     "GPIO16"       unused   input  active-high 
	line  17:     "GPIO17"       unused   input  active-high 
	line  18:     "GPIO18"       unused   input  active-high 
	line  19:     "GPIO19"       unused   input  active-high 
	line  20:     "GPIO20"       unused   input  active-high 
	line  21:     "GPIO21"       unused   input  active-high 
	line  22:     "GPIO22"       unused   input  active-high 
	line  23:     "GPIO23"       unused   input  active-high 
	line  24:     "GPIO24"       unused   input  active-high 
	line  25:     "GPIO25"       unused   input  active-high 
	line  26:     "GPIO26"       unused   input  active-high 
	line  27:     "GPIO27"       unused   input  active-high 
	line  28: "RGMII_MDIO"       unused   input  active-high 
	line  29:  "RGMIO_MDC"       unused   input  active-high 
	line  30:       "CTS0"       unused   input  active-high 
	line  31:       "RTS0"       unused   input  active-high 
	line  32:       "TXD0"       unused   input  active-high 
	line  33:       "RXD0"       unused   input  active-high 
	line  34:    "SD1_CLK"       unused   input  active-high 
	line  35:    "SD1_CMD"       unused   input  active-high 
	line  36:  "SD1_DATA0"       unused   input  active-high 
	line  37:  "SD1_DATA1"       unused   input  active-high 
	line  38:  "SD1_DATA2"       unused   input  active-high 
	line  39:  "SD1_DATA3"       unused   input  active-high 
	line  40:  "PWM0_MISO"       unused   input  active-high 
	line  41:  "PWM1_MOSI"       unused   input  active-high 
	line  42: "STATUS_LED_G_CLK" "ACT" output active-high [used]
	line  43: "SPIFLASH_CE_N" unused input active-high 
	line  44:       "SDA0"       unused   input  active-high 
	line  45:       "SCL0"       unused   input  active-high 
	line  46: "RGMII_RXCLK" unused input active-high 
	line  47: "RGMII_RXCTL" unused input active-high 
	line  48: "RGMII_RXD0"       unused   input  active-high 
	line  49: "RGMII_RXD1"       unused   input  active-high 
	line  50: "RGMII_RXD2"       unused   input  active-high 
	line  51: "RGMII_RXD3"       unused   input  active-high 
	line  52: "RGMII_TXCLK" unused input active-high 
	line  53: "RGMII_TXCTL" unused input active-high 
	line  54: "RGMII_TXD0"       unused   input  active-high 
	line  55: "RGMII_TXD1"       unused   input  active-high 
	line  56: "RGMII_TXD2"       unused   input  active-high 
	line  57: "RGMII_TXD3"       unused   input  active-high 
gpiochip1 - 8 lines:
	line   0:      "BT_ON"   "shutdown"  output  active-high [used]
	line   1:      "WL_ON"       unused  output  active-high 
	line   2: "PWR_LED_OFF" "PWR" output active-low [used]
	line   3: "GLOBAL_RESET" unused output active-high 
	line   4: "VDD_SD_IO_SEL" "vdd-sd-io" output active-high [used]
	line   5:   "CAM_GPIO" "cam1_regulator" output active-high [used]
	line   6:  "SD_PWR_ON" "sd_vcc_reg"  output  active-high [used]
	line   7:    "SD_OC_N"       unused   input  active-high
```


The code in ```lab1-gpio/lab1-gpio/lab1/libgpiod_blink.c``` is a skeleton code. 
Complete the parts labelled ```XXX``` to create a program that will 
output a square wave on GPIO 26. Using an oscilloscope, measure the
frequency of the square wave and put a screen shot in your lab book
together with an explanation of the changes that you needed to make.

It is compiled and executed as follows:
```bash
elec3607@raspberrypi:~/elec3607-lab/labs/lab1-gpio $ make libgpiod_blink
cc -c -Wall -g   libgpiod_blink.c -o libgpiod_blink.o
cc -o libgpiod_blink libgpiod_blink.o -lgpiod 
elec3607@raspberrypi:~/elec3607-lab/labs/lab1-gpio $ ./libgpiod_blink
```

## 3. mmap (50 MHz) (40%)
Directly controlling the registers on the microcontroller via ```mmap(2)``` gives the highest performance and flexibility but is device-dependent. 

The code in ```mmap_blink.c``` is similar to ```libgpiod_blink.c``` except
that it directly manipulates registers. Again, there are parts missing to
the program marked as ```XXX```. Fill them in and create a version that
produces a square wave at 50MHz +/- 20%. Make an oscilloscope screen shot of this version and write an explanation of the changes that you needed to make.

## 4. mmap (highest speed) (30%)
Modify the mmap version to produce the highest clock frequency square wave,
capture a screen shot and record the shortest period achieved. Try to get the best oscilloscope trace of the
output. If it doesn't look like a square wave, explain why.
