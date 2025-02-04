VIDEO_NAME=$1
echo "Tracking video: ${VIDEO_NAME}"

ssh -o "StrictHostKeyChecking no" -t login1.int.janelia.org \
    "bsub -n 8 -gpu \"num=1\" -q gpu_a100 -o \"/groups/zhang/home/zhangl5/Emily/Video_Process/.apt/track/track_${VIDEO_NAME}.log\" \
    -R\"affinity[core(1)]\" -J DLC_Track_${VIDEO_NAME} \
    \"singularity exec --nv -B \\\"/groups\\\" -B \\\"/nrs\\\"  \\\"/groups/branson/bransonlab/apt/sif/apt_20230427_tf211_pytorch113_ampere.sif\\\" \
    bash -c \\\"TORCH_HOME='/groups/zhang/home/zhangl5/.apt/torch' python '/groups/zhang/home/zhangl5/APT/deepnet/APT_interface.py' \
    '/groups/zhang/home/zhangl5/Emily/apt_config.json' -name ${VIDEO_NAME} \
    -err_file '/groups/zhang/home/zhangl5/Emily/Video_Process/.apt/track/track_${VIDEO_NAME}.err' \
    -type deeplabcut -model_files '/groups/zhang/home/zhangl5/Emily/Video_Process/tracking/0131_DLC/deepnet-673000' \
    -ignore_local 1 -cache '/groups/zhang/home/zhangl5/.apt/apt_tracking_temp_files' track \
    -config_file '/groups/zhang/home/zhangl5/Emily/Video_Process/tracking/apt_config.json' \
    -out '/groups/dennis/dennislab/data/hs_cam/${VIDEO_NAME}.trk' \
    -mov '/groups/dennis/dennislab/data/hs_cam/${VIDEO_NAME}.mp4'\\\"\""

printf "\n"