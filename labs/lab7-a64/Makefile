CC=gcc 
CFLAGS= -march=aarch64 -g
OBJS=	main.o printdec.o

printdec:	main.o printdec.s
	$(AS) -o printdec.o printdec.s
	$(CC) -o $@ $(OBJS)

# Define a pattern rule that compiles a .c file into a .s file
%.s : %.c
		$(CC) -S $(CFLAGS) $(CPPFLAGS) $< 

clean:
	-rm -f $(OBJS) printdec
