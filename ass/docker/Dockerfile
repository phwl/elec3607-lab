FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    build-essential \
    libpulse-dev \
    libfftw3-dev \
    pulseaudio \
    wsjtx \
    sox \
    faketime

RUN adduser root pulse-access
COPY entrypoint.sh /usr/bin/entrypoint.sh