#!/usr/bin/env python3
"""Convert YYMMDD_HHMMSS_video.avi files to YYYYMMDD_HHMMSS_hs.mp4.

Submits each ffmpeg conversion as a separate bsub job on the cluster.
"""

import glob
import os
import subprocess
import sys

INPUT_DIR = "/groups/dennis/dennislab/data/hs_cam"
PATTERN = os.path.join(INPUT_DIR, "*_video.avi")
LOGIN_NODE = "login1.int.janelia.org"


def submit_job(avi_path):
    basename = os.path.basename(avi_path)  # e.g. 230823_120011_video.avi
    parts = basename.split("_")            # ['230823', '120011', 'video.avi']
    date_str = "20" + parts[0]             # 230823 -> 20230823
    time_str = parts[1]                    # 120011
    mp4_name = f"{date_str}_{time_str}_hs.mp4"
    mp4_path = os.path.join(INPUT_DIR, mp4_name)

    ffmpeg_cmd = (
        f'ffmpeg -i "{avi_path}" '
        f'-vf "hflip,vflip" '
        f'-c:v libx264 -crf 18 -preset medium '
        f'-pix_fmt yuv420p '
        f'-y "{mp4_path}"'
    )

    bsub_cmd = (
        f"bsub -J convert_{date_str}_{time_str} "
        f"-o /dev/null -n 4 "
        f"'{ffmpeg_cmd}'"
    )

    result = subprocess.run(
        ["ssh", "-o", "StrictHostKeyChecking no", "-t", LOGIN_NODE, bsub_cmd],
        capture_output=True, text=True,
    )

    if result.returncode != 0:
        print(f"ERROR submitting {basename}: {result.stderr.strip()}")
    else:
        print(f"Submitted: {basename} -> {mp4_name}")


def main():
    files = sorted(glob.glob(PATTERN))
    print(f"Found {len(files)} AVI files to process\n")
    for i, f in enumerate(files, 1):
        print(f"[{i}/{len(files)}]", end=" ")
        submit_job(f)
    print("\nAll jobs submitted.")


if __name__ == "__main__":
    main()
