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

# temp directory for the code and log files
temp_script="/groups/zhang/home/zhangl5/.tmp/matlab/jaaba_${safe_name}.m"
log_file="/groups/zhang/home/zhangl5/.tmp/matlab/jaaba_${safe_name}.log"

cat > "$temp_script" << EOF
try
    run('/groups/zhang/home/zhangl5/JAABA/perframe/SetUpJAABAPath.m');

    expdir = '$expdir';
    config_file = '$config';

    % Set safe temp directory for the parpool workers
    jobid = getenv('LSB_JOBID');
    if isempty(jobid); jobid = 'nojob'; end
    scratch_base = fullfile('/scratch/zhangl5', sprintf('%s_%s', '$safe_name', jobid));
    [ok, ~] = mkdir(scratch_base);
    if ~ok
        % Node-local /scratch unavailable: fall back to the node's temp dir.
        scratch_base = fullfile(tempdir, sprintf('jaaba_%s_%s', '$safe_name', jobid));
        mkdir(scratch_base);
    end
    temp_jabs_dir = fullfile(scratch_base, 'temp_jabs'); mkdir(temp_jabs_dir);
    pool_dir = fullfile(scratch_base, 'matlab_pool'); mkdir(pool_dir);
    fprintf('Scratch: %s\n', scratch_base);

    pc = parcluster('Processes');
    pc.JobStorageLocation = pool_dir;
    parpool(pc);   % JAABADetect reuses this pre-started, isolated pool

    % Read the classifier config: which .jab to run and what score file it writes.
    cfg = jsondecode(fileread(config_file));
    C = cfg.classifiers;
    n = numel(C);

    % Build a temp .jab per classifier with the configured output name baked in.
    % The original .jab files are never modified; temp copies live in scratch.
    jabfiles = cell(1, n);
    for i = 1:n
        if iscell(C); c = C{i}; else; c = C(i); end
        x = loadAnonymous(c.jab);
        x.file.scorefilename = {c.scorefile};
        [~, base, ext] = fileparts(c.jab);
        temp_jab = fullfile(temp_jabs_dir, sprintf('c%d__%s%s', i, base, ext));
        saveAnonymous(temp_jab, x);
        jabfiles{i} = temp_jab;
        fprintf('Temp jab %s -> scorefile %s\n', c.jab, c.scorefile);
    end

    JAABADetect(expdir, 'jabfiles', jabfiles(:), 'forcecompute', true);
    fprintf('Successfully ran JAABADetect on %s\n', expdir);

    % Tear down the pool, then remove all of this job's scratch in one go
    % (covers both temp_jabs and the pool storage).
    delete(gcp('nocreate'));
    if exist(scratch_base, 'dir'); rmdir(scratch_base, 's'); end
    exit(0);
catch ME
    fprintf('Error running JAABADetect: %s\n', ME.message);
    delete(gcp('nocreate'));
    if exist('scratch_base', 'var') && exist(scratch_base, 'dir'); rmdir(scratch_base, 's'); end
    exit(1);
end
EOF

ssh -o "StrictHostKeyChecking no" -n login1.int.janelia.org \
  "bsub -J jaaba_detect -o '$log_file' -e '$log_file' -n 2 \
  \"module load matlab && matlab -batch \\\"run('$temp_script')\\\"\""
