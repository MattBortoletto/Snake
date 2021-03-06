import torch
import random 
import numpy as np 
from snake_rl import SnakeGame, Direction, Point
from collections import deque
from model import LinearQNet, QTrainer
from plotter import live_plot_scores


MAX_MEMORY = 100000
BATCH_SIZE = 1000
LR = 0.001
BLOCK_SIZE = 20

class Agent:
  def __init__(self):
    self.n_games = 0
    self.epsilon = 0 # randomness
    self.gamma = 0.9 # discount
    self.memory = deque(maxlen=MAX_MEMORY)
    self.model = LinearQNet(11, 256, 3)
    self.trainer = QTrainer(self.model, LR, self.gamma)
  
  def load_model(self, model_path='./model/model.pth'):
    self.model.load_state_dict(torch.load(model_path))
    print("Model loaded.")

  def get_state(self, game):
    head = game.snake[0]
    # points around the head
    point_l = Point(head.x - BLOCK_SIZE, head.y)
    point_r = Point(head.x + BLOCK_SIZE, head.y)
    point_u = Point(head.x, head.y - BLOCK_SIZE)
    point_d = Point(head.x, head.y + BLOCK_SIZE)
    # directions
    dir_l = game.direction == Direction.LEFT
    dir_r = game.direction == Direction.RIGHT
    dir_u = game.direction == Direction.UP
    dir_d = game.direction == Direction.DOWN
    state = [
          # check if danger is straight
          (dir_r and game.is_collision(point_r)) or 
          (dir_l and game.is_collision(point_l)) or 
          (dir_u and game.is_collision(point_u)) or 
          (dir_d and game.is_collision(point_d)),  
          # check if danger is right
          (dir_u and game.is_collision(point_r)) or 
          (dir_d and game.is_collision(point_l)) or 
          (dir_l and game.is_collision(point_u)) or 
          (dir_r and game.is_collision(point_d)), 
          # check if danger is left
          (dir_d and game.is_collision(point_r)) or 
          (dir_u and game.is_collision(point_l)) or 
          (dir_r and game.is_collision(point_u)) or 
          (dir_l and game.is_collision(point_d)),   
          # move direction
          dir_l, dir_r, dir_u, dir_d,
          # food location
          game.food.x < game.head.x, # food left
          game.food.x > game.head.x, # food right
          game.food.y > game.head.y, # food down
          game.food.y < game.head.y  # food up
        ]
    return np.array(state, dtype=int)


  def remember(self, state, action, reward, next_state, done):
    self.memory.append((state, action, reward, next_state, done))

  def train_long_memory(self):
    if len(self.memory) > BATCH_SIZE:
      sample = random.sample(self.memory, BATCH_SIZE)
    else:
      sample = self.memory
    states, actions, rewards, next_states, dones = zip(*sample)
    self.trainer.train_step(states, actions, rewards, next_states, dones)

  def train_short_memory(self, state, action, reward, next_state, done):
    self.trainer.train_step(state, action, reward, next_state, done)

  def get_action(self, state, greedy=True):
    if greedy:
      # epsilon greedy policy
      self.epsilon = 80 - self.n_games
    final_move = [0,0,0]
    if random.randint(0, 200) < self.epsilon:
      move = random.randint(0, 2)
      final_move[move] = 1
    else:
      state0 = torch.tensor(state, dtype=torch.float)
      prediction = self.model(state0)
      # ex: prediction = [3, 1, 0.5] -> get the maximum index
      move = torch.argmax(prediction).item()
      final_move[move] = 1
    return final_move


def train():
  print("Training...")
  plot_scores = []
  plot_mean_scores = []
  total_score = 0
  record = 0
  agent = Agent()
  game = SnakeGame()
  while True:
    # get current state
    current_state = agent.get_state(game)
    # get move
    final_move = agent.get_action(current_state)
    # perform move and get new state
    reward, done, score = game.play_step(final_move)
    new_state = agent.get_state(game)
    # trin short term memory
    agent.train_short_memory(current_state, final_move, reward, new_state, done)
    # remember
    agent.remember(current_state, final_move, reward, new_state, done)
    if done:
      # train long memory (experience replay)
      game.reset()
      agent.n_games += 1
      agent.train_long_memory()
      if score > record:
        record = score
        agent.model.save()
        print("Model saved.")
      print("Game number:", agent.n_games, "\tScore:", score, "\tRecord:", record)
      plot_scores.append(score)
      total_score += score
      plot_mean_scores.append(total_score / agent.n_games)
      live_plot_scores(plot_scores, plot_mean_scores)

def play():
  record = 0
  agent = Agent()
  game = SnakeGame()
  agent.load_model()
  while True:
    current_state = agent.get_state(game)
    next_move = agent.get_action(current_state, greedy=False)
    reward, done, score = game.play_step(next_move)
    if done:
      if score > record:
        record = score
      game.reset()
      print("Game over! Score:", score, "\tRecord:", record)
  
if __name__ == "__main__":
  train() 
  #play()

