#!/bin/bash
# Step 4 — Convert .temp/out_${i}.trk to .temp/out_${i}.mat
#
# Usage:
#   bash convert.sh               # convert all 5 folds
#   bash convert.sh 0 3           # convert only folds 0 and 3
#
# Reads each .trk (which is a MAT-format file) and writes a .mat with fields
# `points`, `conf`, `start_frame`, `end_frame` — the format pose.load_pred()
# expects.
#
# Submits a single bsub MATLAB job that loops over the requested folds (each
# conversion is seconds, so one job is plenty).

set -e

PROJ_ROOT="/groups/zhang/home/zhangl5/Emily/Video_Process"
TEMP_DIR="${PROJ_ROOT}/training/.temp"
TMP_M="/groups/zhang/home/zhangl5/.tmp/matlab"
mkdir -p "${TMP_M}"

FOLDS=("$@")
if [ ${#FOLDS[@]} -eq 0 ]; then
    FOLDS=(0 1 2 3 4)
fi

STAMP="$(date +%Y%m%d-%H%M%S)"
MFILE="${TMP_M}/cv_convert_${STAMP}.m"
LOG="${TMP_M}/cv_convert_${STAMP}.log"

# Build a MATLAB script with one conversion block per fold.
{
    echo "try"
    for i in "${FOLDS[@]}"; do
        TRK="${TEMP_DIR}/out_${i}.trk"
        MAT="${TEMP_DIR}/out_${i}.mat"
        cat <<EOF
    trk = load('${TRK}', '-mat');
    points = trk.pTrk{:};
    conf = trk.pTrkConf{:};
    start_frame = trk.startframes;
    end_frame = trk.endframes;
    save('${MAT}', 'points', 'conf', 'start_frame', 'end_frame');
    fprintf('converted ${TRK} -> ${MAT}\n');
EOF
    done
    echo "    exit(0);"
    echo "catch ME"
    echo "    fprintf('Error: %s\n', ME.message);"
    echo "    exit(1);"
    echo "end"
} > "${MFILE}"

echo "submitting MATLAB conversion job (folds: ${FOLDS[*]})"
ssh -o "StrictHostKeyChecking no" -t login1.int.janelia.org \
  "bsub -J cv_convert -o '${LOG}' -e '${LOG}' -n 4 \
  \"module load matlab && matlab -batch \\\"run('${MFILE}')\\\"\""

echo "log: ${LOG}"
