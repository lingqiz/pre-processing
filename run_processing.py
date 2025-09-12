#!/usr/bin/env python3

import sys
import os
import glob
import subprocess
from base_utils import *

def main():
    if len(sys.argv) != 3:
        print("Usage: python run_processing.py <base_path> <csv_filename>")
        print("Example: python run_processing.py p34p35p36p37p38 2025-08-04T13_29_50_p36_ccf_all_params_file.csv")
        sys.exit(1)

    base_path = sys.argv[1]
    csv_filename = sys.argv[2]

    # Extract information from the filename
    try:
        animal_name, date_time = parse_filename(csv_filename)
        datetime_obj = parse_datetime(date_time)
    except Exception as e:
        print(f"Error parsing filename '{csv_filename}': {e}")
        sys.exit(1)

    # Base directory for hs_cam videos
    hs_cam_base = '/groups/dennis/dennislab/data/hs_cam'

    # Extract date from datetime for searching (YYYYMMDD format)
    date_folder = datetime_obj.strftime('%Y%m%d')

    # Look for hs video files with pattern like 20250701_*_hs.mp4
    hs_video_pattern = os.path.join(hs_cam_base, f'{date_folder}_*_hs.mp4')
    hs_video_files = glob.glob(hs_video_pattern)

    if not hs_video_files:
        print(f"No hs video files found matching pattern: {hs_video_pattern}")
        sys.exit(1)

    # Find closest hs video
    closest_hs_video, time_diff = find_closest_video(hs_video_files, datetime_obj, extract_hs_timestamp)

    if closest_hs_video:
        print(f"Closest video: {closest_hs_video}")
        print(f"Time difference: {time_diff:.1f} seconds")

        # Check for significant time mismatch
        if time_diff > 600:  # 10 minutes
            print(f"WARNING: Large time difference (>{time_diff:.1f}s). Video not found.")
        elif time_diff > 120:  # 2 minutes
            print(f"WARNING: Moderate time difference ({time_diff:.1f}s). Please verify correctness.")

        # Run tracking if time difference is acceptable (<10 minutes)
        if time_diff < 600:
            print("\n\nRunning tracking...")
            tracking_script = "./tracking/run_track.sh"
            try:
                result = subprocess.run([tracking_script, closest_hs_video],
                                       capture_output=True, text=True, check=True)
                print("Tracking submitted successfully.")
                if result.stdout:
                    print(f"Output: {result.stdout}")

            except subprocess.CalledProcessError as e:
                print(f"Error running tracking: {e}")
                if e.stdout:
                    print(f"stdout: {e.stdout}")
                if e.stderr:
                    print(f"stderr: {e.stderr}")
                sys.exit(1)
            except FileNotFoundError:
                print(f"Tracking script not found: {tracking_script}")
                sys.exit(1)

            # Run calibration
            print("Running calibration...")
            run_calibration(base_path, csv_filename, os.path.basename(closest_hs_video))

        else:
            print("Skipping tracking and calibration due to large time difference")
    else:
        print("No matching video found")
        sys.exit(1)

if __name__ == "__main__":
    main()