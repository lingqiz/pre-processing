#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 <input_video_file>"
    exit 1
fi

input_file="$1"
input_dir=$(dirname "$input_file")
filename=$(basename "$input_file")
name="${filename%.*}"
output_file="${input_dir}/${name}_cmp.avi"

ssh -o "StrictHostKeyChecking no" -t login1.int.janelia.org \
    "bsub -o /dev/null -n 8 'ffmpeg -i \"$input_file\" \
      -vf \"normalize\" \
      -pix_fmt gray \
      -c:v mjpeg -q:v 3 -an \
      \"$output_file\"'"
