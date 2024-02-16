CFLAGS =-Wall -g 
LDFLAGS = -lgpiod 

all: libgpiod_blink mmap_blink

mmap_blink:	mmap_blink.o 
	$(CC) -o $@ $< 

libgpiod_blink:	libgpiod_blink.o 
	$(CC) -o $@ $< $(LDFLAGS)

# Define a pattern rule that compiles every .c file into a .o file
%.o : %.c
		$(CC) -c $(CFLAGS) $(CPPFLAGS) $< -o $@

clean:
	rm -f *~
	rm -f *.o
	rm -rf libgpiod_blink mmap_blink
