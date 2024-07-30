import cv2
import numpy as np
import time
from lab_lib import adjust_hue_bounds, find_available_cameras, create_mask, extract_centroids, draw_centroids


def process_mask(mask):
    kernel_open = np.ones((5, 5), np.uint8)
    kernel_close = np.ones((25, 25), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_open)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_close)
    return mask

def extract_color_and_find_centroids(frame, HSV_vec, range_vec, area_threshold, max_objects):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hue_bounds = adjust_hue_bounds(HSV_vec[0], range_vec[0])
    mask = create_mask(hsv_frame, hue_bounds, HSV_vec, range_vec)
    mask = process_mask(mask)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    centroids = extract_centroids(contours, area_threshold, max_objects)
    draw_centroids(frame, centroids)
    return frame, mask, hsv_frame

def capture_camera_frames(max_frames, camera_index, HSV_vec, range_vec, area_threshold, max_objects, desired_fps):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Error: Could not open camera with index {camera_index}.")
        return
    
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    prev_time = time.time()
    frame_count = 0

    mouse_x, mouse_y = -1, -1
    def onMouse(event, x, y, flags, param):
        nonlocal mouse_x, mouse_y
        if event == cv2.EVENT_MOUSEMOVE:
            mouse_x, mouse_y = x, y

    cv2.namedWindow('Original Frame')
    cv2.namedWindow('Mask Frame')
    cv2.setMouseCallback('Original Frame', onMouse)

    while frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        frame, mask, hsv_frame = extract_color_and_find_centroids(frame, HSV_vec, range_vec, area_threshold, max_objects)
        frame_count += 1

        current_time = time.time()
        elapsed_time = current_time - prev_time
        fps = frame_count / elapsed_time if elapsed_time > 0 else 0

        if elapsed_time >= 1:
            prev_time = current_time
            frame_count = 0

        if mouse_x >= 0 and mouse_y >= 0:
            hsv_value = hsv_frame[mouse_y, mouse_x]            
            text = f"FPS: {fps:.2f}, HSV: ({hsv_value[0]}, {hsv_value[1]}, {hsv_value[2]}), pixel: ({mouse_x}/{frame.shape[1]}, {mouse_y}/{frame.shape[0]})"

            cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow('Original Frame', frame)
        cv2.imshow('Mask Frame', mask)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    cameras = find_available_cameras()
    if cameras:
        capture_camera_frames(
            max_frames=10000, 
            camera_index=cameras[0], 
            HSV_vec=[50, 175, 175], 
            range_vec=[10, 30, 80], 
            area_threshold=50, 
            max_objects=2,
            desired_fps=30
        )
    else:
        print("Error: No cameras available.")
