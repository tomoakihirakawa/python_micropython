import cv2
import numpy as np
import time

def capture_camera_frames(interval=1, max_frames=10):
    # Open the default camera (usually the built-in webcam on a Mac)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open camera.")
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
    frames = capture_camera_frames(interval=0.1, max_frames=10000)
    print("Captured frames:", len(frames))
