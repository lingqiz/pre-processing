#!/bin/bash

# Specify the file to read
input_file="file_names.txt"

# Read the file line by line
while IFS= read -r line; do
    poetry run python3 "$line"            # Use the line as an argument to the command
done < "$input_file"