import cv2
import numpy as np
from tqdm import tqdm

def get_frames(video, start, end, sample=1.0, step=1, fr=120):
    '''
    Get frames from start (sec) to end (sec) from the video
    '''
    start_index = start * fr
    video.set(cv2.CAP_PROP_POS_FRAMES, start_index)

    frames = []
    counter = 0
    for _ in range(int((end - start) * fr)):
        ret, frame = video.read()
        if not ret:
            break

        counter += 1
        if counter % step == 0:
            counter = 0
        else:
            continue

        frames.append(convert_frame(frame, sample))

    return np.array(frames)

def convert_frame(frame, sample=1.0):
    '''
    Convert frame to grayscale and resize
    '''
    return cv2.cvtColor(cv2.resize(frame, None, fx=sample,
                                   fy=sample), cv2.COLOR_BGR2GRAY)

def compute_flow(frames, polar=False, pbar=False):
    # initialization
    n_frame = frames.shape[0]

    prev_frame = frames[0]
    delta = np.zeros((n_frame - 1, *prev_frame.shape, 2))

    if polar:
        magnitude = np.zeros((n_frame - 1, *prev_frame.shape))
        angle = np.zeros((n_frame - 1, *prev_frame.shape))

    for i in tqdm(range(1, n_frame), disable=not pbar):
        frame = frames[i]

        # compute dense optical flow using Farneback method
        flow = cv2.calcOpticalFlowFarneback(prev_frame, frame, None,
                                            pyr_scale=0.5, levels=3,
                                            winsize=15, iterations=3,
                                            poly_n=5, poly_sigma=1.2, flags=0)
        # roll forward frames
        prev_frame = frame

        # convert flow to magnitude and angle
        delta[i - 1] = flow
        if polar:
            magnitude[i - 1], angle[i - 1] = cv2.cartToPolar(flow[..., 0],
                                                             flow[..., 1])

    if polar:
        return delta, magnitude, angle

    return delta

def average_flow(delta):
    dx_bar = np.mean(delta[:, :, :, 0], axis=(1, 2))
    dy_bar = - np.mean(delta[:, :, :, 1], axis=(1, 2))

    return dx_bar, dy_bar

def flow_rgb(magnitude, angle):
    '''
    Convert optical flow to RGB for visualization
    '''
    hsv = np.zeros((*magnitude.shape, 3), dtype=np.uint8)
    hsv[..., 1] = 255
    hsv[..., 0] = angle * 180 / np.pi / 2 # openCV uses 0-180 degrees for hue angle
    hsv[..., 2] = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)

    # Convert HSV to RGB for visualization
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)