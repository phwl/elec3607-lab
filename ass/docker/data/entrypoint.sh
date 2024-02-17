#!/bin/bash

MAX_TIME=3m
data_path=/home/workspace/data
soln_path=/home/workspace/soln
src_path=$soln_path/src
result_path=/home/workspace/results

function setup_pulseaudio() {
    # Cleanup to be "stateless" on startup, otherwise pulseaudio daemon can't start
    rm -rf /var/run/pulse /var/lib/pulse /root/.config/pulse

    # Start pulseaudio as system wide daemon; for debugging it helps to start in non-daemon mode
    pulseaudio -D --verbose --exit-idle-time=-1 --system --disallow-exit

    # Create a virtual audio source; fixed by adding source master and format
    echo "Creating virtual audio source: ";
    pactl load-module module-virtual-source master=auto_null.monitor format=s16le source_name=VirtualMic

    # Set VirtualMic as default input source;
    echo "Setting default source: ";
    pactl set-default-source VirtualMic
}

function build_soln() {
    cd $src_path
    make k9an-wsprd
}

function get_results() {
    rm -rf $result_path
    mkdir -p $result_path
    cd $result_path
    data_files=$(ls $data_path/*.wav)
    output_path="$result_path/output"
    mkdir $output_path
    cd $output_path
    for in_file in $data_files
    do
        filename=$(basename -- $in_file)
        filename="${filename%%.*}"
        echo "Processing $in_file"
        mkdir $filename
        cd $filename
        sox $in_file -c 1 -t wav -r 12000 -b 16 mono.wav
        cp $src_path/k9an-wsprd mywsprd
        paplay mono.wav & timeout $MAX_TIME faketime "00:02:00" ./mywsprd
        mv ALL_WSPR.* "$result_path/$filename-ALL_WSPR.txt"
        # mv hashtable.txt "$result_path/$filename-hashtable.txt"
        cd $output_path
    done
    rm -rf $output_path
}

function verify_results() {
    data_files=$(ls $data_path/*.txt)
    for in_file in $data_files
    do
        filename=$(basename -- $in_file)
        echo "Validating $filename"
        input_msg_col=$(awk '{print $5}' $data_path/$filename)
        result_msg_col=$(awk '{print $7}' $result_path/$filename)
        diff -y <(awk '{print $5}' $data_path/$filename) <(awk '{print $7}' $result_path/$filename)
    done
}

setup_pulseaudio
build_soln
get_results
verify_results