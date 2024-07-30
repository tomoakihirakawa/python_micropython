import cv2
import numpy as np
import time

def find_available_cameras():
    available_cameras = []
    for i in range(5):  # Adjust the range as needed
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available_cameras.append(i)
            cap.release()
    return available_cameras

def capture_camera_frames(interval=1, max_frames=10, camera_index=1):
    # Open the camera with the specified index
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print(f"Error: Could not open camera with index {camera_index}.")
        return

    frames = []

    for _ in range(max_frames):
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            print("Error: Could not read frame.")
            break

        # Append the frame array to the list of frames
        frames.append(frame)

        # Display the resulting frame
        cv2.imshow('Frame', frame)

        # Wait for the specified interval
        time.sleep(interval)

        # Press 'q' on the keyboard to exit early
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

    return frames

def split_frame(frame):
    # Assuming the frame is horizontally concatenated (left | right)
    height, width, _ = frame.shape
    left_image = frame[:, :width//2]
    right_image = frame[:, width//2:]
    return left_image, right_image

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

hsv_lower = np.array([30, 150, 50])  # Example HSV lower bound
hsv_upper = np.array([90, 255, 255])  # Example HSV upper bound

def create_mask(frame, hsv_lower, hsv_upper):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, hsv_lower, hsv_upper)
    return mask


if __name__ == "__main__":
    cameras = find_available_cameras()
    if cameras:
        frames = capture_camera_frames(interval=0.01, max_frames=10000, camera_index=cameras[0])
        print("Captured frames:", len(frames))

        # Use the first frame to compute disparity
        if frames:
            left_frame, right_frame = split_frame(frames[0])
            left_mask = create_mask(left_frame, hsv_lower, hsv_upper)
            right_mask = create_mask(right_frame, hsv_lower, hsv_upper)    
            left_frame = cv2.bitwise_and(left_frame, left_frame, mask=left_mask)
            right_frame = cv2.bitwise_and(right_frame, right_frame, mask=left_mask)

            disp = stereo_distance_measurement(left_frame, right_frame)
            cv2.imshow('Disparity', disp)
            cv2.imshow('Left Image', left_frame)
            cv2.imshow('Right Image', right_frame)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    else:
        print("Error: No cameras available.")
