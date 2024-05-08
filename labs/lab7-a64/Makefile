CC=gcc
CFLAGS=
OBJS=	main.o printdec.o

printdec:	main.o
	$(CC) -S $(CFLAGS) printdec.c
	$(AS) -o printdec.o printdec.s
	$(CC) -o $@ $(OBJS)

clean:
	-rm -f $(OBJS) printdec.s printdec
