
'''DOC_EXTRACT k

OpenCVでは，HSV（Hue, Saturation, Value）色空間を使用して画像の色を定義できる．
Hue(色相)は色を表し，Saturation(彩度)は色の鮮やかさを表し，Value(明度)は色の明るさを表す．
値の範囲は，Hueは0〜179，SaturationとValueは0〜255である．

H（色相）：0から179
S（彩度）：0から255
V（明度）：0から255

| 色 | Hueの範囲 |
|---|---|
| 赤 | 0〜10, 170〜180 |
| 緑 | 40〜80 |
| 青 | 100〜140 |
 
'''

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

def extract_color(frame, HSV_vec = [60, 162, 152], range_vec = [20, 70, 70]):
    # Convert the image from BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define the range of red color in HSV    
    lower_green = np.array(HSV_vec) - np.array(range_vec)
    upper_green = np.array(HSV_vec) + np.array(range_vec)
    
    # Threshold the HSV image to get only red colors
    mask1 = cv2.inRange(hsv, lower_green, upper_green)
    mask2 = cv2.inRange(hsv, lower_green, upper_green)
    mask = cv2.bitwise_or(mask1, mask2)

    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(frame, frame, mask=mask)

    # Morphological operations
    kernel = np.ones((10, 10), np.uint8)
    dilation = cv2.dilate(mask, kernel, iterations=2)
    mask = cv2.morphologyEx(cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel), cv2.MORPH_CLOSE, kernel)

    return res, mask

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
        frame = extract_color(frame, [60, 162, 152], [200, 100, 100])[0]
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

if __name__ == "__main__":
    cameras = find_available_cameras()
    if cameras:
        frames = capture_camera_frames(interval=0.001, max_frames=10000, camera_index=cameras[0])

    else:
        print("Error: No cameras available.")
