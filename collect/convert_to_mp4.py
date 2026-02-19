#!/usr/bin/env python3
"""Convert YYMMDD_HHMMSS_video.avi files to YYYYMMDD_HHMMSS_hs.mp4 using ffmpeg."""

import glob
import os
import subprocess
import sys

INPUT_DIR = "/groups/dennis/dennislab/data/hs_cam"
PATTERN = os.path.join(INPUT_DIR, "*_video.avi")


def convert(avi_path):
    basename = os.path.basename(avi_path)  # e.g. 230823_120011_video.avi
    parts = basename.split("_")            # ['230823', '120011', 'video.avi']
    date_str = "20" + parts[0]             # 230823 -> 20230823
    time_str = parts[1]                    # 120011
    mp4_name = f"{date_str}_{time_str}_hs.mp4"
    mp4_path = os.path.join(INPUT_DIR, mp4_name)

    if os.path.exists(mp4_path):
        print(f"SKIP (exists): {mp4_name}")
        return

    print(f"Converting: {basename} -> {mp4_name}")
    cmd = [
        "ffmpeg", "-i", avi_path,
        "-c:v", "libx264", "-crf", "18", "-preset", "medium",
        "-pix_fmt", "yuv420p",
        "-y", mp4_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: {basename}\n{result.stderr[-500:]}")
    else:
        avi_size = os.path.getsize(avi_path) / (1024**3)
        mp4_size = os.path.getsize(mp4_path) / (1024**3)
        print(f"DONE: {mp4_name} ({avi_size:.1f}G -> {mp4_size:.1f}G)")


def main():
    files = sorted(glob.glob(PATTERN))
    print(f"Found {len(files)} AVI files to convert\n")
    for i, f in enumerate(files, 1):
        print(f"[{i}/{len(files)}]", end=" ")
        convert(f)
    print("\nAll done.")


if __name__ == "__main__":
    main()
