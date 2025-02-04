VIDEO_INDEX=$1
DEEP_NET_NAME=$2

ssh -o "StrictHostKeyChecking no" -t login1.int.janelia.org \
    "bsub -n 8 -gpu \"num=1\" -q gpu_a100 -o \"/groups/zhang/home/zhangl5/Emily/Video_Process/training/.temp/track_${VIDEO_INDEX}.log\" \
    -R\"affinity[core(1)]\" -J DLC_Track_${VIDEO_INDEX} \
    \"singularity exec --nv -B \\\"/groups\\\" -B \\\"/nrs\\\"  \\\"/groups/branson/bransonlab/apt/sif/apt_20230427_tf211_pytorch113_ampere.sif\\\" \
    bash -c \\\"TORCH_HOME='/groups/zhang/home/zhangl5/.apt/torch' python '/groups/zhang/home/zhangl5/APT/deepnet/APT_interface.py' \
    '/groups/zhang/home/zhangl5/Emily/apt_config.json' -name track_${VIDEO_INDEX} \
    -err_file '/groups/zhang/home/zhangl5/Emily/Video_Process/training/.temp/track_${VIDEO_INDEX}.err' \
    -type deeplabcut -model_files '/groups/zhang/home/zhangl5/Emily/Video_Process/.apt/train/train_${VIDEO_INDEX}/${DEEP_NET_NAME}' \
    -ignore_local 1 -cache '/groups/zhang/home/zhangl5/.apt/apt_tracking_temp_files' track \
    -config_file '/groups/zhang/home/zhangl5/Emily/Video_Process/tracking/apt_config.json' \
    -out '/groups/zhang/home/zhangl5/Emily/Video_Process/training/.temp/out_${VIDEO_INDEX}.trk' \
    -mov '/groups/zhang/home/zhangl5/Emily/Video_Process/training/.temp/val_${VIDEO_INDEX}.mp4'\\\"\""

printf "\n"