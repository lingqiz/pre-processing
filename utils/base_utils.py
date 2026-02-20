from datetime import datetime
import os
import matplotlib.pyplot as plt
import pandas as pd

def parse_filename(filename):
    """
    Parse filename to extract animal name and datetime
    Expected format: 2025-07-01T09_19_25_p34_ccf_all_params_file.csv
    """
    # Remove .csv extension
    base_name = filename.replace('.csv', '')
    
    # Remove the suffix '_ccf_all_params_file'
    base_name = base_name.replace('_ccf_all_params_file', '')
    
    # Split by underscore to separate datetime and animal name
    parts = base_name.split('_')
    
    # The datetime part is the first 3 parts: 2025-07-01T09_19_25
    datetime_str = '_'.join(parts[:3])
    
    # The animal name is the last part
    animal_name = parts[-1]
    
    return animal_name, datetime_str

def parse_datetime(datetime_str):
    """
    Parse the datetime string
    Convert format from 2025-07-01T09_19_25 to datetime object
    """
    # Replace underscores with colons for time part
    formatted_str = datetime_str.replace('_', ':')
    dt = datetime.fromisoformat(formatted_str)
    
    return dt

def extract_hs_timestamp(video_file):
    """
    Extract timestamp from hs video filename
    Expected format: 20250701_091925_hs.mp4
    """
    import os
    basename = os.path.basename(video_file)
    # Extract timestamp from 20250701_091925_hs.mp4 format
    parts = basename.replace('_hs.mp4', '').split('_')
    if len(parts) >= 2:
        date_part = parts[0]  # 20250701
        time_part = parts[1]  # 091925
        # Convert to ISO format: 2025-07-01T09:19:25
        formatted_date = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]}"
        formatted_time = f"{time_part[:2]}:{time_part[2:4]}:{time_part[4:6]}"
        return f"{formatted_date}T{formatted_time}"
    raise ValueError("Invalid hs video filename format")

def find_closest_video(video_files, target_time, timestamp_extractor):
    """
    Find the video file with timestamp closest to target_time
    timestamp_extractor: function that takes filename and returns timestamp string
    """
    closest_video = None
    min_time_diff = None
    
    for video_file in video_files:
        try:
            timestamp_str = timestamp_extractor(video_file)
            # Convert timestamp to datetime object
            video_time = datetime.fromisoformat(timestamp_str.replace('_', ':'))
            time_diff = abs((video_time - target_time).total_seconds())
            
            if min_time_diff is None or time_diff < min_time_diff:
                min_time_diff = time_diff
                closest_video = video_file
        except ValueError:
            continue
    
    return closest_video, min_time_diff

def run_calibration(base_path, csv_filename, hs_name,
                    n_point=60, window=45):
    """Run calibration: initial estimate locally, anchor points on cluster via bsub."""
    import subprocess
    from flow.calibrate import calib_video_init
    from flow.constants import ZABER_BASE, HS_BASE, TMP_PATH

    LOGIN_NODE = "login1.int.janelia.org"
    SCRIPT_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'flow', 'run_calib_cluster.py')

    try:
        # Construct paths
        zaber_full = os.path.join(base_path, csv_filename)
        zaber_path = os.path.join(ZABER_BASE, zaber_full)
        video_path = os.path.join(HS_BASE, hs_name)

        print(f'Calibrating {hs_name} with {zaber_full}')

        # Check if files exist
        if not os.path.exists(zaber_path):
            print(f"Warning: Zaber file not found: {zaber_path}")
            return
        if not os.path.exists(video_path):
            print(f"Warning: Video file not found: {video_path}")
            return

        # Phase 1: run initial estimate locally
        result = calib_video_init(zaber_path, video_path, window)
        if result is None:
            print("Calibration failed - initial estimate returned None")
            return

        init_lag, init_window, t_max = result

        # Phase 2: submit anchor-point calibration to cluster
        job_name = hs_name[:-4] + '_calib'
        log_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '..', '.tmp')
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.abspath(os.path.join(log_dir, f'{job_name}.log'))

        python_cmd = (
            f"python {SCRIPT_PATH} "
            f'"{zaber_path}" "{video_path}" "{hs_name}" '
            f"{init_lag} {init_window} {t_max} {n_point} {window}"
        )

        bsub_cmd = (
            f"bsub -J {job_name} "
            f"-o {log_path} -n 4 "
            f"'{python_cmd}'"
        )

        ssh_result = subprocess.run(
            ["ssh", "-o", "StrictHostKeyChecking no", "-t",
             LOGIN_NODE, bsub_cmd],
            capture_output=True, text=True,
        )

        if ssh_result.returncode != 0:
            print(f"ERROR submitting calibration job: {ssh_result.stderr.strip()}")
        else:
            print(f"Submitted calibration job: {job_name}")
            print(f"  Log: {log_path}")

    except Exception as e:
        print(f"Error during calibration: {e}")