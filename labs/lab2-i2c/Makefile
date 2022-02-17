obj-m += i2c-stub.o
KVERSION = $(shell uname -r)
all:
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) modules
i2cread:	i2cread.o
	$(CC) -o $@ $< -li2c
si5351:	si5351.o
	$(CC) -o $@ $< -li2c
clean:
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) clean
