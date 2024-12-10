import cv2, os
import numpy as np
import matplotlib.pyplot as plt
from flow.compute import *

# downsample factor
factor = 0.25

# Path to the video file
HS_BASE = '/groups/dennis/dennislab/data/hs_cam'
video_path = "231004_101805_video.avi"
video_path = os.path.join(HS_BASE, video_path)

# Open the video file
video = cv2.VideoCapture(video_path)

# Check if the video file is opened successfully
if not video.isOpened():
    print("Error: Cannot open video file.")
    exit()

# Read the first frame
ret, last_frame = video.read()
if not ret:
    print("Error: Cannot read the video file.")
    video.release()
    exit()

last_frame = convert_frame(last_frame, factor)

# Set up Matplotlib
plt.ion()  # Turn on interactive mode
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Subplots
flow_ax = axes[0]
magnitude_ax = axes[1]
angle_ax = axes[2]

# Titles
flow_ax.set_title("Optical Flow")
magnitude_ax.set_title("Magnitude Histogram")
angle_ax.set_title("Angle Histogram")

# Initialize histograms
magnitude_bins = np.linspace(0, 50, 50)
angle_bins = np.linspace(0, 360, 90)

magnitude_hist, = magnitude_ax.plot([], [], label="Magnitude", color="blue")
angle_hist, = angle_ax.plot([], [], label="Angle", color="orange")

magnitude_ax.set_xlim(0, 50)
angle_ax.set_xlim(0, 360)
angle_ax.set_xticks(np.linspace(0, 360, 9))
magnitude_ax.set_xlabel("Magnitude")
magnitude_ax.set_ylabel("Frequency")
angle_ax.set_xlabel("Angle (Degrees)")
angle_ax.set_ylabel("Frequency")

magnitude_ax.legend()
angle_ax.legend()
plt.tight_layout()

# Main loop
while True:
    ret, frame = video.read()
    if not ret:
        print("End of video.")
        break

    # Convert the current frame to grayscale
    frame = convert_frame(frame, factor)

    delta, magnitude, angle = compute_flow(np.array([last_frame, frame]), polar=True)
    dx_bar = np.mean(delta[..., 0])
    dy_bar = np.mean(delta[..., 1])

    # Create HSV representation of optical flow
    flow_vis = flow_rgb(magnitude[0], angle[0])

    # Update flow visualization
    flow_ax.clear()
    flow_ax.imshow(flow_vis)
    flow_ax.set_title("dx = {:.2f}, dy = {:.2f}".format(dx_bar, dy_bar))
    flow_ax.axis("off")

    # Update histograms
    angle = np.rad2deg(angle)
    magnitude_counts, _ = np.histogram(magnitude.flatten(), bins=magnitude_bins)
    angle_counts, _ = np.histogram(angle.flatten(), bins=angle_bins)

    magnitude_hist.set_data(magnitude_bins[:-1], magnitude_counts)
    angle_hist.set_data(angle_bins[:-1], angle_counts)

    magnitude_ax.relim()
    magnitude_ax.autoscale_view()
    angle_ax.relim()
    angle_ax.autoscale_view()

    # Update the plots
    fig.canvas.draw()
    fig.canvas.flush_events()

    # Update the previous frame
    last_frame = frame

video.release()
plt.ioff()
plt.show()
