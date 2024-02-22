#!/bin/bash
#####################################################################
# Data Download Instructions:
#     1. Go to http://na5b.com:8901/ in a browser
#     2. Open developer console
#     3. Run the code from run.js    
#####################################################################

script=$(realpath "$0")
scriptpath=$(dirname "$script")
outputpath="$scriptpath/output"
in_files=$(ls $scriptpath/*.wav)

rm -rf $outputpath
mkdir $outputpath
cd $outputpath

for in_file in $in_files
do
    filename=$(basename -- $in_file)
    filename="${filename%%.*}"
    echo "Processing $in_file"
    mkdir $filename
    cd $filename
    sox $in_file -c 1 -t wav -r 12000 -b 16 mono.wav
    wsprd mono.wav
    mv ALL_WSPR.txt "$scriptpath/$filename-ALL_WSPR.txt"
    # sed 's/.....$//' < hashtable.txt > "$scriptpath/$filename-hashtable.txt"
    cd $outputpath
done

cd $scriptpath
rm -rf $outputpath