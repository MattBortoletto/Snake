import pygame 
import numpy as np
import random
from enum import Enum
from collections import namedtuple

pygame.init()

class Direction(Enum):
  RIGHT = 1
  LEFT = 2
  UP = 3
  DOWN = 4

Point = namedtuple("Point", "x, y")

BLOCK_SIZE = 20
SPEED = 10

font = pygame.font.SysFont('arial', 25)

# RGB colors
WHITE = (255, 255, 255)
RED = (200, 0,0 )
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)

class SnakeGame:
  def __init__(self, w=640, h=480):
    # w: screen width
    # h: screen height
    self.w = w
    self.h = h
    # initialize display
    self.display = pygame.display.set_mode((self.w, self.h))
    pygame.display.set_caption("Snake")
    self.clock = pygame.time.Clock()
    # initial game state
    self.reset()
    print("init done")

  def reset(self):
    self.direction = Direction.RIGHT
    self.head = Point(self.w/2, self.h/2)
    self.snake = [self.head, 
                  Point(self.head.x-BLOCK_SIZE, self.head.y), 
                  Point(self.head.x-2*BLOCK_SIZE, self.head.y)]
    self.score = 0
    self.food = None 
    self._place_food()
    self.frame_iteration = 0
  
  def _place_food(self):
    x_food = random.randint(1, (self.w - BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
    y_food = random.randint(1, (self.h - BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
    self.food = Point(x_food, y_food)
    if self.food in self.snake:
      self._place_food()
  
  def play_step(self, action):
    # update frame iteration
    self.frame_iteration += 1
    # collect user input
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        quit()
    # move
    self._move(action)
    # add a block at the front
    self.snake.insert(0, self.head)
    # reward
    reward = 0 
    # check if game over
    game_over = False
    if self.is_collision() == True or self.frame_iteration > 100*len(self.snake):
      game_over = True
      reward = -10
      print("game over")
      return reward, game_over, self.score
    # place new food and/or move
    if self.head == self.food:
      self.score += 1 
      reward = 10
      self._place_food()
    else:
      # remove the block we added before at the front
      self.snake.pop()
    # update ui and clock 
    self._update_ui()
    self.clock.tick(SPEED)
    print("step played")
    # return game over and score
    return reward, game_over, self.score
    
  def is_collision(self, pt=None):
    if pt is None:
      pt = self.head
    if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y < 0 or pt.y > self.h - BLOCK_SIZE:
      return True
    if pt in self.snake[1:]:
      return True
    return False

  def _update_ui(self):
    self.display.fill(BLACK)
    for pt in self.snake:
      pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
      pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x, pt.y, 12, 12))
    pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
    text = font.render("Score: " + str(self.score), True, WHITE) 
    self.display.blit(text, [0,0])
    # update the display
    pygame.display.flip()

  def _move(self, action):
    # [straight, right, left]
    clock_wise_order = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
    current_direction_idx = clock_wise_order.index(self.direction)
    if np.array_equal(action, [1,0,0]):
      new_direction = clock_wise_order[current_direction_idx] # no change
    elif np.array_equal(action, [0,1,0]):
      new_idx = (current_direction_idx + 1) % 4 
      new_direction = clock_wise_order[new_idx] # right turn r -> d -> l -> u
    else: # [0,0,1]
      new_idx = (current_direction_idx - 1) % 4 
      new_direction = clock_wise_order[new_idx] # left turn r -> u -> l -> d
    self.direction = new_direction
    x = self.head.x
    y = self.head.y
    if self.direction == Direction.RIGHT: 
      x += BLOCK_SIZE
    if self.direction == Direction.LEFT: 
      x -= BLOCK_SIZE
    if self.direction == Direction.UP:
      y -= BLOCK_SIZE
    if self.direction == Direction.DOWN:
      y += BLOCK_SIZE
    self.head = Point(x, y)
