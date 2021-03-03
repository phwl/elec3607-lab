TARGETS=	ssd blink PHWL-GPIO-00A0.dtbo
all:	$(TARGETS)

ssd:	ssd.o
	gcc -o ssd ssd.c -lgpiod

blink:	blink.o
	gcc -o blink blink.c -lgpiod

PHWL-GPIO-00A0.dtbo:	PHWL-GPIO.dts
	dtc -O dtb -o PHWL-GPIO-00A0.dtbo -b 0 -@ PHWL-GPIO.dts

install:	PHWL-GPIO-00A0.dtbo
	sudo cp PHWL-GPIO-00A0.dtbo /lib/firmware
	sudo cp uEnv.txt /boot

clean:	
	-rm -f *.o *.dtbo ssd blink
