#!/usr/bin/env python3
"""
Batch processing script to run collect_files.py on all CSV files in a directory
that match the datetime format pattern.

Usage:
    python batch_collect.py /groups/dennis/dennislab/data/processed_data/p16p17p18_ccf_all_params
"""

import os
import sys
import glob
import subprocess
import re
import time
from pathlib import Path

def find_datetime_csv_files(base_path):
    """
    Find all CSV files in the base_path that match the datetime format pattern.
    Pattern: YYYY-MM-DDTHH_MM_SS_*_ccf_all_params_file.csv
    """
    # Pattern to match datetime format: 2024-02-22T09_46_32_*_ccf_all_params_file.csv
    datetime_pattern = r'\d{4}-\d{2}-\d{2}T\d{2}_\d{2}_\d{2}_.*_ccf_all_params_file\.csv$'

    csv_files = []
    csv_pattern = os.path.join(base_path, "*.csv")

    for csv_file in glob.glob(csv_pattern):
        filename = os.path.basename(csv_file)
        if re.match(datetime_pattern, filename):
            csv_files.append(filename)

    return sorted(csv_files)

def run_collect_files(all_params_base, csv_filename):
    """
    Run collect_files.py for a single CSV file
    """
    script_path = os.path.join(os.path.dirname(__file__), 'collect_files.py')

    try:
        result = subprocess.run([
            'python3', script_path, all_params_base, csv_filename
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout

        if result.returncode == 0:
            print(f"✅ Successfully processed: {csv_filename}")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ Error processing {csv_filename}")
            if result.stderr:
                print(f"Error: {result.stderr}")

    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout processing: {csv_filename}")
    except Exception as e:
        print(f"❌ Exception processing {csv_filename}: {e}")

    print("-" * 50)

def clean_temp():
    # sleep for 120 seconds to ensure all processes are done
    temp_dir = '/groups/zhang/home/zhangl5/.tmp/matlab'
    print("Waiting to ensure all processes are done...")
    time.sleep(120)

    # delete all files in the temp directory that ends with .log and .m
    print(f"Cleaning up temporary files in: {temp_dir}")
    for temp_file in Path(temp_dir).glob('*.log'):
        try:
            temp_file.unlink()
        except Exception as e:
            pass

    for temp_file in Path(temp_dir).glob('*.m'):
        try:
            temp_file.unlink()
        except Exception as e:
            pass

def main():
    if len(sys.argv) != 2:
        print("Usage: python batch_collect.py /path/to/all_params_base_folder")
        sys.exit(1)

    all_params_base = sys.argv[1]

    # Verify the base path exists
    if not os.path.exists(all_params_base):
        print(f"Error: Directory '{all_params_base}' does not exist")
        sys.exit(1)

    print(f"Searching for CSV files in: {all_params_base}")

    # Find all CSV files matching the datetime pattern
    csv_files = find_datetime_csv_files(all_params_base)

    if not csv_files:
        print("No CSV files matching the datetime pattern found.")
        sys.exit(0)

    print(f"Found {len(csv_files)} CSV files to process:")
    for i, csv_file in enumerate(csv_files, 1):
        print(f"  {i:2d}. {csv_file}")

    print("\n" + "="*60)
    print("Starting batch processing...")
    print("="*60)

    # Process each CSV file
    success_count = 0
    for i, csv_filename in enumerate(csv_files, 1):
        print(f"\n[{i}/{len(csv_files)}] \n⚙️  Processing: {csv_filename}")

        try:
            run_collect_files(all_params_base, csv_filename)
            success_count += 1
        except KeyboardInterrupt:
            print("\n🛑 Processing interrupted by user")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            continue

    # clean up the temp directory
    clean_temp()

    print("\n" + "="*60)
    print(f"Batch processing completed: {success_count}/{len(csv_files)} files processed successfully")
    print("="*60)

if __name__ == "__main__":
    main()