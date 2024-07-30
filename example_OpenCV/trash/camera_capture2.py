import cv2
import numpy as np
import time

for i in range(5):  # Adjust the range as needed
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Camera index {i} is available.")
        cap.release()


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

        if not ret:
            print("Error: Could not read frame.")
            break

        # Convert the frame to a data array (numpy array)
        frame_array = np.array(frame)

        # Append the frame array to the list of frames
        frames.append(frame_array)

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
    frames = capture_camera_frames(interval=0.01, max_frames=100000, camera_index=0)
    print("Captured frames:", len(frames))
