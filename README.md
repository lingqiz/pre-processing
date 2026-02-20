## Pre-processing and video calibration toolkit for Modulo

**Updated Workflow as of 02/19/2026**
- Generate ccf_all_params files from experiment data (script from Nishan)
- Run `./batch_processing.py` to get DCL tracking and calibration data from hs_cam
- Run `./collect/batch_collect.py` to collect data into the new_format folder (include video and trk file conversions)

## Note on Conda Environment (for cluster jobs)
A conda environment at `/groups/zhang/home/zhangl5/conda/envs/video` (Python 3.10) is used for running jobs on the Janelia cluster. It lives on the shared filesystem so both local and cluster nodes can access it.

- **Python path**: `/groups/zhang/home/zhangl5/conda/envs/video/bin/python3`
- **Conda install**: `/groups/zhang/home/zhangl5/conda`
- **Update packages**: Sync from poetry with `poetry export -f requirements.txt --without-hashes -o /tmp/req.txt && /groups/zhang/home/zhangl5/conda/envs/video/bin/pip install -r /tmp/req.txt`
- **Local development** still uses the poetry-managed `.venv`

## Train / cross-validate DLC tracker (with Janelia Cluster)
*For Janelia cluster:*
- Use `bash train.cmd index` for cross-validation training.
- Training data under `/training/im`

## Partial scripts used during development **(DEPRECATED)**

### Align videos using cross-correlation between optical flow and the zaber coordinate
*Usage example:*
`python3 run_calib.py p16p17p18 2024-05-20T12_29_48_p16 20240520_122900_hs.mp4`

*For Janelia cluster:*
- Modify `file_names.txt` to specify input files.
- Use `generate_list.py` to batch-generate the list of videos based on the corresponding all_params file.
- Run `bsub -n 32 -J video_alignment -o ./.tmp/output.log './run_calib.sh'`
- Note Python3.10 environment is located under `~/local` if python3.10 cannot be found.

### Track high-res video with DLC (with Janelia Cluster)
- Modify `track_names.txt` to specify input files.
- Run `python3 run_track.py` to launch tracking.
- Run `convert_trk.m` in MATLAB to convert trk to mat format.
