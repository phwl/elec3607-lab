CC=gcc

CFLAGS= -I. -I/usr/local/include -Wall -Wextra -std=c99 -pedantic -O3 -ffast-math
LDFLAGS= -L/usr/local/lib
LIBS= /usr/lib/libfftw3.so.3.6.10 /usr/lib/libfftw3_threads.so.3.6.10 -lm -lpulse-simple -lpulse

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

all:    k9an-wsprd wsprsim

DEPS =  wsprsim_utils.h wsprd_utils.h fano.h jelinek.h

OBJS2 = wsprsim.o wsprsim_utils.o wsprd_utils.o tab.o fano.o nhash.o
wsprsim: $(OBJS2)
	$(CC) -o $@ $^ $(CFLAGS) $(LDFLAGS) $(LIBS)

OBJS3 = wsprd.o wsprsim_utils.o wsprd_utils.o tab.o fano.o jelinek.o nhash.o
k9an-wsprd: $(OBJS3)
	$(CC) -o $@ $^ $(CFLAGS) $(LDFLAGS) $(LIBS)

clean:
	-rm *.o k9an-wsprd wsprsim
