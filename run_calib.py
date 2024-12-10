import argparse, os
import matplotlib.pyplot as plt
import pandas as pd
from flow.calibrate import calib_video

# example usage:
# python3 run_calib.py p16p17p18 2024-05-20T12_29_48_p16 20240520_122900_hs.mp4

ZABER_BASE = '/groups/dennis/dennislab/data/processed_data'
HS_BASE = '/groups/dennis/dennislab/data/hs_cam'
USER_PATH = os.path.expanduser('~/hs_align')

# zaber and video paths
parser = argparse.ArgumentParser()
parser.add_argument('folder', type=str)
parser.add_argument('zaber', type=str)
parser.add_argument('hs_name', type=str)
args = parser.parse_args()

# full paths
zaber_full = os.path.join(args.folder, args.zaber + '_all_params_file.csv')
zaber_path = os.path.join(ZABER_BASE, zaber_full)

video_path = os.path.join(HS_BASE, args.hs_name)
output_path = os.path.join(HS_BASE, args.hs_name[:-4] + '_calib.csv')
print('Calibrating', args.hs_name, 'with', zaber_full)

# run calibration
t0, calibration = calib_video(zaber_path, video_path, pbar=True)

# plot calibration results
fig, axs = plt.subplots(1, 2, figsize=(12, 5))

# lag
axs[0].plot(t0, calibration[0], 'o-')
axs[0].set_xlabel('t0 (s)')
axs[0].set_ylabel('Lag (s)')

# correlation r value
axs[1].plot(t0, calibration[3], 'o-')
axs[1].set_xlabel('t0 (s)')
axs[1].set_ylabel('Correlation')

# save plot
fig_path = os.path.join(USER_PATH, args.hs_name[:-4] + '_calib.png')
plt.tight_layout()
plt.savefig(fig_path)
plt.close(fig)
print('Save calibration plot to', fig_path)

# save calibration (write to csv file)
header = ['lag', 'video_index', 'zaber_index', 'correlation']
df = pd.DataFrame({h: calibration[i] for i, h in enumerate(header)})
df.to_csv(output_path, index=False)
