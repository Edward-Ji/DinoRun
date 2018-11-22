import pygame
from pygame.locals import *
import os
import sys


# global constants
WIDTH = 960
HEIGHT = 240
FPS = 30
RES = os.path.join(os.path.dirname(os.path.realpath(__file__)), "res")

def res(fname):
    return os.path.join(RES, fname)


# define colors
ALPHA = (255, 255, 255, 255)
WHITE = (255, 255, 255)
GREY = (155, 155, 155)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DIRT = (153, 102, 51)

# game constants
RUN = 0
DOWN = 1
JUMP = 2

GROUNDH = 30

# initialize pygame and create window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen.fill(WHITE)
pygame.display.set_caption("My Game")

clock = pygame.time.Clock()

stick_img = {RUN: (pygame.image.load(res("stick_run_1.png")),
                   pygame.image.load(res("stick_run_2.png"))),
             DOWN: (pygame.image.load(res("stick_down_1.png")),
                    pygame.image.load(res("stick_down_2.png"))),
             JUMP: pygame.image.load(res("stick_jump.png"))}

cactus_img = pygame.image.load(res("cactus.png"))


class GameObj(pygame.sprite.Sprite):

    all = pygame.sprite.RenderUpdate()

    def __init__(self):
        super().__init__()
        GameObj.all.add(self)


class Ground(GameObj):

    all = pygame.sprite.Group()

    def __init__(self, x_disp=0):
        super().__init__()
        self.image = pygame.Surface((WIDTH, GROUNDH))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.bottom = HEIGHT
        self.rect.move_ip(x_disp, 0)
        self.rand()

    def rand(self):
        self.image.fill(DIRT)
        for dot_y in range(0, 10):
            color = mix_color(DIRT, GREY, dot_y / 10)
            pygame.draw.line(self.image, color, (0, dot_y), (WIDTH, dot_y), 1)

    def update(self):
        self.rect.move_ip(-Player.SPEED, 0)
        if self.rect.right == 0:
            self.rect.left = WIDTH
            self.rand()


class Block:

    all = pygame.sprite.Group()

    def __init__(self):
        super().__init__()
        self.image = cactus_img
        self.rect = self.image.get_rect()
        self.rect.bottom = GROUNDH
        Block.all.add(self)


class Player(pygame.sprite.Sprite):
    SPEED = 10
    X_OFFSET = 100

    r = None

    def __init__(self):
        super().__init__()
        self.image = stick_img[RUN][0]
        self.rect = self.image.get_rect()
        self.rect.bottom = GROUNDH
        self.rect.centerx = Player.X_OFFSET
        Player.r = self

    def update(self):
        pass


def mix_color(color_a, color_b, ratio=0.5):
    return [int(a * ratio + b * (1 - ratio)) for a, b in zip(color_a, color_b)]


def main():

    Ground()
    Ground(WIDTH)

    running = True
    while running:

        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_all()
            if event.type == pygame.KEYDOWN:
                if event.key == K_q and event.mod & KMOD_META:
                    quit_all()
                if event.key == K_SPACE:
                    input()

        GameObj.all.update()

        screen.fill(WHITE)
        GameObj.all.draw(screen)
        pygame.display.flip()


def quit_all():
    pygame.quit()
    sys.exit()


main()
