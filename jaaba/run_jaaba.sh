#!/bin/bash

if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    echo "Usage: $0 <expdir> [classifier_config.json]"
    exit 1
fi

expdir="$1"
# Classifier config: each entry maps a .jab file to the score file it should write.
config="${2:-$(dirname "$(readlink -f "$0")")/classifiers.json}"

if [ ! -f "$config" ]; then
    echo "Error: classifier config not found: $config"
    exit 1
fi

folder_name=$(basename "$expdir")
# Replace hyphens with underscores so MATLAB doesn't parse them as minus
safe_name="${folder_name//-/_}"

# Create a temporary MATLAB script for this specific expdir
temp_script="/groups/zhang/home/zhangl5/.tmp/matlab/jaaba_${safe_name}.m"
log_file="/groups/zhang/home/zhangl5/.tmp/matlab/jaaba_${safe_name}.log"
# Per-session scratch for the derived jabs (jab + overridden scorefilename)
derived_dir="/groups/zhang/home/zhangl5/.tmp/matlab/derived_jabs"

cat > "$temp_script" << EOF
try
    run('/groups/zhang/home/zhangl5/JAABA/perframe/SetUpJAABAPath.m');

    expdir = '$expdir';
    config_file = '$config';
    derived_dir = '$derived_dir';
    if ~exist(derived_dir, 'dir'); mkdir(derived_dir); end

    % Read the classifier config: which .jab to run and what score file it writes.
    cfg = jsondecode(fileread(config_file));
    C = cfg.classifiers;
    n = numel(C);

    % Build a derived .jab per classifier with the configured output name baked in.
    % The original .jab files are never modified; derived copies live in scratch.
    jabfiles = cell(1, n);
    for i = 1:n
        if iscell(C); c = C{i}; else; c = C(i); end
        x = loadAnonymous(c.jab);
        x.file.scorefilename = {c.scorefile};
        [~, base, ext] = fileparts(c.jab);
        derived = fullfile(derived_dir, sprintf('%s__c%d__%s%s', '$safe_name', i, base, ext));
        saveAnonymous(derived, x);
        jabfiles{i} = derived;
        fprintf('Derived %s -> scorefile %s\n', c.jab, c.scorefile);
    end

    JAABADetect(expdir, 'jabfiles', jabfiles(:), 'forcecompute', true);
    fprintf('Successfully ran JAABADetect on %s\n', expdir);

    % Clean up the derived jabs (deterministic names, safe to remove after the run).
    for i = 1:n
        if exist(jabfiles{i}, 'file'); delete(jabfiles{i}); end
    end
    exit(0);
catch ME
    fprintf('Error running JAABADetect: %s\n', ME.message);
    exit(1);
end
EOF

ssh -o "StrictHostKeyChecking no" -t login1.int.janelia.org \
  "bsub -J jaaba_detect -o '$log_file' -e '$log_file' -n 2 \
  \"module load matlab && matlab -batch \\\"run('$temp_script')\\\"\""
