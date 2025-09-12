from datetime import datetime

def parse_filename(filename):
    """
    Parse filename to extract animal name and datetime
    Expected format: 2024-02-22T09_46_32_p16_ccf_all_params_file.csv
    """
    # Remove .csv extension
    base_name = filename.replace('.csv', '')
    
    # Remove the suffix '_ccf_all_params_file'
    base_name = base_name.replace('_ccf_all_params_file', '')
    
    # Split by underscore to separate datetime and animal name
    parts = base_name.split('_')
    
    # The datetime part is the first 3 parts: 2024-02-22T09_46_32
    datetime_str = '_'.join(parts[:3])
    
    # The animal name is the last part
    animal_name = parts[-1]
    
    return animal_name, datetime_str

def parse_datetime(datetime_str):
    """
    Parse the datetime string
    Convert format from 2024-02-22T09_46_32 to datetime object
    """
    # Replace underscores with colons for time part
    formatted_str = datetime_str.replace('_', ':')
    dt = datetime.fromisoformat(formatted_str)
    
    return dt

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
    
    return closest_video

def datetime_to_filename_format(dt):
    """
    Convert datetime object to filename format: 2024-02-22T09_46_32
    """
    return dt.strftime('%Y-%m-%dT%H_%M_%S')