#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: $0 <expdir>"
    exit 1
fi

expdir="$1"
folder_name=$(basename "$expdir")

# Create a temporary MATLAB script for this specific expdir
temp_script="/groups/zhang/home/zhangl5/.tmp/matlab/jaaba_${folder_name}.m"
log_file="/groups/zhang/home/zhangl5/.tmp/matlab/jaaba_${folder_name}.log"

cat > "$temp_script" << EOF
try
    run('/groups/zhang/home/zhangl5/JAABA/perframe/SetUpJAABAPath.m');

    expdir = '$expdir';
    jabfiles = {'/groups/dennis/dennislab/lingqi/03202026_Rearing.jab',
        '/groups/dennis/dennislab/lingqi/03202026_Grooming.jab'};

    JAABADetect(expdir, 'jabfiles', jabfiles, 'forcecompute', true);
    fprintf('Successfully ran JAABADetect on %s\n', expdir);
    exit(0);
catch ME
    fprintf('Error running JAABADetect: %s\n', ME.message);
    exit(1);
end
EOF

ssh -o "StrictHostKeyChecking no" -t login1.int.janelia.org \
  "bsub -J jaaba_detect -o '$log_file' -e '$log_file' -n 2 \
  \"module load matlab && matlab -batch \\\"run('$temp_script')\\\"\""
