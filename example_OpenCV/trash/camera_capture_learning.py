import gymnasium as gym
from gymnasium import spaces
import numpy as np
import cv2

class FishRobotEnv(gym.Env):
    def __init__(self):
        super(FishRobotEnv, self).__init__()
        self.observation_space = spaces.Box(low=0, high=255, shape=(480, 640, 3), dtype=np.uint8)
        self.action_space = spaces.Discrete(4)  # 4つの動作：前進、後退、左折、右折
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Error: Could not open camera.")
        self.current_frame = None
        print("FishRobotEnv initialized. Camera opened successfully.")

    def step(self, action):
        action_meaning = {0: "Move forward", 1: "Move backward", 2: "Turn left", 3: "Turn right"}
        print(f"Action taken: {action} ({action_meaning[action]})")
        
        ret, frame = self.cap.read()
        if not ret:
            raise Exception("Error: Could not read frame.")
        
        self.current_frame = frame
        
        # TODO: actionに応じた魚ロボットの制御を実装する
        if action == 0:
            print("Command: Move forward")
            # Implement forward movement
        elif action == 1:
            print("Command: Move backward")
            # Implement backward movement
        elif action == 2:
            print("Command: Turn left")
            # Implement left turn
        elif action == 3:
            print("Command: Turn right")
            # Implement right turn
        
        # 仮の報酬とdoneフラグ
        reward = 0
        done = False
        
        return frame, reward, done, {}

    def reset(self):
        print("Resetting environment.")
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame
        return self.current_frame

    def render(self, mode='human'):
        if self.current_frame is not None:
            cv2.imshow('Frame', self.current_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.close()

    def close(self):
        print("Closing environment.")
        if self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()

from gymnasium import make

env = FishRobotEnv()

num_episodes = 10

for episode in range(num_episodes):
    print(f"Episode {episode+1}/{num_episodes} started.")
    observation = env.reset()
    done = False
    step_count = 0
    
    while not done:
        step_count += 1
        action = env.action_space.sample()  # ランダムなアクションを選択
        observation, reward, done, info = env.step(action)
        print(f"Step {step_count}: Action = {action}, Reward = {reward}, Done = {done}")
        env.render()

env.close()
