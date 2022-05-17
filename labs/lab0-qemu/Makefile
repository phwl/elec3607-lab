TAG=elec3607-base
WDIR= $(shell pwd)

qemu-run:
	qemu-system-aarch64 -M virt -cpu cortex-a53 -m 1G -initrd initrd.img -kernel vmlinuz -append "root=/dev/vda2 console=ttyAMA0" -drive if=virtio,file=debian-3607-aarch64-lab1.qcow2,format=qcow2,id=hd -net user,hostfwd=tcp::10022-:22 -net nic -device intel-hda -device hda-duplex -nographic

build:
	docker build  --platform linux/amd64 . -t phwl/$(TAG)

run:
	docker run --platform linux/amd64 -it -v $(WDIR):/mnt phwl/$(TAG):latest

