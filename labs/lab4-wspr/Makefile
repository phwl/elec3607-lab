WSPRFILE=	ALL_WSPR.TXT
IQFILE=		data/iq-16b.wav

wspr:
	(cd wsprcan; make)
	sox $(IQFILE) -c 1 -t wav -r 12000 -b 16 mono.wav
	wsprcan/k9an-wsprd mono.wav
	-rm mono.wav

run:
	(cd wsprcan; make)
	bash wsprwait | tee -a wsprwait.out

clean:
	(cd parecfile; make clean)
	(cd wsprcan; make clean)
	-rm -f ALL_WSPR.TXT data/wf*.wav wspr_spots.txt wspr_timer.out wsprwait.out
