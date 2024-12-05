import numpy as np
from scipy import stats
from scipy.interpolate import interp1d
from scipy.signal import correlate

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