'''DOC_EXTRACT 0_1_0 

# 座標推定

## 概要

<img src="001.png" width="50%">
<hr>
<img src="002.png" width="50%">
<hr>
<img src="003.png" width="50%">
<hr>
<img src="004.png" width="50%">
<hr>
<img src="005.png" width="50%">
<hr>
<img src="006.png" width="50%">
<hr>
<img src="007.png" width="50%">
<hr>
<img src="008.png" width="50%">
<hr>
<img src="009.png" width="50%">
<hr>
<img src="010.png" width="50%">
<hr>
<img src="011.png" width="50%">
<hr>
<img src="012.png" width="50%">

このようなわけで，下のようにプログラムすると，点の座標を推定することができる．

```python
def getEstimatedPosition(p,q,f=1.8, b=60., Ry=1280., Rz=720.,HFOV=120., aspect_ratio=16./9.):
    #この変換は，ピンホールカメラモデルを仮定して，カメラの後ろ側にある面に投影された光源の位置を計算するものである．
    #カメラを前から見て，左下が原点で，右がx軸の正方向，上がy軸の正方向，手前がz軸の正方向となるような座標系を仮定している．
    [py,pz] = p
    [qy,qz] = q
    eps = 10.**-20    
    v1x = (b * Ry)/(2 * math.tan(HFOV/180. * math.pi / 2.) * (-py + qy + eps))
    v1y = (2*b*py - b*Ry)/(2*py - 2*qy + eps)
    v1z = (b * Ry * (pz + qz - Rz))/(2 *aspect_ratio* (py - qy + eps) *Rz)    
    return np.array([v1x, v1y, v1z])
```

## 実装

実現したいこと：

- 指定した数の点を検出し，３次元座標を推定する．
- その点の座標にラベルを付け，座標を追跡する．
- 見失った点がある場合は，どのラベルの点が消えたかを判断できるようにする．

1. 初期状態で指定した数の点を検出し，ラベルを付ける．
    ラベルは，左下を原点として，右がx軸の正方向，上がy軸の正方向として，座標の和が小さいものから順に1,2,3,...とする．
2. 大幅に点が移動することはないものとし，次のフレームでは，前のフレームの点との距離が最小となるようにラベルを付ける．(最小値を見つける際に，見失った点の座標は，前のフレームの座標とする．)

### `extract_color_and_find_centroids(frame, HSV_vec, range_vec, area_threshold, max_num_objects)`

* `frame` : カメラからのフレーム
* `HSV_vec` : 抽出したい色のHSV値
* `range_vec` : 抽出したい色の範囲
* `area_threshold` : 抽出される面積の最小値
* `max_num_objects` : 抽出する最大のオブジェクト数

```python
def extract_color_and_find_centroids(frame, HSV_vec, range_vec, area_threshold, max_num_objects):    
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hue_bounds = adjust_hue_bounds(HSV_vec[0], range_vec[0])
    mask = create_mask(hsv_frame, hue_bounds, HSV_vec, range_vec)
    mask = process_mask(mask)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    centroids = []
    centroids_sum = []
    for contour in contours:
        if cv2.contourArea(contour) >= area_threshold:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                centroids.append((cX, cY))
                centroids_sum.append(cX + cY)
            if len(centroids) >= max_num_objects:
                break

    def centroids_sum(centroid):
        return centroid[0] + centroid[1]

    return frame, mask, hsv_frame, sorted(centroids, key=centroids_sum)
```

**最終的に返される，`centroids`の順番，インデックスこそがラベルである．**


'''

import cv2
import numpy as np
import time
from lab_lib import configure_camera_resolution, find_available_cameras, extract_color_and_find_centroids, capture_and_split_frames, getEstimatedPosition
from itertools import permutations 

WIDTH = 1920
WIDTH2 = WIDTH * 2
HEIGHT = 1080

def put_text(frame, text, z):
    cv2.rectangle(frame, (0, z-40), (600, z), (0, 0, 0), cv2.FILLED)
    cv2.putText(frame, text, (0, z-5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

def display_centroids_and_positions(R_frame, L_frame, R_centroids, L_centroids):
    colors = [(0, 255, 0), (0, 0, 255), (255, 0, 0), (255, 255, 0), (0, 255, 255)]
    for i in range(len(L_centroids)):
        if len(R_centroids) > i:
            v1 = getEstimatedPosition(R_centroids[i], L_centroids[i], f=1.8, b=60., Ry=WIDTH, Rz=HEIGHT, HFOV=120., aspect_ratio=16./9.)
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

L_points_xyz = []
R_points_xyz = []

def capture_camera_frames(max_frames, camera_index, HSV_vec, range_vec, area_threshold, max_num_objects, desired_fps):
    global L_points_xyz, R_points_xyz
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Error: Could not open camera with index {camera_index}.")
        return

    configure_camera_resolution(cap, WIDTH2, HEIGHT)

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

        '''
        `L_centroids`と`R_centroids`は，それぞれ左右のカメラから検出された点の座標を格納するリストである．        
        '''

        L_frame, L_mask, hsv_L_frame, L_centroids = extract_color_and_find_centroids(L_frame, HSV_vec, range_vec, area_threshold, max_num_objects)
        R_frame, R_mask, hsv_R_frame, R_centroids = extract_color_and_find_centroids(R_frame, HSV_vec, range_vec, area_threshold, max_num_objects)

        def sort_centroids(L_points_xyz, L_centroids):
            if max_num_objects - len(L_centroids) > 0:
                for _ in range(max_num_objects - len(L_centroids)):
                    L_centroids.append((0, 0))
            i = 0
            sum = 0
            min_sum = 100000
            sums = []
            optimal_centroids = []
            for centroids in list(permutations(L_centroids)):
                for xy in centroids:
                    # calculte the distance between the points                
                    sum += abs(L_points_xyz[i][0] - xy[0]) + abs(L_points_xyz[i][1] - xy[1])
                    i += 1
                sums.append(sum)
                if sum < min_sum:
                    min_sum = sum
                    optimal_centroids = centroids
                sum = 0
                i = 0        
            
            if frame_count % 10 == 0:
                print("sort_centroids")
                print(sums)
                print(min_sum)
            
            return optimal_centroids

        L_centroids = L_points_xyz = sort_centroids(L_points_xyz, L_centroids)
        R_centroids = R_points_xyz = sort_centroids(R_points_xyz, R_centroids)

        def sort_Rcentroids(L_centroids, R_centroids):            
            i = 0
            sum = 0
            min_sum = 100000
            sums = []
            optimal_centroids = []
            for centroids in list(permutations(R_centroids)):
                for xy in centroids:
                    sum += abs(L_centroids[i][0] - xy[0]) + abs(L_centroids[i][1] - xy[1])
                    i += 1
                sums.append(sum)
                if sum < min_sum:
                    min_sum = sum
                    optimal_centroids = centroids
                sum = 0
                i = 0        

            if frame_count % 10 == 0:
                print("sort_Rcentroids")
                print(sums)
                print(min_sum)


            return optimal_centroids

        R_centroids = R_points_xyz = sort_Rcentroids(L_centroids, R_centroids)

        '''
        過去の並びに対して，差の絶対値が，最小となる組み合わせを探し，そのインデックスをラベルとする．
        '''

        display_centroids_and_positions(R_frame, L_frame, R_centroids, L_centroids)

        if mouse_x >= 0 and mouse_y >= 0 and mouse_x < hsv_R_frame.shape[1] and mouse_y < hsv_R_frame.shape[0]:
            hsv_value = hsv_R_frame[mouse_y, mouse_x]
            put_text(R_frame, f"FPS: {fps:.2f}, HSV: ({hsv_value[0]}, {hsv_value[1]}, {hsv_value[2]})", 40)
            put_text(R_frame, f"pixel: ({mouse_x}/{R_frame.shape[1]}, {mouse_y}/{R_frame.shape[0]})", 80)

        if mouse_x > HEIGHT and mouse_y > 0 and mouse_x-HEIGHT < hsv_L_frame.shape[1] and mouse_y < hsv_L_frame.shape[0]:
            hsv_value = hsv_L_frame[mouse_y, mouse_x-HEIGHT]
            put_text(L_frame, f"pixel: ({mouse_x-HEIGHT}/{L_frame.shape[1]}, {mouse_y}/{L_frame.shape[0]})", 80)

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

    max_num_objects = 2
    for _ in range(max_num_objects):
        L_points_xyz.append((0, 0))
        R_points_xyz.append((0, 0))

    if cameras:
        capture_camera_frames(
            max_frames=10000, 
            camera_index=cameras[0], 
            HSV_vec=[0, 150, 210], 
            range_vec=[6, 60, 50], 
            area_threshold=2, 
            max_num_objects=max_num_objects,
            desired_fps=30
        )

        # capture_camera_frames(
        #     max_frames=10000, 
        #     camera_index=cameras[0], 
        #     HSV_vec=[120, 240, 60], 
        #     range_vec=[20, 100, 100], 
        #     area_threshold=1, 
        #     max_num_objects=4,
        #     desired_fps=10
        # )

    else:
        print("Error: No cameras available.")