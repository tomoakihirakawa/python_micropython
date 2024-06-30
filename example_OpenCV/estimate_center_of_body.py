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

def extract_color_and_find_centroid(frame, HSV_vec=[60, 162, 152], range_vec=[20, 70, 70]):
    # Convert the image from BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define the range of the target color in HSV
    lower_bound = np.array(HSV_vec) - np.array(range_vec)
    upper_bound = np.array(HSV_vec) + np.array(range_vec)
    
    # Threshold the HSV image to get only the target color
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(frame, frame, mask=mask)

    # Morphological operations
    kernel = np.ones((10, 10), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # Find contours and calculate the centroid
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            centroid = (cx, cy)
        else:
            centroid = None
    else:
        centroid = None

    return res, mask, centroid

def capture_camera_frames(interval=1, max_frames=10, camera_index=1, HSV_vec=[60, 162, 152], range_vec=[30, 70, 70]):
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

        # Extract the target color and find the centroid
        frame, mask, centroid = extract_color_and_find_centroid(frame, HSV_vec, range_vec)

        # Draw the centroid on the frame
        if centroid:
            cv2.circle(frame, centroid, 5, (0, 255, 0), -1)
            cv2.putText(frame, f"Centroid: {centroid}", (centroid[0] + 10, centroid[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

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

if __name__ == "__main__":
    cameras = find_available_cameras()
    if cameras:
        frames = capture_camera_frames(interval=0.001, max_frames=10000, camera_index=cameras[0])
    else:
        print("Error: No cameras available.")
