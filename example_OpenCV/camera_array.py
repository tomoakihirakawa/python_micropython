import cv2
import numpy as np
import time

cap = cv2.VideoCapture(0)

def capture_camera_frames(interval=1, max_frames=10):
    global cap
    
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return []

    frames = []

    for _ in range(max_frames):
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            print("Error: Could not read frame.")
            break

        # Convert the frame to a data array (numpy array)
        frame_array = np.array(frame)

        # Convert to int32 to avoid overflow, then sum the RGB channels
        frame_sum = frame_array.astype(np.int32).sum(axis=2)
        
        # Create a mask where the sum of RGB values is greater than 100
        mask = frame_sum > 600
        
        # Set the RGB values to 100 where the mask is True
        frame_array[mask] = [100, 100, 100]

        # Append the modified frame array to the list of frames
        frames.append(frame_array)

        # Display the resulting frame
        cv2.imshow('Frame', frame_array)

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
    # Capture frames from the camera
    frames = capture_camera_frames(interval=0.1, max_frames=100)
    print("Captured frames:", len(frames))

    # Example of accessing the data array
    if frames:
        # Get the first frame as a numpy array
        first_frame = frames[0]

        # Print the shape of the first frame to understand its dimensions
        print("Shape of the first frame:", first_frame.shape)
