# collect experiment data into a single folder
import shutil
import os
import sys
import glob
import subprocess
import time
from datetime import timedelta
from datetime import datetime
from utils import parse_filename, parse_datetime, find_closest_video, datetime_to_filename_format

# Get filename from command line argument
all_params_base = sys.argv[1]
ref_name = sys.argv[2]

# Extract information from the filename
animal_name, date_time = parse_filename(ref_name)
datetime_obj = parse_datetime(date_time)

# Create base prefix from original filename (2024-02-22T09_46_32_p16)
base_prefix = f"{date_time}_{animal_name}"

# Base Folder
video_base = '/groups/dennis/dennislab/data/rig'
track_base = '/groups/dennis/dennislab/data/hs_cam'
new_format_base = '/groups/dennis/dennislab/data/new_format'

# 1) Check if animal name folder exists, create if not
animal_folder_path = os.path.join(new_format_base, animal_name)
if not os.path.exists(animal_folder_path):
    os.makedirs(animal_folder_path)

# 2) Create datetime folder with format p16_2024-02-22-09-46-32
# Convert datetime format from 2024-02-22T09_46_32 to 2024-02-22-09-46-32
datetime_folder_name = f"{animal_name}_{date_time.replace('T', '-').replace('_', '-')}"
datetime_folder_path = os.path.join(animal_folder_path, datetime_folder_name)

if not os.path.exists(datetime_folder_path):
    os.makedirs(datetime_folder_path)

# Copy the all_params CSV file to the datetime folder
# Construct the source path (assuming the CSV file is in the track_base directory)
csv_source_path = os.path.join(all_params_base, ref_name)
csv_dest_path = os.path.join(datetime_folder_path, ref_name)

# Copy the CSV file
csv_copied = False
try:
    shutil.copy2(csv_source_path, csv_dest_path)
    csv_copied = True
except Exception:
    pass

# Copy rig video files
# Extract date from datetime for folder name (YYYYMMDD format)
date_folder = datetime_obj.strftime('%Y%m%d')
rig_date_folder = os.path.join(video_base, date_folder)

rig_video_linked = False
hs_cam_frames_linked = False
# Find video files in the rig date folder
if os.path.exists(rig_date_folder):
    # Look for video files matching the pattern video_basler_*.avi
    video_pattern = os.path.join(rig_date_folder, 'video_basler_*.avi')
    video_files = glob.glob(video_pattern)

    if video_files:
        # Define timestamp extractor for rig videos
        def extract_rig_timestamp(video_file):
            basename = os.path.basename(video_file)
            return basename.replace('video_basler_', '').replace('.avi', '')

        # Find closest rig video
        closest_video = find_closest_video(video_files, datetime_obj, extract_rig_timestamp)

        # Create softlink to the closest video
        if closest_video:
            video_basename = os.path.basename(closest_video)

            # Extract actual timestamp from matched video
            rig_timestamp_str = extract_rig_timestamp(closest_video)
            rig_datetime = datetime.fromisoformat(rig_timestamp_str.replace('_', ':'))

            # Check for time mismatch
            time_diff = abs((rig_datetime - datetime_obj).total_seconds())
            if time_diff > 600:  # 10 minutes
                print(f"❌ ERROR: Rig video timestamp mismatch > 10 mins: {time_diff:.1f}s - treating as not found")
                closest_video = None  # Treat as not found
            elif time_diff > 120:  # 2 minutes
                print(f"⚠️  WARNING: Rig video timestamp mismatch > 120s: {time_diff:.1f}s")

            if closest_video:  # Only proceed if still valid after time check
                # Create filename with actual timestamp: 2024-02-22T09_46_32_p16_rig.avi
                rig_formatted_timestamp = datetime_to_filename_format(rig_datetime)
                rig_prefix = f"{rig_formatted_timestamp}_{animal_name}"
                rig_link_name = f"{rig_prefix}_rig.avi"
                video_link_path = os.path.join(datetime_folder_path, rig_link_name)

                # Create softlink (symbolic link)
                try:
                    if not os.path.exists(video_link_path):
                        os.symlink(closest_video, video_link_path)
                    rig_video_linked = True
                    video_basename = rig_link_name  # Update for display

                    # Submit video conversion job to cluster
                    convert_script = "./convert_video.sh"
                    subprocess.run([convert_script, video_link_path])
                except Exception:
                    pass

    # Look for hs_cam_frames CSV files
    hs_cam_frames_pattern = os.path.join(rig_date_folder, 'hs_cam_frames_*.csv')
    hs_cam_frames_files = glob.glob(hs_cam_frames_pattern)

    if hs_cam_frames_files:
        # Define timestamp extractor for hs_cam_frames files
        def extract_hs_cam_frames_timestamp(csv_file):
            basename = os.path.basename(csv_file)
            return basename.replace('hs_cam_frames_', '').replace('.csv', '')

        # Find closest hs_cam_frames file
        closest_hs_cam_frames = find_closest_video(hs_cam_frames_files, datetime_obj, extract_hs_cam_frames_timestamp)

        # Create softlink to the closest hs_cam_frames file
        if closest_hs_cam_frames:
            hs_cam_frames_basename = os.path.basename(closest_hs_cam_frames)

            # Extract actual timestamp from matched file
            frames_timestamp_str = extract_hs_cam_frames_timestamp(closest_hs_cam_frames)
            frames_datetime = datetime.fromisoformat(frames_timestamp_str.replace('_', ':'))

            # Check for time mismatch
            time_diff = abs((frames_datetime - datetime_obj).total_seconds())
            if time_diff > 600:  # 10 minutes
                print(f"❌ ERROR: HS cam frames timestamp mismatch > 10 mins: {time_diff:.1f}s - treating as not found")
                closest_hs_cam_frames = None  # Treat as not found
            elif time_diff > 120:  # 2 minutes
                print(f"⚠️  WARNING: HS cam frames timestamp mismatch > 120s: {time_diff:.1f}s")

            if closest_hs_cam_frames:  # Only proceed if still valid after time check
                # Create filename with actual timestamp: 2024-02-22T09_46_32_p16_hs_cam_frames.csv
                frames_formatted_timestamp = datetime_to_filename_format(frames_datetime)
                frames_prefix = f"{frames_formatted_timestamp}_{animal_name}"
                hs_cam_frames_link_name = f"{frames_prefix}_hs_cam_frames.csv"
                hs_cam_frames_link_path = os.path.join(datetime_folder_path, hs_cam_frames_link_name)

                # Create softlink (symbolic link)
                try:
                    if not os.path.exists(hs_cam_frames_link_path):
                        os.symlink(closest_hs_cam_frames, hs_cam_frames_link_path)
                    hs_cam_frames_linked = True
                    hs_cam_frames_basename = hs_cam_frames_link_name  # Update for display
                except Exception:
                    pass

# Find hs video files in track_base
# Look for files with pattern like 20241016_143919_hs.mp4
hs_video_pattern = os.path.join(track_base, f'{date_folder}_*_hs.mp4')
hs_video_files = glob.glob(hs_video_pattern)

hs_video_linked = False
mat_files_copied = False
trk_files_copied = False
calib_files_copied = False

closest_hs_video_name = None
if hs_video_files:
    # Define timestamp extractor for hs videos
    def extract_hs_timestamp(video_file):
        basename = os.path.basename(video_file)
        # Extract timestamp from 20241016_143919_hs.mp4 format
        parts = basename.replace('_hs.mp4', '').split('_')
        if len(parts) >= 2:
            date_part = parts[0]  # 20241016
            time_part = parts[1]  # 143919
            # Convert to ISO format: 2024-10-16T14:39:19
            formatted_date = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]}"
            formatted_time = f"{time_part[:2]}:{time_part[2:4]}:{time_part[4:6]}"
            return f"{formatted_date}T{formatted_time}"
        raise ValueError("Invalid hs video filename format")

    # Find closest hs video
    closest_hs_video = find_closest_video(hs_video_files, datetime_obj, extract_hs_timestamp)

    if closest_hs_video:
        closest_hs_video_name = os.path.basename(closest_hs_video)

        # Create symbolic link for hs video
        # Extract actual timestamp from matched video
        hs_timestamp_str = extract_hs_timestamp(closest_hs_video)
        hs_datetime = datetime.fromisoformat(hs_timestamp_str.replace('_', ':'))

        # Check for time mismatch
        time_diff = abs((hs_datetime - datetime_obj).total_seconds())
        if time_diff > 600:  # 10 minutes
            print(f"❌ ERROR: HS video timestamp mismatch > 10 mins: {time_diff:.1f}s - treating as not found")
            closest_hs_video = None  # Treat as not found
        elif time_diff > 120:  # 2 minutes
            print(f"⚠️  WARNING: HS video timestamp mismatch > 120s: {time_diff:.1f}s")

        if closest_hs_video:  # Only proceed if still valid after time check
            # Create filename with actual timestamp: 2024-02-22T09_46_32_p16_hs.mp4
            hs_formatted_timestamp = datetime_to_filename_format(hs_datetime)
            hs_file_prefix = f"{hs_formatted_timestamp}_{animal_name}"
            hs_link_name = f"{hs_file_prefix}_hs.mp4"
            hs_video_link_path = os.path.join(datetime_folder_path, hs_link_name)
            try:
                if not os.path.exists(hs_video_link_path):
                    os.symlink(closest_hs_video, hs_video_link_path)
                hs_video_linked = True
                closest_hs_video_name = hs_link_name  # Update for display

                # Submit video conversion job to cluster
                convert_script = "./convert_video.sh"
                subprocess.run([convert_script, hs_video_link_path])
            except Exception:
                pass

    # Find and copy related files with same prefix (.mat, .trk, _calib.csv)
    # Process these even if HS video was rejected due to timestamp
    if closest_hs_video:
        # Extract prefix from original hs video name (remove _hs.mp4)
        original_hs_name = os.path.basename(closest_hs_video)
        hs_prefix = original_hs_name.replace('.mp4', '')

        # Look for files with same prefix and different extensions
        related_extensions = ['.mat', '.trk', '_calib.csv']

        for ext in related_extensions:
            if ext == '_calib.csv':
                # Special case for _calib.csv
                pattern = os.path.join(track_base, f'{hs_prefix}_calib.csv')
            else:
                pattern = os.path.join(track_base, f'{hs_prefix}{ext}')

            matching_files = glob.glob(pattern)

            # Copy each matching file with new naming convention
            for file_path in matching_files:
                file_basename = os.path.basename(file_path)

                # Use the base prefix for related files (from CSV filename)
                file_prefix = hs_file_prefix

                # Create new filename using base timestamp
                if ext == '.mat':
                    new_filename = f"{file_prefix}_tracking.mat"
                elif ext == '.trk':
                    new_filename = f"{file_prefix}_tracking.trk"
                elif ext == '_calib.csv':
                    new_filename = f"{file_prefix}_calib.csv"
                else:
                    new_filename = file_basename  # fallback to original name

                dest_path = os.path.join(datetime_folder_path, new_filename)

                try:
                    if not os.path.exists(dest_path):
                        shutil.copy2(file_path, dest_path)

                    # Track which file types were copied
                    if ext == '.mat':
                        mat_files_copied = True
                    elif ext == '.trk':
                        trk_files_copied = True

                        # Check if corresponding .mat file exists, if not create it
                        mat_path = file_path.replace('.trk', '.mat')
                        if not os.path.exists(mat_path):
                            # Submit conversion job to cluster
                            convert_script = "./convert_track.sh"
                            new_mat_path = dest_path.replace('.trk', '.mat')
                            try:
                                result = subprocess.run([convert_script, file_path, new_mat_path],
                                                      capture_output=True, text=True, check=False)
                                print(f"🔄 .mat conversion submitted to cluster for {file_basename}")
                            except Exception as e:
                                print(f"❌ Failed to submit conversion job for {file_basename}: {e}")

                    elif ext == '_calib.csv':
                        calib_files_copied = True
                except Exception:
                    pass

# Print status summary
print(f"\n=== Summary ===")
print(f"Target folder: {datetime_folder_path}")
print(f"All params CSV:  {'✅' if csv_copied else '❌'}")

# Rig video with filename
if rig_video_linked and 'video_basename' in locals():
    print(f"Rig video:       ✅ {video_basename}")
else:
    print(f"Rig video:       ❌")

# HS cam frames CSV with filename
if hs_cam_frames_linked and 'hs_cam_frames_basename' in locals():
    print(f"HS cam frames:   ✅ {hs_cam_frames_basename}")
else:
    print(f"HS cam frames:   ❌")

# HS video with filename
if hs_video_linked and closest_hs_video_name:
    print(f"HS video:        ✅ {closest_hs_video_name}")
else:
    print(f"HS video:        ❌")

print(f"MAT files:       {'✅' if mat_files_copied else '❌'}")
print(f"TRK files:       {'✅' if trk_files_copied else '❌'}")
print(f"Calib CSV files: {'✅' if calib_files_copied else '❌'}")
print("================================")