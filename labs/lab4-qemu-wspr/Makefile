WSPRFILE=	ALL_WSPR.TXT
IQFILE=		data/iq-16b.wav

wspr:
	(cd wsprcan; make)
	sox $(IQFILE) -c 1 -t wav -r 12000 -b 16 mono.wav
	wsprcan/k9an-wsprd mono.wav
	-rm mono.wav

clean:
	-rm -f *.o *~ $(MAIN) ALL_WSPR.TXT hashtable.txt wspr_spots.txt wspr_timer.out wspr_wisdom.dat mono.wav
	(cd wsprcan; make clean)
	(cd rec; make clean)
