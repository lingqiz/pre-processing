TRAIN_NAME=$1

ssh -o "StrictHostKeyChecking no" -t login1.int.janelia.org "
    :;
    \"/groups/zhang/home/zhangl5/APT/matlab/repo_snapshot.sh\" \"/groups/zhang/home/zhangl5/APT\" > \
    \"/groups/zhang/home/zhangl5/.apt/tp83bd26ed_bd19_4a57_af43_eedc4e8314b0/Tracking1219/20250202T134614_20250202T134617.aptsnapshot\";

    bsub -n 24 -gpu \"num=1\" -q gpu_h100 \
         -o \"/groups/zhang/home/zhangl5/Emily/Video_Process/.apt/train/train_${TRAIN_NAME}.log\" \
         -R \"affinity[core(1)]\" \
         -J train_${TRAIN_NAME} \
         \"singularity exec --nv \
              -B \\\"/groups\\\" -B \\\"/nrs\\\"  \
              \\\"/groups/branson/bransonlab/apt/sif/apt_20230427_tf211_pytorch113_ampere.sif\\\" \
              bash -c \\\"
                  TORCH_HOME='/groups/zhang/home/zhangl5/.apt/torch' \
                  python '/groups/zhang/home/zhangl5/APT/deepnet/APT_interface.py' \
                  '/groups/zhang/home/zhangl5/Emily/Video_Process/training/train_config.json' \
                  -name train_${TRAIN_NAME} \
                  -err_file '/groups/zhang/home/zhangl5/Emily/Video_Process/.apt/train/train_${TRAIN_NAME}.err' \
                  -json_trn_file '/groups/zhang/home/zhangl5/Emily/Video_Process/training/labels.json' \
                  -conf_params \
                  -type deeplabcut \
                  -ignore_local 1 \
                  -cache '/groups/zhang/home/zhangl5/Emily/Video_Process/.apt/train/train_${TRAIN_NAME}' \
                  train -use_cache
              \\\"\"
"
