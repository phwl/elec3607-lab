WSPRFILE=	ALL_WSPR.TXT
IQFILE=		data/iq-16b.wav

wspr:
	(cd wsprcan; make)
	sox $(IQFILE) -c 1 -t wav -r 12000 -b 16 mono.wav
	wsprcan/k9an-wsprd mono.wav
	-rm mono.wav

qemu-run:
	qemu-system-aarch64 -M virt -cpu cortex-a53 -m 1G -initrd initrd.img-5.10.0-11-arm64 -kernel vmlinuz-5.10.0-11-arm64 -append "root=/dev/vda2 console=ttyAMA0" -drive if=virtio,file=debian-3607-aarch64-lab1.qcow2,format=qcow2,id=hd -net user,hostfwd=tcp::10022-:22 -net nic -device intel-hda -device hda-duplex -nographic

run:
	(cd pa-wsprcan; make)
	bash wsprwait | tee -a wsprwait.out

clean:
	(cd parecfile; make clean)
	(cd wsprcan; make clean)
	-rm -f ALL_WSPR.TXT data/wf*.wav wspr_spots.txt wspr_timer.out wsprwait.out
