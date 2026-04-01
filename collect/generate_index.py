#!/usr/bin/env python3
"""
Walk the new_format directory and generate a zaber-to-HS-video frame mapping CSV
for every session that contains a calibration file.

Usage:
    python generate_index.py
"""

import os
import glob
import numpy as np
import pandas as pd
import cv2


NEW_FORMAT_BASE = '/groups/dennis/dennislab/data/new_format'
HS_FRAME_RATE = 120


def generate_hs_mapping(csv_path, calib_path, hs_video_path, output_path):
    """
    Generate a CSV mapping each zaber index to a high-speed video frame index.

    Uses nearest-neighbor interpolation from sparse calibration anchors to map
    the behavioral timeline onto HS video frames.  Frames that fall outside
    the HS video range are marked as -1.

    Parameters
    ----------
    csv_path : str
        Path to the behavioral CSV (must contain 'relative_time' column).
    calib_path : str
        Path to the calibration CSV (must contain 'video_index' and 'zaber_index').
    hs_video_path : str
        Path to the HS video file (used to determine total frame count).
    output_path : str
        Path for the output CSV file.
    """
    time_array = pd.read_csv(csv_path, low_memory=False)['relative_time'].to_numpy()

    calib_array = pd.read_csv(calib_path)
    calib_axis = calib_array[['video_index', 'zaber_index']].to_numpy().T
    zaber_axis = calib_axis[1]
    video_axis = calib_axis[0]

    # get total frame count from the HS video
    cap = cv2.VideoCapture(hs_video_path)
    hs_length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    hs_index = np.zeros(time_array.size, dtype=int)
    for idx in range(time_array.size):
        # find the closest anchor in zaber_axis
        zaber_idx = np.argmin(np.abs(zaber_axis - idx))
        zaber_frame = zaber_axis[zaber_idx]
        video_frame = video_axis[zaber_idx]

        delta = (time_array[idx] - time_array[int(zaber_frame)]) * HS_FRAME_RATE
        frame_idx = int(video_frame + delta)

        # mark out-of-range frames as -1
        if frame_idx < 0 or frame_idx >= hs_length:
            hs_index[idx] = -1
        else:
            hs_index[idx] = frame_idx

    df = pd.DataFrame({'zaber_index': np.arange(time_array.size), 'hs_index': hs_index})
    df.to_csv(output_path, index=False)
    return hs_index


def find_file(session_dir, suffix):
    """Find a file in the session directory by suffix."""
    for f in os.listdir(session_dir):
        if f.endswith(suffix):
            return os.path.join(session_dir, f)
    return None


def process_session(session_dir):
    """Process a single session directory."""
    calib_path = find_file(session_dir, '_calib.csv')
    if calib_path is None:
        return

    csv_path = find_file(session_dir, '_ccf_all_params_file.csv')
    if csv_path is None:
        print(f"  Skipping {session_dir}: no behavioral CSV")
        return

    hs_video_path = find_file(session_dir, '_hs_cmp.avi')
    if hs_video_path is None:
        print(f"  Skipping {session_dir}: no HS video")
        return

    # output file: same prefix as calib file, with _hs_index.csv
    prefix = os.path.basename(calib_path).replace('_calib.csv', '')
    output_path = os.path.join(session_dir, f'{prefix}_hs_index.csv')

    if os.path.exists(output_path):
        print(f"  Already exists: {output_path}")
        return

    try:
        hs_index = generate_hs_mapping(csv_path, calib_path, hs_video_path, output_path)
        n_valid = np.sum(hs_index >= 0)
        n_total = hs_index.size
        print(f"  Generated: {os.path.basename(output_path)} "
              f"({n_valid}/{n_total} valid frames)")
    except Exception as e:
        print(f"  Error processing {session_dir}: {e}")


def main():
    animal_dirs = sorted(glob.glob(os.path.join(NEW_FORMAT_BASE, '*')))

    for animal_dir in animal_dirs:
        if not os.path.isdir(animal_dir):
            continue

        animal_name = os.path.basename(animal_dir)
        session_dirs = sorted(glob.glob(os.path.join(animal_dir, '*')))

        for session_dir in session_dirs:
            if not os.path.isdir(session_dir):
                continue

            print(f"Processing {animal_name}/{os.path.basename(session_dir)}")
            process_session(session_dir)


if __name__ == '__main__':
    main()
