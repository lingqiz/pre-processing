#!/usr/bin/env python3
"""
Batch processing script to run collect_files.py for sessions specified in a JSON file.

Usage:
    python batch_collect.py <json_filename>
    python batch_collect.py data_20260219.json
"""

import os
import sys
import glob
import subprocess
import time
from pathlib import Path

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
BASE_PATH_ROOT = "/groups/dennis/dennislab/data/processed_data"

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
        except Exception:
            pass

    for temp_file in Path(temp_dir).glob('*.m'):
        try:
            temp_file.unlink()
        except Exception:
            pass

def main():
    import json

    if len(sys.argv) != 2:
        print("Usage: python batch_collect.py <json_filename>")
        print("Example: python batch_collect.py data_20260219.json")
        sys.exit(1)

    json_filename = sys.argv[1]
    json_path = os.path.join(DATA_DIR, json_filename)

    if not os.path.exists(json_path):
        print(f"Error: JSON file {json_path} does not exist")
        sys.exit(1)

    with open(json_path, 'r') as f:
        data = json.load(f)

    print("=" * 60)
    print("Starting batch collection...")
    print("=" * 60)

    success_count = 0
    total_count = 0

    for group_name, categories in data.items():
        base_path = f"{group_name}_ccf_all_params"
        dest_dir = os.path.join(BASE_PATH_ROOT, base_path)

        print(f"\n=== Group: {group_name} ===")
        print(f"  Base path: {dest_dir}")

        for category, datetimes in categories.items():
            print(f"\n--- Category: {category} ({len(datetimes)} sessions) ---")

            for dt in datetimes:
                total_count += 1

                # Look up the actual file in the dest folder by datetime
                pattern = os.path.join(dest_dir, f"{dt}_*_ccf_all_params_file.csv")
                matches = glob.glob(pattern)

                if not matches:
                    print(f"❌ No CSV found for datetime {dt} in {dest_dir}")
                    print("-" * 50)
                    continue

                csv_filename = os.path.basename(matches[0])
                print(f"\n⚙️  Processing: {csv_filename}")

                try:
                    run_collect_files(dest_dir, csv_filename)
                    success_count += 1
                except KeyboardInterrupt:
                    print("\n🛑 Processing interrupted by user")
                    break
                except Exception as e:
                    print(f"❌ Unexpected error: {e}")
                    continue

    # clean up the temp directory
    clean_temp()

    print("\n" + "=" * 60)
    print(f"Batch collection completed: {success_count}/{total_count} files processed successfully")
    print("=" * 60)

if __name__ == "__main__":
    main()
