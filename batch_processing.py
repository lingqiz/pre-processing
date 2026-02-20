#!/usr/bin/env python3
# Usage: python batch_processing.py
# Reads group and datetime information from ./data/data_YYYYMMDD.json
# Processes CSV files for each animal and datetime combination using run_processing.py

import os
import sys
import json
import re
from pathlib import Path
import run_processing

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
BASE_PATH_ROOT = "/groups/dennis/dennislab/data/processed_data"

def parse_group_animals(group_name):
    """Parse group name into individual animal names.
    e.g. 'b12b13' -> ['b12', 'b13'], 'p16p17p18' -> ['p16', 'p17', 'p18']
    """
    animals = re.findall(r'[a-zA-Z]+\d+', group_name)

    if not animals:
        raise ValueError(f"Could not parse animal names from group '{group_name}'")
    return animals

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
        animals = parse_group_animals(group_name)
        base_path = f"{group_name}_ccf_all_params"

        print(f"=== Group: {group_name} ===")
        print(f"  Animals: {', '.join(animals)}")
        print(f"  Base path: {os.path.join(BASE_PATH_ROOT, base_path)}")
        print()

        # Collect all datetimes across all categories
        for category, datetimes in categories.items():
            print(f"--- Category: {category} ({len(datetimes)} sessions) ---")

            for i, dt in enumerate(datetimes):
                animal = animals[i % len(animals)]
                csv_filename = f"{dt}_{animal}_ccf_all_params_file.csv"
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
