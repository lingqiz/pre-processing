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

def run_calibration(base_path, csv_filename, hs_name):
    """Run calibration using the found video and CSV file"""
    from flow.calibrate import calib_video
    from flow.constants import ZABER_BASE, HS_BASE, TMP_PATH
    
    try:
        # Construct paths similar to run_calib.py
        zaber_full = os.path.join(base_path, csv_filename)
        zaber_path = os.path.join(ZABER_BASE, zaber_full)
        video_path = os.path.join(HS_BASE, hs_name)
        output_path = os.path.join(HS_BASE, hs_name[:-4] + '_calib.csv')
        
        print(f'Calibrating {hs_name} with {zaber_full}')
        
        # Check if zaber file exists
        if not os.path.exists(zaber_path):
            print(f"Warning: Zaber file not found: {zaber_path}")
            return
            
        # Check if video file exists
        if not os.path.exists(video_path):
            print(f"Warning: Video file not found: {video_path}")
            return
        
        # Run calibration
        result = calib_video(zaber_path, video_path, pbar=True)
        if result is not None:
            t0, calibration = result
            
            # Create .tmp directory if it doesn't exist
            os.makedirs(TMP_PATH, exist_ok=True)
            
            # Plot calibration results
            fig, axs = plt.subplots(1, 2, figsize=(12, 5))
            
            # lag
            axs[0].plot(t0, calibration[0], 'o-')
            axs[0].set_xlabel('t0 (s)')
            axs[0].set_ylabel('Lag (s)')
            
            # correlation r value
            axs[1].plot(t0, calibration[3], 'o-')
            axs[1].set_xlabel('t0 (s)')
            axs[1].set_ylabel('Correlation')
            
            # save plot
            fig_path = os.path.join(TMP_PATH, hs_name[:-4] + '_calib.png')
            plt.tight_layout()
            plt.savefig(fig_path)
            plt.close(fig)
            print(f'Saved calibration plot to {fig_path}')
            
            # save calibration (write to csv file)
            header = ['lag', 'video_index', 'zaber_index', 'correlation']
            df = pd.DataFrame({h: calibration[i] for i, h in enumerate(header)})
            df.to_csv(output_path, index=False)
            print(f'Saved calibration data to {output_path}')
        else:
            print("Calibration failed - no result returned")
            
    except Exception as e:
        print(f"Error during calibration: {e}")