import pygame
from pygame.locals import *
import random

WIDTH = 960
HEIGHT = 240
GROUND = 30
FPS = 30

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# initialize pygame and create window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()


stick_run_img = (pygame.image.load(res("stick_run_1.png")),
                 pygame.image.load(res("stick_run_2.png")))
stick_down_img = (pygame.image.load(res("stick_down_1.png")),
                 pygame.image.load(res("stick_down_2.png")))
stick_jump_img = pygame.image.load(res("stick_jump.png"))


ground = pygame.Surface(0, )


class Player(pygame.sprite.Sprite):
    X_OFFSET = 100

    def __init__(self):
        self.image = stick_run_img[0]
        self.rect = self.image.get_rect()
        self.rect.bottom = GROUND
        self.rect.centerx = Player.X_OFFSET


all_sprites = pygame.sprite.Group()

running = True
while running:

    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update()

    screen.fill(BLACK)
    all_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()
