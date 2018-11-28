import os
import random
import sys

import pygame
from pygame.locals import *

# pygame constants
VER = "0.2"

WIDTH = 960
HEIGHT = 240
FPS = 60
ANIMATE = 5
RES = os.path.join(os.path.dirname(os.path.realpath(__file__)), "res")


def res(file_name):
    return os.path.join(RES, file_name)


# define colors
ALPHA = (255, 255, 255, 255)
WHITE = (255, 255, 255)
GREY = (155, 155, 155)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
TRANSP_YELLOW = (255, 255, 102, 168)
SKY = (153, 221, 255)
DIRT = (153, 102, 51)
DEEP_DIRT = (115, 77, 38)

# game constants
RUN = 0
DOWN = 1
JUMP = 2

DOWN_SPEED = 5
RUN_SPEED = 10

GROUND_H = 30
GRAVITY = 1

BLOCK_GAP_LIMIT = 240

# initialize pygame and create window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen.fill(WHITE)
pygame.display.set_caption("Stick Run" + " V" + VER)

clock = pygame.time.Clock()

# font
SIGN_FONT = pygame.font.Font(None, 20)
TITLE_FONT = pygame.font.Font(None, 65)
NORMAL_FONT = pygame.font.Font(None, 30)

# load images
sign_img = pygame.image.load(res("sign.png"))
stick_img = {RUN: (pygame.image.load(res("stick_run_1.png")),
                   pygame.image.load(res("stick_run_2.png"))),
             DOWN: (pygame.image.load(res("stick_down_1.png")),
                    pygame.image.load(res("stick_down_2.png"))),
             JUMP: pygame.image.load(res("stick_jump.png"))}
cactus_img = pygame.image.load(res("cactus.png"))
timer_img = pygame.image.load(res("timer.png"))


class GameObj(pygame.sprite.Sprite):

    all = pygame.sprite.RenderUpdates()

    def __init__(self):
        super().__init__()
        GameObj.all.add(self)


class Button(GameObj):

    all = pygame.sprite.Group()

    def __init__(self):
        pass

    def update(self, *args):
        pass


class Timer(GameObj):

    end = True

    def __init__(self, limit=3):
        super().__init__()
        self._time = 0
        self.image = timer_img
        self.rect = self.image.get_rect()
        self.rect.top = 0
        self.rect.centerx = WIDTH / 2
        self.limit = limit
        Timer.end = False

    def update(self):
        real_time = self._time / FPS
        time_left = round(self.limit - real_time)
        bit_map = NORMAL_FONT.render(str(time_left), True, WHITE)
        text_rect = bit_map.get_rect()
        text_rect.center = (self.rect.width / 2, self.rect.height / 2)
        self.image = pygame.Surface(timer_img.get_size(), SRCALPHA)
        self.image.blit(timer_img, (0, 0))
        self.image.blit(bit_map, text_rect)
        if time_left <= 0:
            Timer.end = True
            self.kill()
        self._time += 1


class Sign(GameObj):

    all = pygame.sprite.Group()

    def __init__(self, text):
        super().__init__()
        self.image = sign_img
        bit_map = SIGN_FONT.render(text, True, WHITE)
        text_rect = bit_map.get_rect()
        text_rect.center = 25, 12
        self.image.blit(bit_map, text_rect)
        self.rect = self.image.get_rect()
        self.rect.bottom = HEIGHT - GROUND_H
        if text != "START":
            self.rect.left = WIDTH
        else:
            self.rect.left = 10

    def update(self):
        self.rect.move_ip(-Player.SPEED, 0)
        if self.rect.right < 0:
            self.kill()


class Ground(GameObj):

    all = pygame.sprite.Group()

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((WIDTH, GROUND_H))
        self.rect = self.image.get_rect()
        self.rect.bottom = HEIGHT
        x_disp = len(Ground.all.sprites()) * WIDTH
        self.rect.move_ip(x_disp, 0)
        self.gene()
        Ground.all.add(self)

    def gene(self):
        self.image.fill(DIRT)
        for dot_y in range(0, 10):
            gradient = mix_color(DIRT, GREY, dot_y / 10)
            pygame.draw.line(self.image, gradient, (0, dot_y), (WIDTH, dot_y), 1)
        for dot_x in range(0, WIDTH):
            if random.random() < 0.1:
                dot_y = random.randint(10, GROUND_H)
                size = random.randint(1, 5)
                pygame.draw.circle(self.image, DEEP_DIRT, (dot_x, dot_y), size)

    def update(self):
        self.rect.move_ip(-Player.SPEED, 0)
        if self.rect.right <= 0:
            self.rect.left = WIDTH
            self.gene()


class Block(GameObj):
    last = 0

    all = pygame.sprite.Group()

    def __init__(self, img):
        super().__init__()
        pile = choose({1: 0.5, 2: 0.35, 3: 0.15})
        single_width = img.get_width()
        single_height = img.get_height()
        self.image = pygame.Surface((single_width, single_height * pile), SRCALPHA)
        for i in range(0, pile):
            self.image.blit(img, (0, i * single_height))
        self.rect = self.image.get_rect()
        self.rect.left = WIDTH
        self.rect.bottom = HEIGHT - GROUND_H
        Block.last = 0
        Block.all.add(self)

    def update(self):
        self.rect.move_ip(-Player.SPEED, 0)
        if self.rect.right < 0:
            self.kill()

    @classmethod
    def gene(cls):
        if cls.last > BLOCK_GAP_LIMIT:
            if len(cls.all.sprites()) == 0:
                cls(cactus_img)
            elif len(cls.all.sprites()) < 3:
                if random.random() < 0.01:
                    cls(cactus_img)
        cls.last += Player.SPEED


class Player(GameObj):

    SPEED = 0
    X_OFFSET = 100
    JUMP_POWER = 12

    r = None
    pause = False

    def __init__(self):
        super().__init__()
        self._state = RUN
        self._img_index = 0
        self._speed_y = 0
        self.image = stick_img[RUN][0]
        self.rect = self.image.get_rect()
        self.rect.bottom = HEIGHT - GROUND_H
        self.rect.centerx = Player.X_OFFSET
        self.distance = 0
        Player.r = self

    def update(self):

        # control
        if self._state != JUMP:
            if key_state[K_UP] or key_state[K_w]:
                self._state = JUMP
                self._speed_y = Player.JUMP_POWER
            elif key_state[K_DOWN] or key_state[K_s]:
                self._state = DOWN
                Player.SPEED = DOWN_SPEED
            else:
                self._state = RUN
                Player.SPEED = RUN_SPEED

        # update image and rect
        if self._state == RUN or self._state == DOWN:
            self._img_index += 1
            self._img_index %= 2 * ANIMATE
            self.image = stick_img[self._state][self._img_index // ANIMATE]
            self.rect.height = self.image.get_height()
            self.rect.bottom = HEIGHT - GROUND_H
        elif self._state == JUMP:
            self.image = stick_img[self._state]
            self.rect.move_ip(0, -self._speed_y)
            self._speed_y -= GRAVITY
            if pygame.sprite.spritecollide(self, Ground.all, False):
                self._state = RUN
                self._speed_y = 0
                self.rect.bottom = HEIGHT - GROUND_H
        self.distance += Player.SPEED


def mix_color(color_a, color_b, ratio=0.5):
    return [int(a * ratio + b * (1 - ratio)) for a, b in zip(color_a, color_b)]


def choose(dct):
    rand = random.random()
    bar = 0
    for choice, chance in dct.items():
        bar += chance
        if rand <= bar:
            return choice
    raise ValueError('total possibility unreachable')


def dialogue(display,
             title="Dialogue",
             msg="Please select one from the following options",
             key_binding=None):

    if key_binding is None:
        key_binding = {K_y: "Yes", K_n: "No"}
    surf_width = 0
    surf_height = 0

    title_bit_map = TITLE_FONT.render(title, True, BLACK)
    title_rect = title_bit_map.get_rect()
    if title_rect.width > surf_width:
        surf_width = title_rect.width
    surf_height += title_rect.height

    msg_bit_map = NORMAL_FONT.render(msg, True, BLACK)
    msg_rect = msg_bit_map.get_rect()
    if msg_rect.width > surf_width:
        surf_width = msg_rect.width
    surf_height += msg_rect.height

    key_bit_maps = []
    for key, choice in key_binding.items():
        text = choice + " : " + pygame.key.name(key)
        text_bit_map = NORMAL_FONT.render(text, True, BLACK)
        text_rect = text_bit_map.get_rect()
        if text_rect.width > surf_width:
            surf_width = text_rect.width
        surf_height += text_rect.height
        key_bit_maps.append((text_bit_map, text_rect))

    surf = pygame.Surface((surf_width, surf_height), SRCALPHA)
    surf.fill(TRANSP_YELLOW)
    blit_x = 0
    for bit_map, rect in [(title_bit_map, title_rect), (msg_bit_map, msg_rect)] + key_bit_maps:
        rect.top = blit_x
        rect.centerx = surf_width / 2
        surf.blit(bit_map, rect)
        blit_x += rect.height

    surf_rect = surf.get_rect()
    screen_size = display.get_size()
    surf_rect.center = (screen_size[0] / 2, screen_size[1] / 2)

    display.blit(surf, surf_rect)
    pygame.display.flip()

    running = True
    while running:

        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == QUIT:
                quit_all()
            elif event.type == KEYDOWN:
                if event.key == K_q and event.mod & KMOD_META:
                    quit_all()
                if event.key in key_binding.keys():
                    return key_binding.get(event.key)


def main():

    # preparing images
    cactus_loc = []
    for i in range(35):
        x, y = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        cactus_loc.append((x, y))
    bit_map = TITLE_FONT.render("SPACE to START!", True, BLACK)
    text_rect = bit_map.get_rect()
    text_rect.center = (WIDTH / 2, HEIGHT / 2)

    running = True
    while running:

        clock.tick(FPS)

        screen.fill(SKY)
        for loc in cactus_loc:
            screen.blit(cactus_img, loc)
        screen.blit(bit_map, text_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_all()
            if event.type == pygame.KEYDOWN:
                if event.key == K_q and event.mod & KMOD_META:
                    quit_all()
                if event.key == K_SPACE:
                    answer = "Retry"
                    while answer == "Retry":
                        score = start()
                        answer = dialogue(screen,
                                          "Play again?",
                                          "You got " + str(score) + " points in your last run!",
                                          {K_SPACE: "Retry", K_q: "Main Menu"})


def start():

    global key_state, mouse_press, mouse_pos

    Sign("START")
    Ground()
    Ground()
    Player()
    timer = Timer()

    pause_text = NORMAL_FONT.render("PAUSED", True, BLACK)
    pause_rect = pause_text.get_rect()
    pause_rect.topleft = (10, 10)

    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill(SKY)
    screen.blit(background, (0, 0))

    Player.pause = False

    running = True
    while running:

        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_all()
                timer.kill()
                timer = Timer()
            if event.type == pygame.KEYDOWN:
                if event.key == K_q and event.mod & KMOD_META:
                    quit_all()
                    timer.kill()
                    timer = Timer()
                if event.key == K_SPACE:
                    Player.pause = not Player.pause
                    if Player.pause:
                        timer.kill()
                        timer = Timer()

        key_state = pygame.key.get_pressed()
        mouse_press = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        screen.fill(SKY)

        if Player.pause:
            screen.blit(pause_text, pause_rect)
        elif Timer.end:
            Block.gene()
            GameObj.all.update()
        else:
            timer.update()

        if pygame.sprite.spritecollide(Player.r, Block.all, False):
            score = Player.r.distance
            Player.r.kill()
            Player.r = None
            for block in Block.all.sprites():
                block.kill()
            if not Timer.end:
                timer.kill()
            return score

        dirty = GameObj.all.draw(screen)
        pygame.display.update(dirty)


def quit_all():
    answer = dialogue(screen,
                      title="Warning",
                      msg="Do you really want to quit?")
    if answer == "Yes":
        pygame.quit()
        sys.exit()
    else:
        Player.pause = True


main()
