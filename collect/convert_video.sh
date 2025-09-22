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

output=$(ssh -o "StrictHostKeyChecking no" -t login1.int.janelia.org \
  "bsub -J convert_mov -o /dev/null -n 8 'ffmpeg -i \"$input_file\" \
    -vf \"normalize=smoothing=60:strength=0.8,format=gray\" \
    -pix_fmt yuv420p \
    -c:v libx264 -crf 26 -preset medium -movflags +faststart -an \
    \"$output_file\"'" 2>&1)

echo "Submitted job to cluster for converting $filename"

