CFLAGS = -Wall -g `pkg-config --cflags gtk+-3.0` -lm -lpthread
LDFLAGS = `pkg-config --libs gtk+-3.0` -lgpiod -lpthread
DISPLAY = gpio_ssd.o

all: gpio_blink gpio_count 

gpio_count:	gpio_count.o $(DISPLAY)
	$(CC) -o $@ $< $(DISPLAY) $(LDFLAGS)

gpio_blink:	gpio_blink.o $(DISPLAY)
	$(CC) -o $@ $< $(DISPLAY) $(LDFLAGS)

copyto:
	scp -P 10022 -r ../lab1 elec3607@localhost:lab1/

copyfrom:
	scp -P 10022 -r elec3607@localhost:lab1/'*.c' .

ssh:
	ssh -Y elec3607@localhost -p 10022

# Define a pattern rule that compiles every .c file into a .o file
%.o : %.c
		$(CC) -c $(CFLAGS) $(CPPFLAGS) $< -o $@

clean:
	rm -f *~
	rm -f *.o
	rm -rf ssd ssd.dSYM gpio_blink gpio_count lab1 gpio_ssd
