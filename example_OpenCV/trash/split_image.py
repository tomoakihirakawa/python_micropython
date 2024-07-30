
'''DOC_EXTRACT

## デュアルカメラについて

* ベースライン距離（カメラ間距離）:60mm
* 焦点距離:おそらく$`f=3.6`$mm
* ピクセル数，左右それぞれ：(1280,720)
* アスペクト比：16:9

### ピンホールカメラモデル

カメラの位置を原点として，座標$`P`$にある光源は，$`f`$だけカメラの後ろにある面に投影されるとする．

'''

import cv2
import numpy as np
import time
from lab_lib import capture_and_split_frames

# Open the video capture
cap = cv2.VideoCapture(0)  # Adjust the camera index if needed

# Measure the time to capture and split frames
frame_count = 100  # Number of frames to measure for delay

# ---------------------------------------------------------------------------- #

cap = cv2.VideoCapture(0)  # Adjust the camera index if needed
start_time = time.time()
while cap.isOpened():

    for _ in range(frame_count):

        # Assuming the frame is split horizontally into two        
        left_frame, right_frame = capture_and_split_frames(cap)

        # Display the frames
        cv2.imshow('Left Frame', left_frame)
        cv2.imshow('Right Frame', right_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    end_time = time.time()
    cap.release()
    cv2.destroyAllWindows()

# Calculate average delay per frame
total_time = end_time - start_time
average_time_per_frame = total_time / frame_count
print(f"Average time per frame: {average_time_per_frame:.6f} seconds")

# ---------------------------------------------------------------------------- #
