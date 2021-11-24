import pygame 
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

  def reset(self):
    self.direction = Direction.RIGHT
    self.head = Point(self.w/2, self.h/2)
    self.snake = [self.head, 
                  Point(self.head.x-BLOCK_SIZE, self.head.y), 
                  Point(self.head.x-2*BLOCK_SIZE, self.head.y)]
    self.score = 0
    self.food = None 
    self._place_food()


  def _place_food(self):
    x_food = random.randint(1, (self.w - BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
    y_food = random.randint(1, (self.h - BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
    self.food = Point(x_food, y_food)
    if self.food in self.snake:
      self._place_food()
  
  def play_step(self):
    # collect user input
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygama.quit()
        quit()
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_a:
          self.direction = Direction.LEFT
        elif event.key == pygame.K_w:
          self.direction = Direction.UP 
        elif event.key == pygame.K_d:
          self.direction = Direction.RIGHT
        elif event.key == pygame.K_s:
          self.direction = Direction.DOWN
    # move
    self._move(self.direction)
    # add a block at the front
    self.snake.insert(0, self.head)
    # check if game over
    game_over = False
    if self._is_collision() == True:
      game_over = True
      return game_over, self.score
    # place new food and/or move
    if self.head == self.food:
      self.score += 1 
      self._place_food()
    else:
      # remove the block we added before at the front
      self.snake.pop()
    # update ui and clock 
    self._update_ui()
    self.clock.tick(SPEED)
    # return game over and score
    return game_over, self.score
    
  def _is_collision(self):
    if self.head.x > self.w - BLOCK_SIZE or self.head.x < 0 or self.head.y < 0 or self.head.y > self.h - BLOCK_SIZE:
      return True
    if self.head in self.snake[3:]:
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

  def _move(self, direction):
    x = self.head.x
    y = self.head.y
    if direction == Direction.RIGHT: 
      x += BLOCK_SIZE
    if direction == Direction.LEFT: 
      x -= BLOCK_SIZE
    if direction == Direction.UP:
      y -= BLOCK_SIZE
    if direction == Direction.DOWN:
      y += BLOCK_SIZE
    self.head = Point(x, y)


if __name__ == "__main__":   
  game = SnakeGame()
  while True:
    game_over, score = game.play_step()
    # break if game over 
    if game_over == True:
      break 
  print("Final score:", score)
  pygame.quit()
