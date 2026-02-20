#!/usr/bin/env python3
"""Anchor-point calibration for cluster execution.

Usage:
    python flow/run_calib_cluster.py <zaber_path> <video_path> <hs_name> \
        <init_lag> <init_window> <t_max> <n_point> <window>
"""
import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

# Add project root to path so we can import flow modules
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

from flow.calibrate import compute_lag, exclude_outliers
from flow.constants import HS_BASE

# Use absolute TMP_PATH since cluster working directory may differ
TMP_PATH = os.path.join(PROJECT_ROOT, '.tmp')


def main():
    if len(sys.argv) != 9:
        print(f"Usage: {sys.argv[0]} <zaber_path> <video_path> <hs_name> "
              "<init_lag> <init_window> <t_max> <n_point> <window>")
        sys.exit(1)

    zaber_path = sys.argv[1]
    video_path = sys.argv[2]
    hs_name = sys.argv[3]
    init_lag = float(sys.argv[4])
    init_window = float(sys.argv[5])
    t_max = float(sys.argv[6])
    n_point = int(sys.argv[7])
    window = int(sys.argv[8])

    print(f'Running anchor calibration for {hs_name}')
    print(f'  init_lag={init_lag:.3f}, init_window={init_window}, '
          f't_max={t_max:.1f}, n_point={n_point}, window={window}')

    # run calibration along anchor points t0
    from tqdm import tqdm

    t0 = np.linspace(init_window, t_max, n_point)

    all_lag = np.zeros_like(t0, dtype=float)
    video_index = np.zeros_like(t0, dtype=int)
    zaber_index = np.zeros_like(t0, dtype=int)
    corr_val = np.zeros_like(t0, dtype=float)
    calibration = [all_lag, video_index, zaber_index, corr_val]

    for i in tqdm(range(len(t0)), miniters=5):
        calib_result = compute_lag(zaber_path, video_path, t0[i], window, init_lag)
        for j in range(len(calibration)):
            calibration[j][i] = calib_result[j]

    # exclude outliers
    t0, calibration = exclude_outliers(t0, calibration)

    # Plot calibration results
    os.makedirs(TMP_PATH, exist_ok=True)

    fig, axs = plt.subplots(1, 2, figsize=(12, 5))
    axs[0].plot(t0, calibration[0], 'o-')
    axs[0].set_xlabel('t0 (s)')
    axs[0].set_ylabel('Lag (s)')

    axs[1].plot(t0, calibration[3], 'o-')
    axs[1].set_xlabel('t0 (s)')
    axs[1].set_ylabel('Correlation')

    fig_path = os.path.join(TMP_PATH, hs_name[:-4] + '_calib.png')
    plt.tight_layout()
    plt.savefig(fig_path)
    plt.close(fig)
    print(f'Saved calibration plot to {fig_path}')

    # Save calibration CSV
    output_path = os.path.join(HS_BASE, hs_name[:-4] + '_calib.csv')
    header = ['lag', 'video_index', 'zaber_index', 'correlation']
    df = pd.DataFrame({h: calibration[i] for i, h in enumerate(header)})
    df.to_csv(output_path, index=False)
    print(f'Saved calibration data to {output_path}')


if __name__ == '__main__':
    main()
