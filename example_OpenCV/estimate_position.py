import cv2
import numpy as np
import time
from lab_lib import find_available_cameras, extract_color_and_find_centroids, capture_and_split_frames, getEstimatedPosition

def put_text(frame, text, z):
    cv2.rectangle(frame, (0, z-40), (600, z), (0, 0, 0), cv2.FILLED)
    cv2.putText(frame, text, (0, z-5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

def display_centroids_and_positions(R_frame, L_frame, R_centroids, L_centroids):
    colors = [(0, 255, 0), (0, 0, 255), (255, 0, 0), (255, 255, 0), (0, 255, 255)]
    for i in range(len(L_centroids)):
        if len(R_centroids) > i:
            v1 = getEstimatedPosition(R_centroids[i], L_centroids[i], f=1.8, b=60., Ry=1280., Rz=720., HFOV=120., aspect_ratio=16./9.)
            put_text(R_frame, f"Position: [{v1[0]:.0f}, {v1[1]:.0f}, {v1[2]:.0f}]", 120+40*i)
            color = colors[i % len(colors)]
            cv2.circle(R_frame, R_centroids[i], 5, color, -1)
            cv2.circle(L_frame, L_centroids[i], 5, color, -1)

class timer:
    def __init__(self):
        self.prev_time = time.time()

    def elapsed_time(self):
        current_time = time.time()
        elapsed_time = current_time - self.prev_time
        self.prev_time = current_time
        return elapsed_time

def capture_camera_frames(max_frames, camera_index, HSV_vec, range_vec, area_threshold, max_num_objects, desired_fps):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Error: Could not open camera with index {camera_index}.")
        return

    tm = timer()
    frame_count = 0

    mouse_x, mouse_y = -1, -1
    def onMouse(event, x, y, flags, param):
        nonlocal mouse_x, mouse_y
        if event == cv2.EVENT_MOUSEMOVE:
            mouse_x, mouse_y = x, y

    cv2.namedWindow('Combined Frame')
    cv2.setMouseCallback('Combined Frame', onMouse)

    while frame_count < max_frames:
        ret, R_frame, L_frame = capture_and_split_frames(cap)
        if not ret:
            print("Error: Could not read frame.")
            break

        L_frame, L_mask, hsv_L_frame, L_centroids = extract_color_and_find_centroids(L_frame, HSV_vec, range_vec, area_threshold, max_num_objects)
        R_frame, R_mask, hsv_R_frame, R_centroids = extract_color_and_find_centroids(R_frame, HSV_vec, range_vec, area_threshold, max_num_objects)

        display_centroids_and_positions(R_frame, L_frame, R_centroids, L_centroids)

        if mouse_x >= 0 and mouse_y >= 0 and mouse_x < hsv_R_frame.shape[1] and mouse_y < hsv_R_frame.shape[0]:
            hsv_value = hsv_R_frame[mouse_y, mouse_x]
            put_text(R_frame, f"FPS: {fps:.2f}, HSV: ({hsv_value[0]}, {hsv_value[1]}, {hsv_value[2]})", 40)
            put_text(R_frame, f"pixel: ({mouse_x}/{R_frame.shape[1]}, {mouse_y}/{R_frame.shape[0]})", 80)

        if mouse_x > 1280 and mouse_y > 0 and mouse_x-1280 < hsv_L_frame.shape[1] and mouse_y < hsv_L_frame.shape[0]:
            hsv_value = hsv_L_frame[mouse_y, mouse_x-1280]
            put_text(L_frame, f"pixel: ({mouse_x-1280}/{L_frame.shape[1]}, {mouse_y}/{L_frame.shape[0]})", 80)

        # 

        if frame_count % 10 == 0:
            elapsed_time = tm.elapsed_time()
            fps = 10. / elapsed_time

        frame_count += 1
        combined_frame = np.hstack((np.vstack((R_frame, cv2.cvtColor(R_mask, cv2.COLOR_GRAY2BGR))),
                                    np.vstack((L_frame, cv2.cvtColor(L_mask, cv2.COLOR_GRAY2BGR)))))
        cv2.imshow('Combined Frame', combined_frame)

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
            HSV_vec=[0, 150, 210], 
            range_vec=[10, 50, 50], 
            area_threshold=10, 
            max_num_objects=3,
            desired_fps=10
        )
    else:
        print("Error: No cameras available.")