#!/usr/bin/env python3
"""
Batch submit JAABADetect jobs for sessions specified in a JSON file.

Usage:
    python batch_jaaba.py <json_filename>
    python batch_jaaba.py data.json
"""

import os
import sys
import json
import glob
import subprocess

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
BASE_PATH_ROOT = "/groups/dennis/dennislab/data/processed_data"
NEW_FORMAT_BASE = "/groups/dennis/dennislab/data/new_format"

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.base_utils import parse_filename


def main():
    if len(sys.argv) != 2:
        print("Usage: python batch_jaaba.py <json_filename>")
        print("Example: python batch_jaaba.py data.json")
        sys.exit(1)

    json_filename = sys.argv[1]
    json_path = os.path.join(DATA_DIR, json_filename)

    if not os.path.exists(json_path):
        print(f"Error: JSON file {json_path} does not exist")
        sys.exit(1)

    with open(json_path, 'r') as f:
        data = json.load(f)

    run_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_jaaba.sh")

    print("=" * 60)
    print("Starting batch JAABA submission...")
    print("=" * 60)

    submitted = 0
    skipped = 0

    for group_name, categories in data.items():
        base_path_with_suffix = f"{group_name}_ccf_all_params"
        if os.path.isdir(os.path.join(BASE_PATH_ROOT, base_path_with_suffix)):
            base_path = base_path_with_suffix
        else:
            base_path = group_name
        dest_dir = os.path.join(BASE_PATH_ROOT, base_path)

        print(f"\n=== Group: {group_name} ===")

        for category, datetimes in categories.items():
            print(f"\n--- Category: {category} ({len(datetimes)} sessions) ---")

            for dt in datetimes:
                # Find the CSV to get the animal name
                pattern = os.path.join(dest_dir, f"{dt}_*_ccf_all_params_file.csv")
                matches = glob.glob(pattern)

                if not matches:
                    print(f"  No CSV found for {dt}, skipping")
                    skipped += 1
                    continue

                csv_filename = os.path.basename(matches[0])
                animal_name, date_time = parse_filename(csv_filename)

                # Build expdir: new_format/<animal>/<animal>_<datetime_dashes>
                datetime_folder_name = f"{animal_name}_{date_time.replace('T', '-').replace('_', '-')}"
                expdir = os.path.join(NEW_FORMAT_BASE, animal_name, datetime_folder_name)

                if not os.path.isdir(expdir):
                    print(f"  Folder not found: {expdir}, skipping")
                    skipped += 1
                    continue

                print(f"  Submitting: {datetime_folder_name}")
                try:
                    subprocess.run([run_script, expdir], check=False)
                    submitted += 1
                except Exception as e:
                    print(f"  ERROR: {e}")
                    skipped += 1

    print("\n" + "=" * 60)
    print(f"Batch JAABA: {submitted} submitted, {skipped} skipped")
    print("=" * 60)


if __name__ == "__main__":
    main()
