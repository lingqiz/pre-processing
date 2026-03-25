#!/usr/bin/env python3
"""
Find folders under new_format that have a _tracking.trk but no _tracking.mat,
and submit conversion jobs via convert_track.sh.
"""

import os
import glob
import subprocess

NEW_FORMAT_BASE = "/groups/dennis/dennislab/data/new_format"
HS_CAM_BASE = "/groups/dennis/dennislab/data/hs_cam"

def main():
    convert_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "convert_track.sh")

    # Find all _tracking.trk files
    trk_files = glob.glob(os.path.join(NEW_FORMAT_BASE, "*", "*", "*_tracking.trk"))

    missing = []
    for trk_path in trk_files:
        mat_path = trk_path.replace("_tracking.trk", "_tracking.mat")
        if not os.path.exists(mat_path):
            missing.append((trk_path, mat_path))

    if not missing:
        print("No missing .mat files found.")
        return

    print(f"Found {len(missing)} folders with .trk but no .mat:")
    for trk_path, mat_path in missing:
        print(f"  {os.path.dirname(trk_path)}")

    print()
    for trk_path, mat_path in missing:
        # The trk in the folder is a copy; find the original in hs_cam
        # Resolve symlink if it is one, otherwise look up by matching the source
        if os.path.islink(trk_path):
            source_trk = os.path.realpath(trk_path)
        else:
            # trk_path is a copy; derive the hs_cam source from the filename
            # e.g. 2024-03-14T11_45_43_p16_tracking.trk -> 20240314_114543_hs.trk
            basename = os.path.basename(trk_path)
            # Extract datetime part: 2024-03-14T11_45_43
            dt_str = basename.split("_")[0]  # e.g. 2024-03-14T11
            # Actually the format is like 2024-03-14T11_45_43_p16_tracking.trk
            # We need to reconstruct: take everything before the animal name
            parts = basename.replace("_tracking.trk", "").rsplit("_", 1)
            # parts[0] = "2024-03-14T11_45_43", parts[1] = "p16"
            dt_part = parts[0]  # 2024-03-14T11_45_43
            # Convert to hs_cam format: 20240314_114543_hs.trk
            date_part = dt_part[:10].replace("-", "")  # 20240314
            time_part = dt_part[11:].replace("_", "")  # 114543
            source_name = f"{date_part}_{time_part}_hs.trk"
            source_trk = os.path.join(HS_CAM_BASE, source_name)

        if not os.path.exists(source_trk):
            print(f"WARNING: Source .trk not found: {source_trk}")
            continue

        print(f"Converting: {os.path.basename(source_trk)} -> {os.path.basename(mat_path)}")
        try:
            result = subprocess.run(
                [convert_script, source_trk, mat_path],
                capture_output=True, text=True, check=False
            )
            if result.stdout:
                print(f"  {result.stdout.strip()}")
            if result.stderr:
                print(f"  {result.stderr.strip()}")
        except Exception as e:
            print(f"  ERROR: {e}")

    print(f"\nSubmitted {len(missing)} conversion jobs.")

if __name__ == "__main__":
    main()
