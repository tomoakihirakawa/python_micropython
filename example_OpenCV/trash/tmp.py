import cv2
import numpy as np

def stereo_distance_measurement(left_image, right_image, num_disparities=16, block_size=15):
    # Convert images to grayscale
    gray_left = cv2.cvtColor(left_image, cv2.COLOR_BGR2GRAY)
    gray_right = cv2.cvtColor(right_image, cv2.COLOR_BGR2GRAY)

    # Create StereoBM object and compute the disparity map
    stereo = cv2.StereoBM_create(numDisparities=num_disparities, blockSize=block_size)
    disparity = stereo.compute(gray_left, gray_right)
    
    # Normalize the disparity map for display
    disp = cv2.normalize(disparity, disparity, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
    disp = np.uint8(disp)

    return disp

def capture_and_split_frames(cap):
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture image")
        return None, None
    height, width = frame.shape[:2]
    left_frame = frame[:, :width // 2]
    right_frame = frame[:, width // 2:]
    return left_frame, right_frame

def create_mask(frame, hsv_lower, hsv_upper):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, hsv_lower, hsv_upper)
    return mask

def calculate_depth(disparity, focal_length, baseline):
    disparity[disparity <= 0] = 10**-10  # Avoid division by zero
    depth = (focal_length * baseline) / disparity
    return depth

# Parameters
focal_length = 1080  # Example focal length in pixels
baseline = 0.06  # Example baseline in meters
hsv_lower = np.array([30, 150, 50])  # Example HSV lower bound
hsv_upper = np.array([90, 255, 255])  # Example HSV upper bound

cap = cv2.VideoCapture(0)  # Adjust the camera index if needed

while cap.isOpened():
    left_frame, right_frame = capture_and_split_frames(cap)
    if left_frame is None or right_frame is None:
        break

    left_mask = create_mask(left_frame, hsv_lower, hsv_upper)
    right_mask = create_mask(right_frame, hsv_lower, hsv_upper)    
    left_image = cv2.bitwise_and(left_frame, left_frame, mask=left_mask)
    right_image = cv2.bitwise_and(right_frame, right_frame, mask=left_mask)

    disparity = stereo_distance_measurement(left_image, right_image)
    depth_map = calculate_depth(disparity, focal_length, baseline)

    # Normalize the depth map for visualization
    depth_map_normalized = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX)
    depth_map_normalized = np.uint8(depth_map_normalized)

    cv2.imshow('Left Mask', left_mask)
    cv2.imshow('Right Mask', right_mask)
    cv2.imshow('Disparity Map', disparity)
    cv2.imshow('Depth Map', depth_map_normalized)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
