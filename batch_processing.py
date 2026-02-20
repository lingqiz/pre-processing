#!/usr/bin/env python3
# Usage: python batch_processing.py
# Reads group and datetime information from ./data/data_YYYYMMDD.json
# Processes CSV files for each animal and datetime combination using run_processing.py

import os
import sys
import json
import glob
import run_processing

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
BASE_PATH_ROOT = "/groups/dennis/dennislab/data/processed_data"

def main():
    if len(sys.argv) != 2:
        print("Usage: python batch_processing.py <json_filename>")
        print("Example: python batch_processing.py data_20260219.json")
        sys.exit(1)

    json_filename = sys.argv[1]
    json_path = os.path.join(DATA_DIR, json_filename)

    if not os.path.exists(json_path):
        print(f"Error: JSON file {json_path} does not exist")
        sys.exit(1)

    with open(json_path, 'r') as f:
        data = json.load(f)

    for group_name, categories in data.items():
        base_path = f"{group_name}_ccf_all_params"
        dest_dir = os.path.join(BASE_PATH_ROOT, base_path)

        print(f"=== Group: {group_name} ===")
        print(f"  Base path: {dest_dir}")
        print()

        for category, datetimes in categories.items():
            print(f"--- Category: {category} ({len(datetimes)} sessions) ---")

            for dt in datetimes:
                # Look up the actual file in the dest folder by datetime
                pattern = os.path.join(dest_dir, f"{dt}_*_ccf_all_params_file.csv")
                matches = glob.glob(pattern)

                if not matches:
                    print(f"No CSV found for datetime {dt} in {dest_dir}")
                    print("-" * 50)
                    continue

                csv_filename = os.path.basename(matches[0])
                print(f"Processing: {csv_filename}")

                try:
                    run_processing.process_file(base_path, csv_filename)
                    print(f"  Successfully processed {csv_filename}")
                except SystemExit as e:
                    if e.code != 0:
                        print(f"  Error processing {csv_filename}: exited with code {e.code}")
                    else:
                        print(f"  Successfully processed {csv_filename}")
                except Exception as e:
                    print(f"  Unexpected error processing {csv_filename}: {e}")

                print("-" * 50)

            print()

if __name__ == "__main__":
    main()
