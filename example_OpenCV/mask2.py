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

        frames.append(frame)

        time.sleep(interval)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    return frames

def extract_color_point(frame, lower_color, upper_color):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_color, upper_color)
    res = cv2.bitwise_and(frame, frame, mask=mask)

    # 輪郭を検出
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        # 最大の輪郭を取得
        largest_contour = max(contours, key=cv2.contourArea)
        # 重心を計算
        M = cv2.moments(largest_contour)
        if M['m00'] != 0:
            cX = int(M['m10'] / M['m00'])
            cY = int(M['m01'] / M['m00'])
            return cX, cY, res
    return None, None, res

def draw_detected_points(frame, points):
    for point in points:
        if point:
            cv2.circle(frame, point, 5, (0, 255, 0), -1)
    return frame

if __name__ == "__main__":
    cameras = find_available_cameras()
    if cameras:
        frames = capture_camera_frames(interval=0.01, max_frames=1000, camera_index=cameras[0])
        print("Captured frames:", len(frames))

        if frames:
            lower_red = np.array([0, 70, 50])
            upper_red = np.array([10, 255, 255])
            lower_red2 = np.array([170, 70, 50])
            upper_red2 = np.array([180, 255, 255])

            detected_points = []
            for frame in frames:
                cX1, cY1, res1 = extract_color_point(frame, lower_red, upper_red)
                cX2, cY2, res2 = extract_color_point(frame, lower_red2, upper_red2)
                if cX1 is not None and cY1 is not None:
                    detected_points.append((cX1, cY1))
                if cX2 is not None and cY2 is not None:
                    detected_points.append((cX2, cY2))
                
                combined_frame = draw_detected_points(frame, detected_points)
                cv2.imshow('Detected Points', combined_frame)
                cv2.imshow('Masked Frame', res1 if cX1 is not None else res2)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cv2.waitKey(0)
            cv2.destroyAllWindows()
    else:
        print("Error: No cameras available.")
