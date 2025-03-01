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

        # flip y-axis for motion
        if video_path[-3:] == 'avi':
            self.flip_x = False
            self.flip_y = True
        elif video_path[-3:] == 'mp4':
            self.flip_x = True
            self.flip_y = False

        self.dsp = dsp
        self.step = step
        self.fr = fr
        self.dt = 1 / fr * step

    def get_motion(self, start, length):
        frames = get_frames(self.video, start, start + length,
                            self.dsp, self.step, self.fr)

        delta = compute_flow(frames)
        dx_bar, dy_bar = average_flow(delta, self.flip_x, self.flip_y)

        return MotionData(dx_bar, dy_bar, self.dt)

    def get_frame(self, t):
        return int(t * self.fr)

    def release(self):
        self.video.release()

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
        t = self.zaber_t[t0_index:t1_index] - t0

        return MotionData(dx, dy, 0, t), t0, t1

    def get_frame(self, t):
        # find t0 in zaber_t cloest to start
        index = int(np.argmin(np.abs(self.zaber_t - t)))
        return index, self.zaber_t[index]

def compute_lag(zaber_path, video_path, t0, length, init=0):
    zaber = ZaberData(zaber_path)
    zaber_motion, t0, t1 = zaber.get_motion(start=t0, length=length)

    video = VideoData(video_path, step=4)
    optical_flow = video.get_motion(start=t0+init, length=t1-t0)

    # compute lag using cross-correlation
    corr, lags = cross_correlate(optical_flow, zaber_motion, combine=True)
    corr_val = np.max(corr)
    lag = init + float(lags[np.argmax(corr)])

    # seek the corresponding video and zaber frame
    zaber_index, zaber_time = zaber.get_frame(t0 - lag)
    video_index = video.get_frame(zaber_time + lag)

    video.release()
    return lag, video_index, zaber_index, corr_val

def calib_video(zaber_path, video_path,
                n_point=60, window=45,
                exclude=True, pbar=True):

    # find the maximum length
    zaber = ZaberData(zaber_path)
    zaber_max = zaber.zaber_t[-1]

    video = VideoData(video_path, step=4)
    video_max = video.video.get(cv2.CAP_PROP_FRAME_COUNT) / video.fr
    video.release()
    t_max = min(zaber_max, video_max) - window * 2

    # initial guess
    run_flag = True
    init_max = 720
    init_window = window
    while run_flag:
        init_lag, _, _, corr = compute_lag(zaber_path, video_path, 0, init_window)
        if corr >= 0.5:
            run_flag = False
        else:
            init_window *= 2

        if init_window > init_max:
            print('Warning: initial calibration failed')
            return None

    print('Initial Lag: %.3f (sec)' % init_lag)

    # run calibration along anchor points t0
    t0 = np.linspace(init_window, t_max, n_point)

    all_lag = np.zeros_like(t0, dtype=float)
    video_index = np.zeros_like(t0, dtype=int)
    zaber_index = np.zeros_like(t0, dtype=int)
    corr_val = np.zeros_like(t0, dtype=float)
    calibration = [all_lag, video_index,
                   zaber_index, corr_val]

    for i in tqdm(range(len(t0)), disable=not pbar, miniters=5):
        # compute lag, video frame and the corresponding zaber frame
        calib_result = compute_lag(zaber_path, video_path, t0[i], window, init_lag)
        for j in range(len(calibration)):
            calibration[j][i] = calib_result[j]

    # exclude outliers
    if exclude:
        t0, calibration = exclude_outliers(t0, calibration)

    # final result
    return t0, calibration

def exclude_outliers(t0, calibration, threshold=0.30):
    indice = calibration[3] >= threshold
    index = np.where(indice)[0]

    t0 = t0[index]
    for i in range(len(calibration)):
        calibration[i] = calibration[i][index]

    print('%d Point(s) Excluded (correlation < %.2f)' % \
          (np.sum(~indice), threshold))

    return t0, calibration

def exclude_outliers_legacy(t0, calibration, sd_scale=3, time_thres=0.25):
    '''
    Exclude outliers using standard deviation and derivative
    '''
    all_lag = calibration[0]

    # exclude outliers with s.d.
    lag_mean = np.mean(all_lag)
    lag_sd = np.std(all_lag)
    indice = np.abs(all_lag - lag_mean) < sd_scale * lag_sd

    t0 = t0[indice]
    for i in range(len(calibration)):
        calibration[i] = calibration[i][indice]
    print('%d Point(s) Excluded (outside s.d. range)' % np.sum(~indice))

    # exclude outliers with derivative
    # with derivative
    dlag = np.abs(np.diff(all_lag))
    indice = np.where(dlag > time_thres)[0] + 1
    t0 = np.delete(t0, indice)
    for i in range(len(calibration)):
        calibration[i] = np.delete(calibration[i], indice)
    print('%d Point(s) Excluded (due to large derivative)' % len(indice))

    return t0, calibration