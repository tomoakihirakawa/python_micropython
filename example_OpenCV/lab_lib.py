import numpy as np
import cv2
import math

def capture_and_split_frames(cap):
    ret, frame = cap.read()
    if not ret:
        return None, None
    height, width = frame.shape[:2]
    L_frame = frame[:, :width // 2]
    R_frame = frame[:, width // 2:]
    return ret, R_frame, L_frame

def adjust_hue_bounds(hue, range_val):
    lower_hue = (hue - range_val) % 180
    upper_hue = (hue + range_val) % 180
    if lower_hue > upper_hue:
        return [(0, upper_hue), (lower_hue, 179)]
    return [(lower_hue, upper_hue)]

def find_available_cameras(max_range=5):
    available_cameras = [i for i in range(max_range) if cv2.VideoCapture(i).isOpened()]
    for i in available_cameras:
        cv2.VideoCapture(i).release()
    return available_cameras

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

def extract_centroids(contours, area_threshold, max_objects):
    centroids = [(int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])) for c in contours if (M := cv2.moments(c))["m00"] != 0 and cv2.contourArea(c) > area_threshold]
    return sorted(centroids, key=lambda x: x[1], reverse=True)[:max_objects]

def draw_centroids(frame, centroids):
    for cx, cy in centroids:
        cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
        cv2.putText(frame, f"Centroid: ({cx}, {cy})", (cx + 10, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

def getEstimatedPosition(p,q,f=1.8, b=60., Ry=1280., Rz=720.,HFOV=120., aspect_ratio=16./9.):
    # この変換は，ピンホールカメラモデルを仮定して，カメラの後ろ側にある面に投影された光源の位置を計算するものである．
    # カメラを前から見て，左下が原点で，右がx軸の正方向，上がy軸の正方向，手前がz軸の正方向となるような座標系を仮定している．
    [py,pz] = p
    [qy,qz] = q
    eps = 10.**-20    
    v1x = (b * Ry)/(2 * math.tan(HFOV/180. * math.pi / 2.) * (-py + qy + eps))
    v1y = (2*b*py - b*Ry)/(2*py - 2*qy + eps)
    v1z = (b * Ry * (pz + qz - Rz))/(2 *aspect_ratio* (py - qy + eps) *Rz)    
    return np.array([v1x, v1y, v1z])

# ---------------------------------------------------------------------------- #


def gamma_correction(image, gamma=1.0):
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)

def process_mask(mask):
    # Define kernels
    kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
    kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20))
    
    # Apply morphological operations
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_open)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_close)
    return mask

def equalize_histogram_color_image(image):
    # カラー画像をYUVカラースペースに変換
    yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    
    # 輝度チャンネル（Y）にヒストグラム均一化を適用
    yuv[:,:,0] = cv2.equalizeHist(yuv[:,:,0])
    
    # YUVカラースペースからBGRカラースペースに戻す
    equalized_image = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
    
    return equalized_image


def extract_color_and_find_centroids(frame, HSV_vec, range_vec, area_threshold, max_num_objects):
    # frame = gamma_correction(frame, gamma=1.5)
    # frame = equalize_histogram_color_image(frame)
    
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hue_bounds = adjust_hue_bounds(HSV_vec[0], range_vec[0])
    mask = create_mask(hsv_frame, hue_bounds, HSV_vec, range_vec)
    mask = process_mask(mask)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # コンツアを面積順に並べ替える
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Filter contours by area and shape
    centroids = []
    for contour in contours:
        if cv2.contourArea(contour) >= area_threshold:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                centroids.append((cX, cY))
            if len(centroids) >= max_num_objects:
                break

    return frame, mask, hsv_frame, centroids
