#!/usr/bin/env python3
# Usage: python batch_processing.py
# Specify the base path using 'base_path' variable
# Specify directory containing CSV files in the script using 'csv_dir' variable
# Process all CSV files in a specified directory using run_processing.py

import os
import sys
from pathlib import Path
import run_processing

def main():
    # Directory containing CSV files
    base_path = "p34p35p36p37p38"
    csv_dir = "/groups/zhang/home/zhangl5/Emily/Processed/p35_subset"

    # Check if directory exists
    if not os.path.exists(csv_dir):
        print(f"Error: Directory {csv_dir} does not exist")
        sys.exit(1)

    # Find all CSV files in the directory
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]

    if not csv_files:
        print(f"No CSV files found in {csv_dir}")
        sys.exit(1)

    print(f"Found {len(csv_files)} CSV files to process:")
    for csv_file in csv_files:
        print(f"  - {csv_file}")
    print()

    # Process each CSV file
    for csv_file in csv_files:
        print(f"Processing: {csv_file}")

        try:
            # Call the processing function directly
            run_processing.process_file(base_path, csv_file)
            print(f"✓ Successfully processed {csv_file}")

        except SystemExit as e:
            if e.code != 0:
                print(f"✗ Error processing {csv_file}: exited with code {e.code}")
            else:
                print(f"✓ Successfully processed {csv_file}")
        except Exception as e:
            print(f"✗ Unexpected error processing {csv_file}: {e}")

        print("-" * 50)

if __name__ == "__main__":
    main()