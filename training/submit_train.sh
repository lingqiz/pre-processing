#!/bin/bash
# Submit APT/DeepLabCut training bsub jobs for the cross-validation folds.
#
# Usage:
#   bash submit_train.sh                   # all 5 folds, fresh (backup old cache)
#   bash submit_train.sh 1 3               # only folds 1 and 3 (retry), fresh
#   bash submit_train.sh --no-fresh        # don't back up / clear cache first
#
# By default ("fresh" mode), each fold's existing cache dir
# ../.apt/train/train_${i}/ is renamed to train_${i}.bak.<timestamp> before
# submission, so training starts from scratch and the old checkpoints are
# preserved. Pass --no-fresh to skip the backup-and-clear and let APT reuse the
# existing cache (only correct if labels and splits haven't changed).

set -e

PROJ_ROOT="/groups/zhang/home/zhangl5/Emily/Video_Process"
APT_DIR="/groups/zhang/home/zhangl5/APT"
SIF="/groups/branson/bransonlab/apt/sif/apt_20230427_tf211_pytorch113_ampere.sif"
TRAIN_ROOT="${PROJ_ROOT}/.apt/train"

QUEUE="gpu_a100"
WALLTIME="24:00"
NCORES=12

FRESH=1
FOLDS=()
for arg in "$@"; do
    case "$arg" in
        --no-fresh) FRESH=0 ;;
        --fresh) FRESH=1 ;;
        *) FOLDS+=("$arg") ;;
    esac
done
if [ ${#FOLDS[@]} -eq 0 ]; then
    FOLDS=(0 1 2 3 4)
fi

STAMP="$(date +%Y%m%d-%H%M%S)"

for i in "${FOLDS[@]}"; do
    TRAIN_DIR="${TRAIN_ROOT}/train_${i}"
    LOG="${TRAIN_ROOT}/train_${i}.log"
    ERR="${TRAIN_ROOT}/train_${i}.err"
    SNAP="${TRAIN_ROOT}/train_${i}.aptsnapshot"

    if [ "${FRESH}" -eq 1 ] && [ -d "${TRAIN_DIR}" ]; then
        BACKUP="${TRAIN_DIR}.bak.${STAMP}"
        echo "backing up ${TRAIN_DIR} -> ${BACKUP}"
        mv "${TRAIN_DIR}" "${BACKUP}"
    fi
    mkdir -p "${TRAIN_DIR}"

    echo "submitting fold ${i}..."

    ssh -o "StrictHostKeyChecking no" -t login1.int.janelia.org "
        \"${APT_DIR}/matlab/repo_snapshot.sh\" \"${APT_DIR}\" > \"${SNAP}\";

        bsub -n ${NCORES} -gpu \"num=1\" -q ${QUEUE} -W ${WALLTIME} \
             -o \"${LOG}\" \
             -R \"affinity[core(1)]\" \
             -J train_${i} \
             \"singularity exec --nv \
                  -B \\\"/groups\\\" -B \\\"/nrs\\\"  \
                  \\\"${SIF}\\\" \
                  bash -c \\\"
                      TORCH_HOME='/groups/zhang/home/zhangl5/.apt/torch' \
                      python '${APT_DIR}/deepnet/APT_interface.py' \
                      '${PROJ_ROOT}/training/train_config.json' \
                      -name train_${i} \
                      -err_file '${ERR}' \
                      -json_trn_file '${PROJ_ROOT}/training/cv/train_${i}.json' \
                      -conf_params \
                      -type deeplabcut \
                      -ignore_local 1 \
                      -cache '${TRAIN_DIR}' \
                      train -use_cache
                  \\\"\"
    "
done

echo
echo "Submitted ${#FOLDS[@]} fold(s). Check status with: ssh login1.int.janelia.org bjobs"
