# pip install gymnasium
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import matplotlib.pyplot as plt

# Observation space
xmin, xmax = 0, 10
ymin, ymax = 0, 10
x_discrete_size = 21
y_discrete_size = 21
vel_min, vel_max = -2., 2.
vel_discrete_size = 11

# Action space
acc_min, acc_max = -4., 4.
acc_discrete_size = 11
center_index = round(acc_discrete_size / 2)

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
        self.dt = 0.1
        self.checkpoints = [
            # ((1, 1), (3, 3)),  
            ((4, 1), (6, 3)),
            ((7, 1), (9, 3)),
            ((7, 7), (9, 9)),
            ((1, 7), (3, 9))
        ]
        self.action_space = spaces.Box(
            low=np.array([acc_min, acc_min]), 
            high=np.array([acc_max, acc_max]), 
            dtype=np.float32
        )
        self.observation_space = spaces.Box(
            low=np.array([xmin, ymin, vel_min, vel_min, 0]),
            high=np.array([xmax, ymax, vel_max, vel_max, len(self.checkpoints)]),
            dtype=np.float32
        )
        self.current_checkpoint_index = 0
        self.fig, (self.ax, self.ax_reward) = plt.subplots(1, 2, figsize=(12, 5))
        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.state = np.array([1.0, 1.0, 0.0, 0.0, 0])
        self.current_checkpoint_index = 0
        self.trajectory = [self.state.copy()]
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.acc_x = 0.0
        self.acc_y = 0.0
        self.moved_distance = 0.0
        self.steps = 0
        self.steps_from_last = 0
        self.initial_action = np.array([0.0, 0.0])  # 初期のアクションを設定
        self.step_rewards = []  # Initialize step rewards list
        return self.state, {}

    def step(self, action):
        x, y, vel_x, vel_y, _ = self.state
        acc_x, acc_y = action

        self.acc_x = np.clip(acc_x, acc_min, acc_max)
        self.acc_y = np.clip(acc_y, acc_min, acc_max)

        self.vel_x += acc_x * self.dt
        self.vel_y += acc_y * self.dt

        self.vel_x = np.clip(self.vel_x, vel_min, vel_max) 
        self.vel_y = np.clip(self.vel_y, vel_min, vel_max)

        x += self.vel_x * self.dt
        y += self.vel_y * self.dt

        reward = self._calculate_reward(x, y)
        self.step_rewards.append(reward)  # Append reward for each step

        self.state = np.array([x, y, self.vel_x, self.vel_y, self.current_checkpoint_index])
        self.trajectory.append(self.state.copy())

        done = self._check_done(x, y)
        return self.state, reward, done, False, {}

    def _check_done(self, x, y):
        return x < 0 or x > 10 or y < 0 or y > 10 or self.in_obstacle(x, y) or self.current_checkpoint_index > 5

    def in_obstacle(self, x, y):
        return 4.0 < x < 6.0 and 4.0 < y < 6.0

    def reached_checkpointQ(self, x, y):
        checkpoint_min, checkpoint_max = self.checkpoints[self.current_checkpoint_index]
        return checkpoint_min[0] <= x <= checkpoint_max[0] and checkpoint_min[1] <= y <= checkpoint_max[1]

    def _calculate_reward(self, x, y):
        reward = 0

        self.steps_from_last += 1
        checkpoint_min, checkpoint_max = self.checkpoints[self.current_checkpoint_index]
        vector_to_checkpoint = ((np.array(checkpoint_min) + np.array(checkpoint_max)) / 2. - np.array([x, y]))
        norm = np.linalg.norm(vector_to_checkpoint)
        if norm > 0:
            vector_to_checkpoint /= norm
            # reward += np.dot(vector_to_checkpoint, np.array([self.vel_x, self.vel_y]))
        reward -= np.linalg.norm([self.acc_x, self.acc_y])*0.5
        reward -= 0.01

        if self.in_obstacle(x, y):
            reward -= 100/(self.current_checkpoint_index+1) * np.linalg.norm([self.vel_x, self.vel_y])
        else:
            if self.reached_checkpointQ(x, y):
                self.current_checkpoint_index = (self.current_checkpoint_index + 1) % len(self.checkpoints)
                reward += self.current_checkpoint_index*1000
                self.steps_from_last = 0

                if self.current_checkpoint_index > 5:
                    reward += 100

        return reward

    def render(self, mode='human'):
        if mode == 'human':
            self.ax.clear()
            trajectory = np.array(self.trajectory)
            self.ax.plot(trajectory[:, 0], trajectory[:, 1], 'b-')
            x, y, vel_x, vel_y, _ = self.state
            dx = self.vel_x * 0.1
            dy = self.vel_y * 0.1
            self.arrow = self.ax.arrow(x, y, dx, dy, head_width=0.1, head_length=0.1, fc='r', ec='r')
            self.ax.set_xlim(0, 10)
            self.ax.set_ylim(0, 10)
            self.ax.add_patch(plt.Rectangle((4, 4), 2, 2, fill=True, color='grey'))
            for i, (cp_min, cp_max) in enumerate(self.checkpoints):
                color = 'green' if i != self.current_checkpoint_index else 'blue'
                self.ax.add_patch(plt.Rectangle(cp_min, cp_max[0] - cp_min[0], cp_max[1] - cp_min[1], fill=True, color=color, alpha=0.3))
            self.ax.set_title('Car Robot Path')
            self.ax.set_xlabel('X position')
            self.ax.set_ylabel('Y position')
            self.ax.grid()
            
            # Plot the rewards on the right subplot
            self.ax_reward.clear()
            self.ax_reward.bar(range(len(self.step_rewards)), self.step_rewards, color='blue')
            # self.ax_reward.set_title('Step Rewards')
            self.ax_reward.set_title(f"Step {env.steps}: State: {self.state}")
            self.ax_reward.set_xlabel('Step')
            self.ax_reward.set_ylabel('Reward')
            
            self.fig.canvas.draw()
            plt.pause(0.0002)

    def close(self):
        plt.close()

def discretize_state(state):
    x, y, vel_x, vel_y, index = state
    return (real2index(x, xmin, xmax, x_discrete_size),
            real2index(y, ymin, ymax, y_discrete_size),
            real2index(vel_x, acc_min, acc_max, acc_discrete_size),
            real2index(vel_y, acc_min, acc_max, acc_discrete_size),
            int(index))

def discretize_action(action):
    acc_x, acc_y = action
    return (real2index(acc_x, acc_min, acc_max, acc_discrete_size),
            real2index(acc_y, acc_min, acc_max, acc_discrete_size))

def undiscretize_action(action_discrete):
    acc_x_discrete, acc_y_discrete = action_discrete
    return (index2real(acc_x_discrete, acc_min, acc_max, acc_discrete_size),
            index2real(acc_y_discrete, acc_min, acc_max, acc_discrete_size))

# Training function
def train(env, max_steps, episodes, epsilon, alpha, gamma):
    discretized_state_space = (x_discrete_size, y_discrete_size, vel_discrete_size, vel_discrete_size, len(env.checkpoints))
    action_space_size = (acc_discrete_size, acc_discrete_size)
    q_table = np.zeros(discretized_state_space + action_space_size)

    # Initialize Q-table with the central value
    q_table[:, :, :, :, :, center_index, center_index] = 0.5

    rewards = []
    episode_lengths = []

    for episode in range(episodes):
        state, _ = env.reset()
        state_discrete = discretize_state(state)
        done = False
        total_reward = 0
        env.steps = 0

        while not done:
            if episode % 1000 == 0:
                env.render()
            if np.random.rand() < epsilon:
                action = env.action_space.sample()
                action_discrete = discretize_action(action)
            else:
                action_discrete = np.unravel_index(q_table[state_discrete].argmax(), q_table[state_discrete].shape)
                action = undiscretize_action(action_discrete)

            next_state, reward, done, _, _ = env.step(action)
            next_state_discrete = discretize_state(next_state)
            best_next_action = q_table[next_state_discrete].max()
            q_table[state_discrete + action_discrete] = (
                (1 - alpha) * q_table[state_discrete + action_discrete] + alpha * (reward + gamma * best_next_action)
            )
            state_discrete = next_state_discrete
            total_reward += reward
            env.steps += 1
            if env.steps > max_steps:
                break

        rewards.append(total_reward)
        episode_lengths.append(env.steps)
        if episode % 100 == 0:
            print(f"Episode {episode + 1}: Total Reward: {total_reward}, Steps: {env.steps}")

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

if __name__ == "__main__":
    env = CarRobotEnv()
    train(env, max_steps = 200, episodes=100000, epsilon=0.3, alpha=0.3, gamma=0.99)
    env.close()
