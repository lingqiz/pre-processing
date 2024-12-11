### Align videos using cross-correlation between optical flow and the zaber coordinate  
Usage example: `python3 run_calib.py p16p17p18 2024-05-20T12_29_48_p16 20240520_122900_hs.mp4`

For Janelia cluster:  
Modify `file_names.txt` to specify input files, and run `bsub -n 64 -J video_alignment -o ./.tmp/output.log './run_calib.sh'`
