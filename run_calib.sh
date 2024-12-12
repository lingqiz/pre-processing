#!/bin/bash

# Check and create the directory if it doesn't exist
tmp_path="./.tmp"
[ -d "$tmp_path" ] || mkdir -p "$tmp_path"

echo "Job start: $(date)"

# Specify the file to read
input_file="file_names.txt"

# Read the file line by line
while IFS= read -r line; do
    command="poetry run python3 run_calib.py $line"
    eval "$command"
done < "$input_file"

echo "Job end: $(date)"