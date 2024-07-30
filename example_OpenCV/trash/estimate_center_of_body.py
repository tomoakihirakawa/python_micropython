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

def adjust_hue_bounds(hue, range_val):
    lower_hue = (hue - range_val) % 180
    upper_hue = (hue + range_val) % 180
    if lower_hue > upper_hue:
        return [(0, upper_hue), (lower_hue, 179)]
    else:
        return [(lower_hue, upper_hue)]

def extract_color_and_find_centroid(frame, HSV_vec=[60, 162, 152], range_vec=[20, 70, 70]):
    hue_bounds = adjust_hue_bounds(HSV_vec[0], range_vec[0])
    lower_bound1 = np.array([hue_bounds[0][0], HSV_vec[1] - range_vec[1], HSV_vec[2] - range_vec[2]])
    upper_bound1 = np.array([hue_bounds[0][1], HSV_vec[1] + range_vec[1], HSV_vec[2] + range_vec[2]])
    if len(hue_bounds) == 2:
        lower_bound2 = np.array([hue_bounds[1][0], HSV_vec[1] - range_vec[1], HSV_vec[2] - range_vec[2]])
        upper_bound2 = np.array([hue_bounds[1][1], HSV_vec[1] + range_vec[1], HSV_vec[2] + range_vec[2]])
    
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    mask1 = cv2.inRange(hsv_frame, lower_bound1, upper_bound1)
    if len(hue_bounds) == 2:
        mask2 = cv2.inRange(hsv_frame, lower_bound2, upper_bound2)
        mask = mask1 | mask2
    else:
        mask = mask1

    cv2.imshow('Mask', mask)
    cv2.waitKey(1)  # Display the mask image

    # Step 2: Morphological transformations
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    cv2.imshow('Mask after Morphology', mask)
    cv2.waitKey(1)  # Display the mask after morphological transformations

    # Step 3: Contour detection
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
        cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)  # Draw the largest contour
        cv2.circle(frame, centroid, 5, (0, 255, 0), -1)  # Mark the centroid
        cv2.putText(frame, f"Centroid: {centroid}", (cx + 10, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    else:
        centroid = None

    return frame, mask, centroid

def capture_camera_frames(interval=1, max_frames=10, camera_index=1, HSV_vec=[0, 200, 190], range_vec=[6, 55,65]):
    # Open the camera with the specified index
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print(f"Error: Could not open camera with index {camera_index}.")
        return

    frames = []

    for _ in range(max_frames):
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break
        frame, mask, centroid = extract_color_and_find_centroid(frame, HSV_vec, range_vec)
        frames.append(frame)
        cv2.imshow('Processed Frame', frame)
        time.sleep(interval)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return frames

if __name__ == "__main__":
    cameras = find_available_cameras()
    if cameras:
        frames = capture_camera_frames(interval=0.001, max_frames=10000, camera_index=cameras[0])
    else:
        print("Error: No cameras available.")
