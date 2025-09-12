### Pre-processing and video calibration toolkit for Modulo

#### Align videos using cross-correlation between optical flow and the zaber coordinate
*Usage example:*
`python3 run_calib.py p16p17p18 2024-05-20T12_29_48_p16 20240520_122900_hs.mp4`

*For Janelia cluster:*
- Modify `file_names.txt` to specify input files.   
- Use `generate_list.py` to batch-generate the list of videos based on the corresponding all_params file.   
- Run `bsub -n 32 -J video_alignment -o ./.tmp/output.log './run_calib.sh'`   
- Note Python3.10 environment is located under `~/local` if python3.10 cannot be found.   

#### Track high-res video with DLC (with Janelia Cluster)
- Modify `track_names.txt` to specify input files.   
- Run `python3 run_track.py` to launch tracking.   
- Run `convert_trk.m` in MATLAB to convert trk to mat format.

#### Train / cross-validate DLC tracker (with Janelia Cluster)
*For Janelia cluster:*
- Use `bash train.cmd index` for cross-validation training.   
- Training data under `/training/im`
