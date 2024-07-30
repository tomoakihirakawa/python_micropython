import cv2
import numpy as np
from lab_lib import capture_and_split_frames, adjust_hue_bounds, create_mask, extract_centroids, draw_centroids

def on_trackbar(val):
    pass

# Initial Parameters
focal_length = 1080*10  # Example focal length in pixels
baseline = 6 / 1000  # Example baseline distance in meters

# Open the video capture
cap = cv2.VideoCapture(0)  # Adjust the camera index if needed

# Create windows
cv2.namedWindow('Left Frame')
cv2.namedWindow('Right Frame')
cv2.namedWindow('Disparity Map')
cv2.namedWindow('Depth Map')

# Define HSV range for masking
hsv_lower = np.array([30, 150, 50])  # Example HSV lower bound
hsv_upper = np.array([90, 255, 255])  # Example HSV upper bound


def process_mask(mask):
    kernel_open = np.ones((5, 5), np.uint8)
    kernel_close = np.ones((25, 25), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_open)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_close)
    return mask

def create_mask(frame, hsv_lower, hsv_upper):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, hsv_lower, hsv_upper)
    return process_mask(mask)

def extract_centroids(contours, area_threshold, max_objects):
    centroids = []
    for c in contours:
        if cv2.contourArea(c) > area_threshold:
            M = cv2.moments(c)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                centroids.append((cx, cy))
    centroids = sorted(centroids, key=lambda x: x[1], reverse=True)[:max_objects]
    return centroids

while cap.isOpened():
    # Capture and split frames
    left_frame, right_frame = capture_and_split_frames(cap)
    if left_frame is None or right_frame is None:
        break

    # Apply masks
    left_mask = create_mask(left_frame, hsv_lower, hsv_upper)
    right_mask = create_mask(right_frame, hsv_lower, hsv_upper)
    left_frame_masked = cv2.bitwise_and(left_frame, left_frame, mask=left_mask)
    right_frame_masked = cv2.bitwise_and(right_frame, right_frame, mask=right_mask)

    # Find contours and extract centroids
    contours_left, _ = cv2.findContours(left_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_right, _ = cv2.findContours(right_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    centroids_left = extract_centroids(contours_left, 50, 5)  # area_threshold=50, max_objects=5
    centroids_right = extract_centroids(contours_right, 50, 5)

    # Convert images to grayscale for disparity calculation
    grayL = cv2.cvtColor(left_frame_masked, cv2.COLOR_BGR2GRAY)
    grayR = cv2.cvtColor(right_frame_masked, cv2.COLOR_BGR2GRAY)

    # Initialize the stereo block matcher
    stereo = cv2.StereoBM_create(numDisparities=2*64, blockSize=15)

    # Compute the disparity map
    disparity = stereo.compute(grayL, grayR).astype(np.float32) / 16.0

    # Avoid division by zero
    disparity[disparity <= 0] = 10**-10

    # Calculate the depth map
    depth_map = (focal_length * baseline) / disparity

    # Normalize the disparity map for visualization
    disparity_normalized = cv2.normalize(disparity, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
    disparity_normalized = np.uint8(disparity_normalized)

    # Normalize the depth map for visualization
    depth_map_normalized = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX)
    depth_map_normalized = np.uint8(depth_map_normalized)


    # Draw centroids on frames
    draw_centroids(left_frame_masked, centroids_left)
    draw_centroids(right_frame_masked, centroids_right)

    # Display the frames
    cv2.imshow('Left Frame', left_frame_masked)
    cv2.imshow('Right Frame', right_frame_masked)
    cv2.imshow('Disparity Map', disparity_normalized)
    cv2.imshow('Depth Map', depth_map_normalized)

    # Calculate and display centroid distances
    for centroid in centroids_left:
        x, y = centroid
        distance = depth_map[y, x]
        # cv2.putText(left_frame_masked, f"({x}, {y}), Depth: {distance:.2f}m", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        print(left_frame_masked, f"({x}, {y}), Depth: {distance:.2f}m", (x, y))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
