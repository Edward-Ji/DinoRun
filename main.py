#!/usr/bin/env python3
import pygame
from pygame.locals import *
import os
import random
import time
import pickle

try:
    from pyautogui import size
    display_w = size()[0]
except ModuleNotFoundError:
    display_w = 1440

GAME_NAME = "StickRun"
GAME_VER = "0.1"
RES = os.path.join(os.path.dirname(os.path.realpath(__file__)), "res")


pygame.init()


display_h = 205

display = pygame.display.set_mode((display_w, display_h))
pygame.display.set_caption(GAME_NAME + GAME_VER)

icon_img = pygame.image.load(os.path.join(RES, "icon.png"))
pygame.display.set_icon(icon_img)

# obstacle images
cactus_img = pygame.image.load(os.path.join(RES, "cactus.png"))
stabs_img = pygame.image.load(os.path.join(RES, "stabs.png"))
zombie_img = pygame.image.load(os.path.join(RES, "zombie_hole.png"))
zombie_pop_up = pygame.image.load(os.path.join(RES, "zombie.png"))
obstacle_img = [cactus_img, stabs_img, zombie_img]

# stick images
stick_run_1_img = pygame.image.load(os.path.join(RES, "stick_run_1.png"))
stick_run_2_img = pygame.image.load(os.path.join(RES, "stick_run_2.png"))
stick_jump_img = pygame.image.load(os.path.join(RES, "stick_jump.png"))
stick_down_1_img = pygame.image.load(os.path.join(RES, "stick_down_1.png"))
stick_down_2_img = pygame.image.load(os.path.join(RES, "stick_down_2.png"))
stick_img = {"run1": stick_run_1_img,
             "run2": stick_run_2_img,
             "jump": stick_jump_img,
             "down1": stick_down_1_img,
             "down2": stick_down_2_img}

clock = pygame.time.Clock()
FPS = 40

FONT = pygame.font.Font(None, 24)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class Slider:
    HEIGHT = 14
    GAP = 20
    WIDTH = display_w - 2 * GAP

    active = None
    family = []

    def __init__(self, text, min_val, max_val, def_val):
        self.text = text
        self.min_val = min_val
        self.max_val = max_val
        self.def_val = def_val
        self.pos_val = def_val
        Slider.family.append(self)
        if Slider.active is None:
            Slider.active = self

    def _show(self, display, y):
        fraction = (self.pos_val - self.min_val) / (self.max_val - self.min_val)
        x = Slider.GAP
        frame = pygame.Rect(x, y, Slider.WIDTH, Slider.HEIGHT)
        fill = pygame.Rect(x, y, fraction * Slider.WIDTH, Slider.HEIGHT)
        pygame.draw.rect(display, BLACK, frame, 2)
        pygame.draw.rect(display, BLACK, fill)
        if Slider.active is self:
            msg = "changing " + self.text + " - " + str(self.pos_val)
            message(display, msg, -2, y + Slider.HEIGHT)
        message(display, str(self.min_val), 0, y)
        message(display, str(self.max_val), -1, y)

    def change(self, dir):
        if dir == K_LEFT:
            if self.pos_val > self.min_val:
                self.pos_val -= 1
        elif dir == K_RIGHT:
            if self.pos_val < self.max_val:
                self.pos_val += 1

    @classmethod
    def focus(cls, move):
        if move == K_DOWN:
            index = cls.family.index(cls.active)
            if index < len(cls.family) - 1:
                index += 1
            else:
                index = 0
        elif move == K_UP:
            index = cls.family.index(cls.active)
            if index > 0:
                index -= 1
            else:
                index = len(cls.family) - 1
        cls.active = cls.family[index]

    @classmethod
    def reset(cls):
        for obj in cls.family:
            obj.pos_val = obj.def_val

    @classmethod
    def show(cls, display, top):
        y = top
        for obj in cls.family:
            obj._show(display, y)
            y += Slider.HEIGHT + Slider.GAP


class File:
    CHARACTER = os.path.join(RES, "character.p")

    @classmethod
    def load(cls):
        dic = {}
        for obj in Slider.family:
            dic[obj.text] = obj.pos_val
        Stick.INIT_SPEED_X = dic["run speed"]
        Stick.JUMP_SPEED = dic["jump power"]
        Stick.DOWN_SPEED_X = dic["crouch speed"]

    @classmethod
    def read(cls):
        try:
            with open(cls.CHARACTER, "rb") as f:
                Slider.family = pickle.load(f)
                Slider.active = Slider.family[0]
        except Exception as e:
            # create sliders for character modification
            Slider("run speed", 8, 20, 10)
            Slider("jump power", 8, 15, 10)
            Slider("crouch speed", 2, 8, 5)
            message(display, "Error loading game data", -1, 0)

    @classmethod
    def write(cls):
        with open(cls.CHARACTER, "wb") as f:
            pickle.dump(Slider.family, f)


class Obstacle:
    ground_h = 20
    ground_scroll = 0

    spawn_time = time.time()
    family = []

    def __init__(self, img):
        self.image = img
        rect = img.get_rect()
        rect.left, rect.bottom = display_w, display_h - Obstacle.ground_h
        self.rect = rect
        Obstacle.family.append(self)
        Obstacle.spawn_time = time.time()

    def _move(self):
        # move
        if hasattr(self, "speed"):
            self.rect.left -= Stick.active.speed_x + obj.speed
        else:
            self.rect.left -= Stick.active.speed_x
        # eliminate
        if self.rect.right <= 0:
            Obstacle.family.remove(self)
            del self

    def _show(self, display):
        if self.image == zombie_img:
            if self.rect.left - Stick.active.rect.right <= 150:
                self.image = zombie_pop_up
        display.blit(self.image, self.rect)

    @classmethod
    def renew(cls):
        # spawn
        spawn_limit = Stick.JUMP_SPEED / Stick.GRAVITY * 2 / FPS + 0.1
        gap_time = time.time() - cls.spawn_time
        if gap_time >= spawn_limit:
            if random.random() <= 0.05:
                cls(random.choice(obstacle_img))
        # move all
        for obj in cls.family:
            obj._move()

    @classmethod
    def show(cls, display):
        pygame.draw.line(display,
                         BLACK,
                         (0, display_h - Obstacle.ground_h),
                         (display_w, display_h - Obstacle.ground_h))
        for obj in cls.family:
            obj._show(display)


class Stick:
    FIXED_X = 100
    INIT_SPEED_X = 10
    DOWN_SPEED_X = 5
    JUMP_SPEED = 10
    GRAVITY = 1

    active = None

    def __init__(self, img):
        self._pose = 0
        self._score = 0
        self.speed_x = Stick.INIT_SPEED_X
        self.speed_y = None
        self.img = img
        self.act = "run1"
        rect = img[self.act].get_rect()
        rect.left, rect.bottom = Stick.FIXED_X, display_h - Obstacle.ground_h
        self.rect = rect
        Stick.active = self

    def score():
        doc = "The score property."

        def fget(self):
            return round(self._score, 2)

        def fset(self, value):
            self._score = value

        def fdel(self):
            del self._score
        return locals()
    score = property(**score())

    def run(self):
        self.speed_x = Stick.INIT_SPEED_X
        if self.act == "run1" and self._pose >= 3:
            self.act = "run2"
            self._pose = 0
        elif self.act == "run2" and self._pose >= 3:
            self.act = "run1"
            self._pose = 0
        self._pose += 1

    def jump(self):
        if self.speed_y is None:
            self.speed_y = Stick.JUMP_SPEED
        self.rect.top -= self.speed_y
        self.speed_y -= Stick.GRAVITY
        if self.rect.bottom >= display_h - Obstacle.ground_h:
            self.speed_y = None
            self.act = "run1"

    def down(self):
        if self.speed_x == Stick.INIT_SPEED_X:
            self.speed_x = Stick.DOWN_SPEED_X
        if self.act == "down1" and self._pose >= 4:
            self.act = "down2"
            self._pose = 0
        elif self.act == "down2" and self._pose >= 4:
            self.act = "down1"
            self._pose = 0
        self._pose += 1

    def renew(self):
        if "run" in self.act:
            self.run()
        elif self.act == "jump":
            self.jump()
        elif "down" in self.act:
            self.down()
        img_wh = self.img[self.act].get_rect()
        self.rect.width, self.rect.height = img_wh.width, img_wh.height
        if self.act != "jump":
            self.rect.bottom = display_h - Obstacle.ground_h
        self.score += self.speed_x / display_w

    def show(self, display):
        display.blit(self.img[self.act], self.rect)

    @classmethod
    def crashed(cls):
        rect = cls.active.rect
        for obj in Obstacle.family:
            if rect.colliderect(obj.rect):
                return True
        else:
            return False

    @classmethod
    def ai(cls):
        stick = cls.active
        for obj in Obstacle.family:
            if 0 < obj.rect.left - stick.rect.left <= 100:
                stick.act = "jump"


def message(display, text, x, y, fill=False):
    bit_map = FONT.render(text, True, BLACK)
    rect = bit_map.get_rect()
    if x >= 0:
        rect.left, rect.top = x, y
    else:
            if x == -1:
                rect.right = display_w
                rect.top = y
            elif x == -2:
                rect.center = (display_w / 2, 0)
                rect.top = y
    if fill:
        pygame.draw.rect(display, WHITE, rect)
    display.blit(bit_map, rect)


def start():
    File.read()

    display.fill(WHITE)

    while True:
        message(display, "Jump - UP or SPACE", -2, 0, True)
        message(display, "Crouch - DOWN", -2, 20, True)
        message(display, "Press SPACE to start!", -2, 40, True)
        message(display, "Press C to modify character!", -2, 60, True)
        message(display, "Press Q to quit!", -2, 80, True)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                quit_all()
            elif event.type == KEYDOWN:
                if event.key == K_q:
                    quit_all()
                elif event.key == K_SPACE:
                    main()
                elif event.key == K_c:
                    character()

        clock.tick(FPS)


def character():
    # loop
    while True:
        display.fill(WHITE)
        message(display, "Arrow keys - adjust values; D - reset default", 0, 0)
        message(display, "Any other key to save and return!", 0, 20)
        Slider.show(display, 40)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                quit_all()
            elif event.type == KEYDOWN:
                if event.key == K_UP or event.key == K_DOWN:
                    Slider.focus(event.key)
                elif event.key == K_LEFT or event.key == K_RIGHT:
                    Slider.active.change(event.key)
                elif event.key == K_d:
                    Slider.reset()
                else:
                    File.load()
                    display.fill(WHITE)
                    return

        clock.tick(FPS)


def pause():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                quit_all()
            elif event.type == KEYDOWN:
                if event.key == K_q:
                    quit_all()
                if event.key == K_p:
                    return


def main():
    random.seed(time.time())
    stick = Stick(stick_img)
    Obstacle.family.clear()

    while True:
        if Stick.crashed():
            message(display, "Press SPACE to retry!", 0, 20, True)
            pygame.display.flip()
            return

        for event in pygame.event.get():
            if event.type == QUIT:
                quit_all()
            elif event.type == KEYDOWN:
                if event.key == K_q:
                    quit_all()
                if event.key == K_p:
                    pause()

        key_press = pygame.key.get_pressed()
        if key_press[K_DOWN]:
            if "run" in stick.act:
                stick.act = "down1"
        else:
            if "down" in stick.act:
                stick.act = "run1"
        if key_press[K_SPACE] or key_press[K_UP]:
            if "run" in stick.act:
                stick.act = "jump"

        if key_press[K_CAPSLOCK]:
            Stick.ai()

        Obstacle.renew()
        stick.renew()

        display.fill(WHITE)
        Obstacle.show(display)
        stick.show(display)
        score = "You've traveled {} screen width!".format(Stick.active.score)
        message(display, score, 0, 0, True)

        pygame.display.flip()
        clock.tick(FPS)


def quit_all():
    File.write()
    pygame.quit()
    quit()


start()
