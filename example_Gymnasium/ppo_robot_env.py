# pip install gymnasium
# pip install stable-baselines3

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.vec_env import DummyVecEnv

# Observation space
xmin, xmax = 0, 10
ymin, ymax = 0, 10
qmin, qmax = -np.pi, np.pi

# Action space
linear_acc_min, linear_acc_max = 0.0, 1.0
rotational_acc_min, rotational_acc_max = -1.0, 1.0

class CarRobotEnv(gym.Env):  # Ensure it inherits from gym.Env
    def __init__(self):
        super(CarRobotEnv, self).__init__()
        self.action_space = spaces.Box(low=np.array([linear_acc_min, rotational_acc_min]), high=np.array([linear_acc_max, rotational_acc_max]), dtype=np.float32)
        self.observation_space = spaces.Box(low=np.array([xmin, ymin, qmin]), high=np.array([xmax, ymax, qmax]), dtype=np.float32)
        self.dt = 0.1
        self.checkpoints = [
            ((1, 1), (3, 3)),
            ((7, 1), (9, 3)),
            ((7, 7), (9, 9)),
            ((1, 7), (3, 9))
        ]
        self.current_checkpoint_index = 0
        self.goal = (5, 5)
        self.reset()
        self.fig, self.ax = plt.subplots()
        self.arrow = None
        self.prev_distance_to_checkpoint = None
        self.linear_vel = 0.0
        self.rotational_vel = 0.0
        self.moved_distance = 0.0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.state = np.array([1.0, 1.0, 0.0])
        self.current_checkpoint_index = 0
        self.trajectory = [self.state.copy()]
        self.prev_distance_to_checkpoint = None
        self.linear_vel = 0.0
        self.rotational_vel = 0.0
        self.moved_distance = 0.0
        return self.state, {}

    def step(self, action):
        x, y, theta = self.state
        linear_acc, rotational_acc = action

        self.linear_vel += linear_acc * self.dt
        self.rotational_vel += rotational_acc * self.dt

        self.linear_vel -= 0.01 * self.linear_vel
        self.rotational_vel -= 0.01 * self.rotational_vel

        theta += self.rotational_vel * self.dt

        x += self.linear_vel * np.cos(theta)
        y += self.linear_vel * np.sin(theta)
        self.state = np.array([x, y, theta])
        self.trajectory.append(self.state.copy())
        done = x < 0 or x > 10 or y < 0 or y > 10 or self.in_obstacle(x, y) or self.reached_goal(x, y)
        reward = self.calculate_reward(x, y, theta, linear_acc, rotational_acc)
        return self.state, reward, done, False, {}

    def in_obstacle(self, x, y):
        return 4.0 < x < 6.0 and 4.0 < y < 6.0

    def reached_goal(self, x, y):
        return np.linalg.norm(np.array([x, y]) - np.array(self.goal)) < 0.5

    def Dot(self, v1, v2):
        return sum((a * b) for a, b in zip(v1, v2))

    def calculate_reward(self, x, y, theta, linear_acc, rotational_acc):
        checkpoint_min, checkpoint_max = self.checkpoints[self.current_checkpoint_index]
        checkpoint_center = np.array([(checkpoint_min[0] + checkpoint_max[0]) / 2, (checkpoint_min[1] + checkpoint_max[1]) / 2])
        vector_to_checkpoint = checkpoint_center - np.array([x, y])
        vector_to_checkpoint /= np.linalg.norm(vector_to_checkpoint)
        velocity_vector = self.linear_vel * np.array([np.cos(theta), np.sin(theta)])
        self.moved_distance += np.linalg.norm(velocity_vector * self.dt)
        reward = self.moved_distance
        reward += 5 * self.Dot(vector_to_checkpoint, velocity_vector)

        if self.in_obstacle(x, y):
            reward = -10
        elif self.reached_goal(x, y):
            reward = 100
        else:
            if checkpoint_min[0] <= x <= checkpoint_max[0] and checkpoint_min[1] <= y <= checkpoint_max[1]:
                reward = 30
                self.current_checkpoint_index = (self.current_checkpoint_index + 1) % len(self.checkpoints)
                self.prev_distance_to_checkpoint = None

        reward = np.clip(reward, -100, 100)

        return reward

    def render(self, mode='human'):
        if mode == 'human':
            self.ax.clear()
            trajectory = np.array(self.trajectory)
            self.ax.plot(trajectory[:, 0], trajectory[:, 1], 'b-')
            x, y, theta = self.state
            dx = np.cos(theta) * 0.5
            dy = np.sin(theta) * 0.5
            if self.arrow:
                self.arrow.remove()
            self.arrow = self.ax.arrow(x, y, dx, dy, head_width=0.1, head_length=0.1, fc='r', ec='r')
            self.ax.set_xlim(0, 10)
            self.ax.set_ylim(0, 10)
            self.ax.add_patch(plt.Rectangle((4, 4), 2, 2, fill=True, color='grey'))
            for i, (cp_min, cp_max) in enumerate(self.checkpoints):
                color = 'green' if i != self.current_checkpoint_index else 'blue'
                self.ax.add_patch(plt.Rectangle(cp_min, cp_max[0]-cp_min[0], cp_max[1]-cp_min[1], fill=True, color=color, alpha=0.3))
            self.ax.scatter(*self.goal, color='red')
            self.ax.set_title('Car Robot Path')
            self.ax.set_xlabel('X position')
            self.ax.set_ylabel('Y position')
            self.ax.grid()
            self.fig.canvas.draw()
            plt.pause(0.01)

    def close(self):
        plt.close()

# Check the environment
env = DummyVecEnv([lambda: CarRobotEnv()])
check_env(env)

# Train the model
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=10000)

# Evaluate the model
obs, _ = env.reset()
for i in range(1000):
    action, _states = model.predict(obs)
    obs, rewards, done, _ = env.step(action)
    env.envs[0].render()
    if done:
        obs, _ = env.reset()

env.close()
