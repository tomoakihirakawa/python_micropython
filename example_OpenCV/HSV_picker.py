'''DOC_EXTRACT

# OpenCV

## HSV Picker（映像のHSV色空間を確認できる）

トラックバーを使ってHSV色空間の各パラメータを調整し，
それに基づき，カメラ映像のマスク処理を行う．
カメラに映る物体のHSV色空間パラメタを確認することができる．

![HSV Picker](./hsv_picker.png)

'''

import cv2
import numpy as np

def nothing(x):
    pass

# トラックバーとウィンドウを作成
# set size of the window
window_title = 'choose H center, H range, S lower, S upper, V lower, V upper, Open K S, Close K S'
cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
cv2.createTrackbar('H Center', window_title, 0, 179, nothing)
cv2.createTrackbar('H Range', window_title, 10, 90, nothing)
cv2.createTrackbar('S Lower', window_title, 0, 255, nothing)
cv2.createTrackbar('S Upper', window_title, 255, 255, nothing)
cv2.createTrackbar('V Lower', window_title, 0, 255, nothing)
cv2.createTrackbar('V Upper', window_title, 255, 255, nothing)
cv2.createTrackbar('Open K Size', window_title, 1, 21, nothing)
cv2.createTrackbar('Close K Size', window_title, 1, 21, nothing)

# カメラを開く
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

while True:
    # フレームをキャプチャする
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    # 画像をBGRからHSVに変換する
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    cv2.waitKey(20)
    # トラックバーの位置を取得
    h_center = cv2.getTrackbarPos('H Center', window_title)
    h_range = cv2.getTrackbarPos('H Range', window_title)
    s_lower = cv2.getTrackbarPos('S Lower', window_title)
    s_upper = cv2.getTrackbarPos('S Upper', window_title)
    v_lower = cv2.getTrackbarPos('V Lower', window_title)
    v_upper = cv2.getTrackbarPos('V Upper', window_title)    
    open_kernel_size = cv2.getTrackbarPos('Open K Size', window_title)
    close_kernel_size = cv2.getTrackbarPos('Close K Size', window_title)
    cv2.waitKey(20)

    # カーネルサイズは奇数にする
    if open_kernel_size % 2 == 0:
        open_kernel_size += 1
    if close_kernel_size % 2 == 0:
        close_kernel_size += 1

    # HSV範囲を適用してマスクを作成
    lower_bound1 = np.array([max(0, h_center - h_range), s_lower, v_lower])
    upper_bound1 = np.array([min(179, h_center + h_range), s_upper, v_upper])
    mask1 = cv2.inRange(hsv_frame, lower_bound1, upper_bound1)

    # 赤色を扱うための特別な範囲設定
    if h_center - h_range < 0:
        lower_bound2 = np.array([h_center - h_range + 179, s_lower, v_lower])
        upper_bound2 = np.array([179, s_upper, v_upper])
        mask2 = cv2.inRange(hsv_frame, lower_bound2, upper_bound2)
        mask1 = cv2.bitwise_or(mask1, mask2)

    if h_center + h_range > 179:
        lower_bound2 = np.array([0, s_lower, v_lower])
        upper_bound2 = np.array([h_center + h_range - 179, s_upper, v_upper])
        mask2 = cv2.inRange(hsv_frame, lower_bound2, upper_bound2)
        mask1 = cv2.bitwise_or(mask1, mask2)

    # オープニングとクロージングのカーネルを作成
    open_kernel = np.ones((open_kernel_size, open_kernel_size), np.uint8)
    close_kernel = np.ones((close_kernel_size, close_kernel_size), np.uint8)

    # オープニングとクロージングを適用
    mask1 = cv2.morphologyEx(mask1, cv2.MORPH_OPEN, open_kernel)
    mask1 = cv2.morphologyEx(mask1, cv2.MORPH_CLOSE, close_kernel)

    result = cv2.bitwise_and(frame, frame, mask=mask1)

    # 画像を表示
    cv2.waitKey(20)
    cv2.imshow('Original Frame', frame)
    cv2.imshow('Mask', mask1)
    cv2.imshow('Masked Result', result)

    # 遅延を加えてトラックバーの変更を反映させる
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

# リソースを解放する
cap.release()
cv2.destroyAllWindows()
