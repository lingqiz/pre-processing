import numpy as np
import cv2
import pandas as pd
from scipy import stats
from scipy.interpolate import interp1d
from scipy.signal import correlate
from .compute import *

class MotionData():
    def __init__(self, dx, dy, dt, t=None):
        self.dx = stats.zscore(dx)
        self.dy = stats.zscore(dy)
        self.dt = dt

        if t is None:
            self.t = np.arange(0, len(dx)*dt, dt)
        else:
            self.t = t
            self.dt = t[-1] / len(t)

    def plot_motion(self, axis):
        axis.plot(self.t, self.dx, label='dx')
        axis.plot(self.t, self.dy, label='dy')
        axis.legend()
        axis.set_xlabel('Time (s)')
        axis.set_ylabel('Motion (z-score)')

    def interpolate(self, t):
        dx = interp1d(self.t, self.dx, kind='linear',
                      fill_value="extrapolate")(t)

        dy = interp1d(self.t, self.dy, kind='linear',
                      fill_value="extrapolate")(t)
        return dx, dy

def cross_correlate(f, g, combine=False):
    gx, gy = g.interpolate(f.t)
    lags = np.arange(-len(f.dx) + 1, len(f.dx)) * f.dt

    if combine:
        corr = (correlate(f.dx, gx, mode='full') +
                correlate(f.dy, gy, mode='full')) / \
                    signal_power([np.concatenate([f.dx, f.dy]),
                                  np.concatenate([gx, gy])])

        return corr, lags

    # else
    corr_x = correlate(f.dx, gx, mode='full') / signal_power([f.dx, gx])
    corr_y = correlate(f.dy, gy, mode='full') / signal_power([f.dy, gy])

    return corr_x, corr_y, lags

def signal_power(ts):
    power_sum = np.array([np.sum(f ** 2) for f in ts])
    return np.sqrt(np.prod(power_sum))

class VideoData():
    def __init__(self, video_path, step, dsp=0.25, fr=120):
        self.video = cv2.VideoCapture(video_path)

        if not self.video.isOpened():
            # raise an error if the video file cannot be opened
            raise ValueError("Error: Cannot open video file.")

        self.dsp = dsp
        self.step = step
        self.fr = fr
        self.dt = 1 / fr * step

    def get_motion(self, start, length):
        frames = get_frames(self.video, start, start + length,
                            self.dsp, self.step, self.fr)

        delta = compute_flow(frames)
        dx_bar, dy_bar = average_flow(delta)

        return MotionData(dx_bar, dy_bar, self.dt)

class ZaberData():
    def __init__(self, data_path):
        data_frame = pd.read_csv(data_path, low_memory=False)

        ZABER_TO_MM = 508 / 72248
        zaber_x = data_frame['zaber_x'].to_numpy() * ZABER_TO_MM
        zaber_y = data_frame['zaber_y'].to_numpy() * ZABER_TO_MM
        self.zaber_t = data_frame['relative_time'].to_numpy()

        self.dx_zaber = np.diff(zaber_x)
        self.dy_zaber = np.diff(zaber_y)

    def get_motion(self, start, length):
        # find t0 in zaber_t cloest to start
        t0_index = np.argmin(np.abs(self.zaber_t - start))
        t0 = self.zaber_t[t0_index]

        # find t1 in zaber_t cloest to start
        t1_index = np.argmin(np.abs(self.zaber_t - (start + length)))
        t1 = self.zaber_t[t1_index]

        dx = self.dx_zaber[t0_index:t1_index]
        dy = self.dy_zaber[t0_index:t1_index]
        t = self.zaber_t[t0_index:t1_index]

        return MotionData(dx, dy, 0, t), t0, t1