
'''

pip install opencv-contrib-python
を実行して，opencvだけでなくopencv-contribもインストールする必要がある．

'''

import cv2
import numpy as np
from lab_lib import capture_and_split_frames

def on_trackbar(val):
    pass

# Initial Parameters
focal_length = 1080  # Example focal length in pixels * 10 for better trackbar precision
baseline = 60  # Example baseline distance in mm

# Open the video capture
cap = cv2.VideoCapture(0)  # Adjust the camera index if needed

# Create windows
cv2.namedWindow('Left Frame')
cv2.namedWindow('Right Frame')
cv2.namedWindow('Disparity Map')
cv2.namedWindow('Depth Map')

# Initialize the stereo block matcher
stereo = cv2.StereoSGBM_create(
    minDisparity=0,
    numDisparities=64,
    blockSize=15,
    P1=8 * 3 * 3**2,
    P2=32 * 3 * 3**2,
    disp12MaxDiff=1,
    uniquenessRatio=10,
    speckleWindowSize=100,
    speckleRange=32
)

# Create the WLS filter
wls_filter = cv2.ximgproc.createDisparityWLSFilter(matcher_left=stereo)
stereoR = cv2.ximgproc.createRightMatcher(stereo)
wls_filter.setLambda(8000.0)
wls_filter.setSigmaColor(1.5)

while cap.isOpened():
    imgL, imgR = capture_and_split_frames(cap)
    if imgL is None or imgR is None:
        break

    # Convert images to grayscale for disparity calculation
    grayL = cv2.cvtColor(imgL, cv2.COLOR_BGR2GRAY)
    grayR = cv2.cvtColor(imgR, cv2.COLOR_BGR2GRAY)

    # Compute the disparity map
    disparityL = stereo.compute(grayL, grayR).astype(np.float32) / 16.0
    disparityR = stereoR.compute(grayR, grayL).astype(np.float32) / 16.0

    # Filter the disparity map
    filtered_disparity = wls_filter.filter(disparityL, grayL, None, disparityR)
    
    # Avoid division by zero
    filtered_disparity[filtered_disparity <= 0] = 10**-10

    # Calculate the depth map
    depth_map = (focal_length * baseline) / filtered_disparity

    # Normalize the disparity map for visualization
    disparity_normalized = cv2.normalize(filtered_disparity, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
    disparity_normalized = np.uint8(disparity_normalized)

    # Normalize the depth map for visualization
    depth_map_normalized = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX)
    depth_map_normalized = np.uint8(depth_map_normalized)

    # Display the frames
    # cv2.imshow('Left Frame', imgL)
    # cv2.imshow('Right Frame', imgR)
    cv2.imshow('Disparity Map', disparity_normalized)
    # cv2.imshow('Depth Map', depth_map_normalized)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
