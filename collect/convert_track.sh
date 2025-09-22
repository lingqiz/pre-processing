#!/bin/bash

if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    echo "Usage: $0 <input_trk_file> [destination_mat_file]"
    exit 1
fi

input_file="$1"
input_dir=$(dirname "$input_file")
filename=$(basename "$input_file")
name="${filename%.*}"
output_file="${input_dir}/${name}.mat"

# Optional destination file for copying
dest_file="$2"

# Create a temporary MATLAB script for this specific file
temp_script="/groups/zhang/home/zhangl5/.tmp/matlab/convert_trk_${RANDOM}.m"
cat > "$temp_script" << EOF
try
    % Load .trk file
    trk_data = load('$input_file', '-mat');

    % Extract data
    points = trk_data.pTrk{:};
    conf = trk_data.pTrkConf{:};
    start_frame = trk_data.startframes;
    end_frame = trk_data.endframes;

    % Save as .mat file in original location
    save('$output_file', 'points', 'conf', 'start_frame', 'end_frame');
    fprintf('Successfully converted %s to %s\n', '$input_file', '$output_file');

    % Copy to destination if provided
    dest_file = '$dest_file';
    if ~strcmp(dest_file, '')
        copyfile('$output_file', dest_file);
        fprintf('Successfully copied to %s\n', dest_file);
    end

    exit(0);
catch ME
    fprintf('Error converting file: %s\n', ME.message);
    exit(1);
end
EOF

# Create log file path
log_file="/groups/zhang/home/zhangl5/.tmp/matlab/convert_$(basename "$input_file").log"

ssh -o "StrictHostKeyChecking no" -t login1.int.janelia.org \
  "bsub -J convert_trk -o '$log_file' -e '$log_file' -n 2 \
  \"cd $(pwd) && module load matlab && matlab -batch \\\"run('$temp_script')\\\"\""

