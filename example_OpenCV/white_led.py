import cv2
import numpy as np
import time

def find_available_cameras():
    available_cameras = []
    for i in range(5):  # 調整が必要な場合は範囲を変更
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available_cameras.append(i)
            cap.release()
    return available_cameras

def extract_color_and_find_centroids(frame, HSV_ranges=[[0, 180], [0, 255], [200, 255]]):
    # 画像をBGRからHSVに変換
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # HSVの範囲を定義
    lower_bound = np.array([HSV_ranges[0][0], HSV_ranges[1][0], HSV_ranges[2][0]])
    upper_bound = np.array([HSV_ranges[0][1], HSV_ranges[1][1], HSV_ranges[2][1]])

    # HSV画像をしきい値処理して対象の色を抽出
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # マスクと元の画像をAND処理
    res = cv2.bitwise_and(frame, frame, mask=mask)

    # 形態学的処理
    kernel = np.ones((10, 10), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # 輪郭を見つけて重心を計算
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    centroids = []
    for c in contours:
        M = cv2.moments(c)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            centroids.append((cx, cy))

    return res, mask, centroids

def capture_camera_frames(interval=1, max_frames=10, camera_index=1, HSV_ranges=[[0, 180], [0, 255], [200, 255]]):
    # 指定したインデックスでカメラを開く
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print(f"Error: Could not open camera with index {camera_index}.")
        return

    frames = []

    for _ in range(max_frames):
        # フレームをキャプチャ
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # 対象色を抽出し、重心を見つける
        frame, mask, centroids = extract_color_and_find_centroids(frame, HSV_ranges)

        # フレームに重心を描画
        for centroid in centroids:
            cv2.circle(frame, centroid, 5, (0, 255, 0), -1)
            cv2.putText(frame, f"Centroid: {centroid}", (centroid[0] + 10, centroid[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # フレームリストに追加
        frames.append(frame)

        # 結果フレームを表示
        cv2.imshow('Frame', frame)

        # 指定した間隔だけ待機
        time.sleep(interval)

        # 'q'キーで早期終了
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # すべて終了したらキャプチャをリリース
    cap.release()
    cv2.destroyAllWindows()

    return frames

if __name__ == "__main__":
    cameras = find_available_cameras()
    if cameras:
        # HSVのしきい値範囲を設定（調整が必要）
        HSV_ranges = [[40, 80], [100, 255], [100, 255]]
        frames = capture_camera_frames(interval=0.001, max_frames=10000, camera_index=cameras[0], HSV_ranges=HSV_ranges)
    else:
        print("Error: No cameras available.")