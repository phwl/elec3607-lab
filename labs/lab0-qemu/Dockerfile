FROM --platform=linux/arm64 debian:bullseye-slim

# install x86 development tools
RUN apt update && apt install -y \
    bash vim make \
    gcc-aarch64-linux-gnu binutils-aarch64-linux-gnu

RUN apt install -y \
    qemu-system-aarch64
