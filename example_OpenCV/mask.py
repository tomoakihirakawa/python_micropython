
'''DOC_EXTRACT

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

def extract_red_color(frame):
    # Convert the image from BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define the range of red color in HSV
    # lower_red1 = np.array([0, 70, 50])
    # upper_red1 = np.array([10, 255, 255])
    # lower_red2 = np.array([170, 70, 50])
    # upper_red2 = np.array([180, 255, 255])

    # define for green

    green = [60, 162, 152]
    lower_green = np.array([green[0] - 20, green[1] - 70, green[2] - 70])
    upper_green = np.array([green[0] + 20, green[1] + 70, green[2] + 70])
    # why 40 to 80? because green is between 40 to 80 in HSV
    # why 70 to 255? because green is between 70 to 255 in HSV
    # why 50 to 255? because green is between 50 to 255 in HSV
    # what is the center of green? 60, 162, 152
    
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
        frame = extract_red_color(frame)[0]
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
