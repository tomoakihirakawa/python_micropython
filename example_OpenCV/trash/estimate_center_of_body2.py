import cv2
import numpy as np
import time

def find_available_cameras(max_range=5):
    available_cameras = []
    for i in range(max_range):
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
    return [(lower_hue, upper_hue)]

def create_mask(hsv_frame, hue_bounds, HSV_vec, range_vec):
    lower_bound1 = np.array([hue_bounds[0][0], HSV_vec[1] - range_vec[1], HSV_vec[2] - range_vec[2]])
    upper_bound1 = np.array([hue_bounds[0][1], HSV_vec[1] + range_vec[1], HSV_vec[2] + range_vec[2]])
    
    mask1 = cv2.inRange(hsv_frame, lower_bound1, upper_bound1)
    
    if len(hue_bounds) == 2:
        lower_bound2 = np.array([hue_bounds[1][0], HSV_vec[1] - range_vec[1], HSV_vec[2] - range_vec[2]])
        upper_bound2 = np.array([hue_bounds[1][1], HSV_vec[1] + range_vec[1], HSV_vec[2] + range_vec[2]])
        mask2 = cv2.inRange(hsv_frame, lower_bound2, upper_bound2)
        return mask1 | mask2
    return mask1


def process_mask(mask):
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
    return mask

def extract_centroids(contours, area_threshold, max_objects):
    centroids = []
    for c in contours:
        if cv2.contourArea(c) > area_threshold:
            M = cv2.moments(c)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                centroids.append(((cx, cy), cv2.contourArea(c)))
    return sorted(centroids, key=lambda x: x[1], reverse=True)[:max_objects]

def draw_centroids(frame, centroids):
    for centroid, _ in centroids:
        cx, cy = centroid
        cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
        cv2.putText(frame, f"Centroid: {centroid}", (cx + 10, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

def extract_color_and_find_centroids(frame, HSV_vec, range_vec, area_threshold, max_objects):
    hue_bounds = adjust_hue_bounds(HSV_vec[0], range_vec[0])
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = create_mask(hsv_frame, hue_bounds, HSV_vec, range_vec)
    mask = process_mask(mask)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    centroids = extract_centroids(contours, area_threshold, max_objects)
    draw_centroids(frame, centroids)
    
    return frame, mask, [c[0] for c in centroids]

def capture_camera_frames(interval, max_frames, camera_index, HSV_vec, range_vec, area_threshold, max_objects):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Error: Could not open camera with index {camera_index}.")
        return

    frames = []
    prev_time = time.time()
    frame_count = 0

    for _ in range(max_frames):
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break
        
        frame, mask, centroids = extract_color_and_find_centroids(frame, HSV_vec, range_vec, area_threshold, max_objects)
        frames.append(frame)

        frame_count += 1
        current_time = time.time()
        elapsed_time = current_time - prev_time
        
        if elapsed_time > 1:
            fps = frame_count / elapsed_time
            prev_time = current_time
            frame_count = 0
        else:
            fps = frame_count / elapsed_time
        
        cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow('Processed Frame', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(interval)

    cap.release()
    cv2.destroyAllWindows()
    return frames

if __name__ == "__main__":
    cameras = find_available_cameras()
    if cameras:
        capture_camera_frames(
            interval=0.001, 
            max_frames=10000, 
            camera_index=cameras[0], 
            HSV_vec=[0, 200, 190], 
            range_vec=[6, 55, 65], 
            area_threshold=500, 
            max_objects=5
        )
    else:
        print("Error: No cameras available.")