# pip install gymnasium
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import matplotlib.pyplot as plt

# Observation space
xmin, xmax = 0, 10
ymin, ymax = 0, 10
x_discrete_size = 11
y_discrete_size = 11

# Action space
linear_acc_min, linear_acc_max = -5., 5.
linear_acc_discrete_size = 11
center_index = round(linear_acc_discrete_size / 2)

def real2index(x, xmin, xmax, x_discrete_size):
    x = np.clip(x, xmin, xmax)
    dL = (xmax - xmin) / (x_discrete_size - 1)
    return round((x - xmin) / dL)

def index2real(x_discrete, xmin, xmax, x_discrete_size):
    dL = (xmax - xmin) / (x_discrete_size - 1)
    return np.clip(x_discrete * dL + xmin, xmin, xmax)

class CarRobotEnv(gym.Env):
    def __init__(self):
        super(CarRobotEnv, self).__init__()
        self.action_space = spaces.Box(
            low=np.array([linear_acc_min, linear_acc_min]), 
            high=np.array([linear_acc_max, linear_acc_max]), 
            dtype=np.float32
        )
        self.observation_space = spaces.Box(
            low=np.array([xmin, ymin]), 
            high=np.array([xmax, ymax]), 
            dtype=np.float32
        )
        self.dt = 0.1
        self.checkpoints = [
            # ((1, 1), (3, 3)),  
            ((7, 1), (9, 3)),
            ((7, 7), (9, 9)),
            ((1, 7), (3, 9))
        ]
        self.current_checkpoint_index = 0
        self.goal = np.array([5, 5])
        self.fig, self.ax = plt.subplots()
        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.state = np.array([1.0, 1.0]) 
        self.current_checkpoint_index = 0
        self.trajectory = [self.state.copy()]
        self.linear_vel_x = 0.0
        self.linear_vel_y = 0.0
        self.moved_distance = 0.0
        self.initial_action = np.array([0.0, 0.0])  # 初期のアクションを設定
        return self.state, {}

    def step(self, action):
        x, y = self.state
        linear_acc_x, linear_acc_y = action
        
        self.linear_vel_x += linear_acc_x * self.dt
        self.linear_vel_y += linear_acc_y * self.dt

        x += self.linear_vel_x * self.dt
        y += self.linear_vel_y * self.dt
        self.state = np.array([x, y])
        self.trajectory.append(self.state.copy())
        done = self._check_done(x, y)
        reward = self._calculate_reward(x, y)
        return self.state, reward, done, False, {}

    def _check_done(self, x, y):
        return x < 0 or x > 10 or y < 0 or y > 10 or self.in_obstacle(x, y) or self.reached_goal(x, y)

    def in_obstacle(self, x, y):
        return 4.0 < x < 6.0 and 4.0 < y < 6.0

    def reached_goal(self, x, y):
        return np.linalg.norm(np.array([x, y]) - self.goal) < 0.5

    def _calculate_reward(self, x, y):
        checkpoint_min, checkpoint_max = self.checkpoints[self.current_checkpoint_index]
        checkpoint_center = (np.array(checkpoint_min) + np.array(checkpoint_max)) / 2
        vector_to_checkpoint = checkpoint_center - np.array([x, y])
        vector_to_checkpoint /= np.linalg.norm(vector_to_checkpoint)
        velocity_vector = np.array([self.linear_vel_x, self.linear_vel_y])

        # reward = np.dot(vector_to_checkpoint, velocity_vector)
        reward = np.dot(vector_to_checkpoint, velocity_vector)/np.linalg.norm(vector_to_checkpoint)+1
        # reward -= np.linalg.norm(velocity_vector)

        if self.in_obstacle(x, y):
            reward = -100
        elif self.reached_goal(x, y):
            reward = 100
        else:
            if checkpoint_min[0] <= x <= checkpoint_max[0] and checkpoint_min[1] <= y <= checkpoint_max[1]:
                reward = 100
                self.current_checkpoint_index = (self.current_checkpoint_index + 1) % len(self.checkpoints)

        # return np.clip(reward, -1000, 1000)
        return reward

    def render(self, mode='human'):
        if mode == 'human':
            self.ax.clear()
            trajectory = np.array(self.trajectory)
            self.ax.plot(trajectory[:, 0], trajectory[:, 1], 'b-')
            x, y = self.state
            dx = self.linear_vel_x * 0.1
            dy = self.linear_vel_y * 0.1
            self.arrow = self.ax.arrow(x, y, dx, dy, head_width=0.1, head_length=0.1, fc='r', ec='r')
            self.ax.set_xlim(0, 10)
            self.ax.set_ylim(0, 10)
            self.ax.add_patch(plt.Rectangle((4, 4), 2, 2, fill=True, color='grey'))
            for i, (cp_min, cp_max) in enumerate(self.checkpoints):
                color = 'green' if i != self.current_checkpoint_index else 'blue'
                self.ax.add_patch(plt.Rectangle(cp_min, cp_max[0] - cp_min[0], cp_max[1] - cp_min[1], fill=True, color=color, alpha=0.3))
            self.ax.scatter(*self.goal, color='red')
            self.ax.set_title('Car Robot Path')
            self.ax.set_xlabel('X position')
            self.ax.set_ylabel('Y position')
            self.ax.grid()
            self.fig.canvas.draw()
            plt.pause(0.01)

    def close(self):
        plt.close()

def train(env, episodes=1000, epsilon=0.2, alpha=0.3, gamma=0.99):
    discretized_state_space = (x_discrete_size, y_discrete_size)
    action_space_size = (linear_acc_discrete_size, linear_acc_discrete_size)
    q_table = np.zeros(discretized_state_space + action_space_size)
    
    # 中央の値でQテーブルを初期化
    q_table[:, :, center_index, center_index] = 0.5

    rewards = []
    episode_lengths = []

    for episode in range(episodes):
        state, _ = env.reset()
        state_discrete = discretize_state(state)
        done = False
        total_reward = 0
        steps = 0

        while not done:
            env.render()
            if steps == 0:
                action = env.initial_action  # 初期ステップでのアクションを設定
                action_discrete = discretize_action(action)
            elif np.random.rand() < epsilon:
                action = env.action_space.sample()
                action_discrete = discretize_action(action)
            else:
                action_discrete = np.unravel_index(q_table[state_discrete].argmax(), q_table[state_discrete].shape)
                action = undiscretize_action(action_discrete)

            # monitor the action
            # print(f"Episode {episode + 1}, Step {steps + 1}: Action: {action}, Discrete Action: {action_discrete}/{linear_acc_discrete_size}")

            next_state, reward, done, _, _ = env.step(action)
            next_state_discrete = discretize_state(next_state)
            best_next_action = q_table[next_state_discrete].max()
            q_table[state_discrete][action_discrete] = (1 - alpha) * q_table[state_discrete][action_discrete] + alpha * (reward + gamma * best_next_action)
            state_discrete = next_state_discrete
            total_reward += reward
            steps += 1

        rewards.append(total_reward)
        episode_lengths.append(steps)
        print(f"Episode {episode + 1}: Total Reward: {total_reward}, Steps: {steps}")

    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(rewards)
    plt.title('Episode Reward Over Time')
    plt.xlabel('Episode')
    plt.ylabel('Total Reward')
    plt.subplot(1, 2, 2)
    plt.plot(episode_lengths)
    plt.title('Episode Length Over Time')
    plt.xlabel('Episode')
    plt.ylabel('Episode Length')
    plt.show()

def discretize_state(state):
    x, y = state
    x_discrete = real2index(x, xmin, xmax, x_discrete_size)
    y_discrete = real2index(y, ymin, ymax, y_discrete_size)
    return (x_discrete, y_discrete)

def discretize_action(action):
    linear_acc_x, linear_acc_y = action
    linear_acc_x_discrete = real2index(linear_acc_x, linear_acc_min, linear_acc_max, linear_acc_discrete_size)
    linear_acc_y_discrete = real2index(linear_acc_y, linear_acc_min, linear_acc_max, linear_acc_discrete_size)
    return (linear_acc_x_discrete, linear_acc_y_discrete)

def undiscretize_action(action_discrete):
    linear_acc_x_discrete, linear_acc_y_discrete = action_discrete
    linear_acc_x = index2real(linear_acc_x_discrete, linear_acc_min, linear_acc_max, linear_acc_discrete_size)
    linear_acc_y = index2real(linear_acc_y_discrete, linear_acc_min, linear_acc_max, linear_acc_discrete_size)
    return (linear_acc_x, linear_acc_y)

if __name__ == "__main__":
    env = CarRobotEnv()
    train(env, episodes=1000, epsilon=0.2, alpha=0.1, gamma=0.9)
    env.close()
