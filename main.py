import pygame
import time
from random import randint
from pathlib import Path
from os import getcwd


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# create pygame
pygame.init()
clock = pygame.time.Clock()
sizes = pygame.display.get_desktop_sizes()
X, Y = sizes[0][0], sizes[0][1]
mw = pygame.display.set_mode((X, Y))
mw.fill(BLACK)

surf = pygame.Surface((X, Y))
hud = pygame.Surface((X * 0.3, Y * 0.5))

running_menu = True
running_game = False
running_inventory = False
running_achievement = False
running_settings = False
FPS = 70

moving_time = 100
moving_timer = 0
moving_interval = 500
moving_obj = 1
moving_X, moving_Y = -X * 0.2, Y // 3

bg = -X
background_speed = 5

MOBS = []
mob_speed = 3

PLAYER_POS = [X * 0.2, Y * 0.5]
PLAYER_SIZE = [X * 0.2, X * 0.2]
PLAYER_SIDE = False
PLAYER_SPEED = 4


class Area(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        pygame.sprite.Sprite.__init__(self)
        self.x, self.y, self.w, self.h = x, y, width, height
        self.rect = pygame.Rect(x, y, width, height)
        self.color, self.surf = color, pygame.Surface((X, Y))

    def draw(self):
        pygame.draw.rect(mw, self.color, self.rect)

    def outline(self, thickness):
        pygame.draw.rect(mw, self.color, self.rect, thickness)

    def collidepoint(self, x, y):
        return self.rect.collidepoint(x, y)

    def set_color(self, new_color):
        self.color = new_color

    def set_size(self, width):
        self.w = width
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)


class Circle(pygame.sprite.Sprite):
    def __init__(self, color, center, radius):
        pygame.sprite.Sprite.__init__(self)
        self.surf, self.center, self.radius, self.color = (500, 500), center, radius, color
        self.circle, self.surf = pygame.draw.circle(mw, color, center, radius), pygame.Surface((X, Y))

    def draw(self):
        pygame.draw.circle(mw, self.color, self.center, self.radius)

    def collidepoint(self, x, y):
        return self.circle.collidepoint(x, y)

    def set_color(self, new_color):
        self.color = new_color


class Label(Area):
    def __init__(self, x, y, width, height, color):
        super().__init__(x, y, width, height, color)
        self.text = None

    def set_text(self, text, font_size=20, text_color=(0, 0, 0)):
        self.text = pygame.font.SysFont('microsoft yahei', font_size).render(text, True, text_color)
        # verdana, tahoma, microsoft yahei, georgia

    def draw(self, shift_x=0, shift_y=0):
        pygame.draw.rect(mw, self.color, self.rect)
        mw.blit(self.text, (self.rect.x + shift_x, self.rect.y + shift_y))


class Mob:
    def __init__(self, name, skin, health, damage, mana, crit, speed, status='walking', do=3):
        self.name, self.skin, self.health, self.damage, self.mana, self.crit, self.speed = name, skin, health, damage, mana, crit, speed
        self.status, self.do = status, do
        self.x, self.y = X * 0.8, Y * (0.6 + randint(-1, 2))
        self.count_angering = 0

        self.anim_attaching = Animation(self.skin[0], 1)
        self.anim_dying = Animation(self.skin[1], 1)
        self.anim_staying = Animation(self.skin[2], 1)
        self.anim_walking = Animation(self.skin[3], 1)
        self.anim_angering = Animation(self.skin[4], 1)
        self.anim_hurting = Animation(self.skin[5], 1)
        self.sp_anim = [self.anim_attaching, self.anim_dying, self.anim_staying,
                        self.anim_walking, self.anim_angering, self.anim_hurting]

    def hit(self, other, damage):
        if self.anim_attaching.index == 0:
            print(f'{self.name} ударил {other.name} и снес {damage} хп! У моба: {other.health} хп!')
            other.health -= damage

    def beat(self, other, damage, ii=0):
        print(f'{self.name} получил удар от {other.name} на {damage} хп!')
        self.health -= damage
        if self.health <= 0:
            self.die(other, ii)

    def kill(self, other):
        print(f'{self.name} убил {other.name}!')

    def die(self, other, ii=0):
        print(f'{self.name} умер от {other.name}!')
        '''for _ in range(len(self.skin[1]) * 20):
            self.anim_dying.update(0.05)
            mw.blit(self.anim_dying.image, (self.x, self.y))
            draw_mob(self.anim_dying, self)'''
        del MOBS[ii]

    def set_status(self, status):
        self.status = status
        match status:
            case 'attaching': self.do = 0
            case 'dying': self.do = 1
            case 'staying': self.do = 2
            case 'walking': self.do = 3
            case 'angering': self.do = 4
            case 'hurting': self.do = 5

    def reverse(self):
        self.speed //= -1


class Animation(pygame.sprite.Sprite):
    def __init__(self, images, time_interval, index=0):
        super(Animation, self).__init__()
        self.images = images
        self.image = self.images[0]
        self.time_interval = time_interval
        self.index = index
        self.timer = 0

    def update(self, seconds, reverse=False):
        self.timer += seconds
        if self.timer >= self.time_interval:
            self.image = self.images[self.index]
            if reverse:
                self.image = pygame.transform.flip(self.image, True, False)
            self.index = (self.index + 1) % len(self.images)
            self.timer = 0


forest = forest2 = pygame.image.load('World\\forest3.png').convert_alpha()
forest = pygame.transform.scale(forest, (X * 3, Y + Y * 0.1))

castle = pygame.image.load('World\\castle.png').convert_alpha()
castle = pygame.transform.scale(castle, (X, Y))

hill = pygame.image.load('World\\hill (3).png').convert_alpha()
hill = pygame.transform.scale(hill, (X * 0.7, Y * 0.6))

preview = pygame.image.load('preview.png').convert_alpha()
preview = pygame.transform.scale(preview, (X, Y))
preview.set_alpha(255)

PLAYER_ATTACHING, PLAYER_DYING, PLAYER_STAYING, PLAYER_WALKING, PLAYER_ANGERING, PLAYER_HURTING = [], [], [], [], [], []

FANGEL_1_ATTACHING, FANGEL_1_DYING, FANGEL_1_STAYING, FANGEL_1_WALKING, FANGEL_1_ANGERING, FANGEL_1_HURTING = [], [], [], [], [], []
FANGEL_2_ATTACHING, FANGEL_2_DYING, FANGEL_2_STAYING, FANGEL_2_WALKING, FANGEL_2_ANGERING, FANGEL_2_HURTING = [], [], [], [], [], []
FANGEL_3_ATTACHING, FANGEL_3_DYING, FANGEL_3_STAYING, FANGEL_3_WALKING, FANGEL_3_ANGERING, FANGEL_3_HURTING = [], [], [], [], [], []

GOLEM_1_ATTACHING, GOLEM_1_DYING, GOLEM_1_STAYING, GOLEM_1_WALKING, GOLEM_1_ANGERING, GOLEM_1_HURTING = [], [], [], [], [], []
GOLEM_2_ATTACHING, GOLEM_2_DYING, GOLEM_2_STAYING, GOLEM_2_WALKING, GOLEM_2_ANGERING, GOLEM_2_HURTING = [], [], [], [], [], []
GOLEM_3_ATTACHING, GOLEM_3_DYING, GOLEM_3_STAYING, GOLEM_3_WALKING, GOLEM_3_ANGERING, GOLEM_3_HURTING = [], [], [], [], [], []

MINOTAUR_1_ATTACHING, MINOTAUR_1_DYING, MINOTAUR_1_STAYING, MINOTAUR_1_WALKING, MINOTAUR_1_ANGERING, MINOTAUR_1_HURTING = [], [], [], [], [], []
MINOTAUR_2_ATTACHING, MINOTAUR_2_DYING, MINOTAUR_2_STAYING, MINOTAUR_2_WALKING, MINOTAUR_2_ANGERING, MINOTAUR_2_HURTING = [], [], [], [], [], []
MINOTAUR_3_ATTACHING, MINOTAUR_3_DYING, MINOTAUR_3_STAYING, MINOTAUR_3_WALKING, MINOTAUR_3_ANGERING, MINOTAUR_3_HURTING = [], [], [], [], [], []

REAPER_1_ATTACHING, REAPER_1_DYING, REAPER_1_STAYING, REAPER_1_WALKING, REAPER_1_ANGERING, REAPER_1_HURTING = [], [], [], [], [], []
REAPER_2_ATTACHING, REAPER_2_DYING, REAPER_2_STAYING, REAPER_2_WALKING, REAPER_2_ANGERING, REAPER_2_HURTING = [], [], [], [], [], []
REAPER_3_ATTACHING, REAPER_3_DYING, REAPER_3_STAYING, REAPER_3_WALKING, REAPER_3_ANGERING, REAPER_3_HURTING = [], [], [], [], [], []

SATYR_1_ATTACHING, SATYR_1_DYING, SATYR_1_STAYING, SATYR_1_WALKING, SATYR_1_ANGERING, SATYR_1_HURTING = [], [], [], [], [], []
SATYR_2_ATTACHING, SATYR_2_DYING, SATYR_2_STAYING, SATYR_2_WALKING, SATYR_2_ANGERING, SATYR_2_HURTING = [], [], [], [], [], []
SATYR_3_ATTACHING, SATYR_3_DYING, SATYR_3_STAYING, SATYR_3_WALKING, SATYR_3_ANGERING, SATYR_3_HURTING = [], [], [], [], [], []

WRAITH_1_ATTACHING, WRAITH_1_DYING, WRAITH_1_STAYING, WRAITH_1_WALKING, WRAITH_1_ANGERING, WRAITH_1_HURTING = [], [], [], [], [], []
WRAITH_2_ATTACHING, WRAITH_2_DYING, WRAITH_2_STAYING, WRAITH_2_WALKING, WRAITH_2_ANGERING, WRAITH_2_HURTING = [], [], [], [], [], []
WRAITH_3_ATTACHING, WRAITH_3_DYING, WRAITH_3_STAYING, WRAITH_3_WALKING, WRAITH_3_ANGERING, WRAITH_3_HURTING = [], [], [], [], [], []

BUTTONS = []

for i in range(1, 8):
    im = pygame.image.load(f'Buttons\\button{i}.png').convert_alpha()
    if 1 <= i <= 5:
        im = pygame.transform.scale(im, (380, 100))
    elif i == 6:
        im = pygame.transform.scale(im, (X * 0.05, X * 0.05))
    elif i == 7:
        im = pygame.transform.scale(im, (X * 0.25, X * 0.06))
    BUTTONS.append(im)

########################################################################################################################

for i in range(1, 11):
    im = pygame.image.load(f'Mobs\\_PLAYER\\Attaching\\player{i}.png').convert_alpha()
    im = pygame.transform.scale(im, PLAYER_SIZE)
    PLAYER_ATTACHING.append(im)
for i in range(1, 14):
    im = pygame.image.load(f'Mobs\\_PLAYER\\Dying\\player{i}.png').convert_alpha()
    im = pygame.transform.scale(im, PLAYER_SIZE)
    PLAYER_DYING.append(im)
for i in range(1, 4):
    im = pygame.image.load(f'Mobs\\_PLAYER\\Staying\\player{i}.png').convert_alpha()
    im = pygame.transform.scale(im, PLAYER_SIZE)
    PLAYER_STAYING.append(im)
for i in range(1, 7):
    im = pygame.image.load(f'Mobs\\_PLAYER\\Walking\\player{i}.png').convert_alpha()
    im = pygame.transform.scale(im, PLAYER_SIZE)
    PLAYER_WALKING.append(im)
for i in range(1, 3):
    im = pygame.image.load(f'Mobs\\_PLAYER\\Angering\\player{i}.png').convert_alpha()
    im = pygame.transform.scale(im, PLAYER_SIZE)
    PLAYER_ANGERING.append(im)
for i in range(1, 3):
    im = pygame.image.load(f'Mobs\\_PLAYER\\Hurting\\player{i}.png').convert_alpha()
    im = pygame.transform.scale(im, PLAYER_SIZE)
    PLAYER_HURTING.append(im)

########################################################################################################################

for num_pers in range(1):
    for i in range(1, 13):
        im = pygame.image.load(f'Mobs\\Satyr1\\Attaching\\satyr{i}.png').convert_alpha()
        im = pygame.transform.scale(im, (X * 0.2, X * 0.2))
        SATYR_1_ATTACHING.append(im)
    for i in range(1, 15):
        im = pygame.image.load(f'Mobs\\Satyr1\\Dying\\satyr{i}.png').convert_alpha()
        im = pygame.transform.scale(im, (X * 0.2, X * 0.2))
        SATYR_1_DYING.append(im)
    for i in range(1, 12):
        im = pygame.image.load(f'Mobs\\Satyr1\\Staying\\satyr{i}.png').convert_alpha()
        im = pygame.transform.scale(im, (X * 0.2, X * 0.2))
        SATYR_1_STAYING.append(im)
    for i in range(1, 17):
        im = pygame.image.load(f'Mobs\\Satyr1\\Walking\\satyr{i}.png').convert_alpha()
        im = pygame.transform.scale(im, (X * 0.2, X * 0.2))
        SATYR_1_WALKING.append(im)
    for i in range(1, 19):
        im = pygame.image.load(f'Mobs\\Satyr1\\Angering\\satyr{i}.png').convert_alpha()
        im = pygame.transform.scale(im, (X * 0.2, X * 0.2))
        SATYR_1_ANGERING.append(im)
    for i in range(1, 13):
        im = pygame.image.load(f'Mobs\\Satyr1\\Hurting\\satyr{i}.png').convert_alpha()
        im = pygame.transform.scale(im, (X * 0.2, X * 0.2))
        SATYR_1_HURTING.append(im)

########################################################################################################################

PLAYER_ATTACHING_ANIM = Animation(PLAYER_ATTACHING, 2)
PLAYER_DYING_ANIM = Animation(PLAYER_DYING, 1)
PLAYER_STAYING_ANIM = Animation(PLAYER_STAYING, 5)
PLAYER_WALKING_ANIM = Animation(PLAYER_WALKING, 2)
PLAYER_ANGERING_ANIM = Animation(PLAYER_ANGERING, 1)
PLAYER_HURTING_ANIM = Animation(PLAYER_HURTING, 1)

MENU_WEATHER = []

weather_folder = Path(f"{getcwd()}/Weather/")
for i in weather_folder.rglob('*'):
    im = pygame.image.load(i).convert_alpha()
    im = pygame.transform.scale(im, (X, Y))
    MENU_WEATHER.append(im)


SUN = pygame.image.load('sun.png').convert_alpha()
SUN = pygame.transform.scale(SUN, (X * 0.2, X * 0.2))
mw.blit(SUN, (moving_X, moving_Y))

MOON = pygame.image.load('moon.png').convert_alpha()
MOON = pygame.transform.scale(MOON, (X * 0.2, X * 0.2))
mw.blit(MOON, (moving_X, moving_Y))

COIN1 = COIN2 = []
for i in range(1, 5):
    coin = pygame.image.load(f'coin{i}.png').convert_alpha()
    coin = pygame.transform.scale(coin, (X * 0.1, X * 0.1))
    COIN1.append(coin), COIN2.append(coin)
COIN2.reverse()

COIN_ANIM1 = Animation(COIN1, 1)
COIN_ANIM2 = Animation(COIN2, 1)

MOB_TYPES = [
    ['player', [PLAYER_ATTACHING, PLAYER_DYING, PLAYER_STAYING, PLAYER_WALKING, PLAYER_ANGERING, PLAYER_HURTING], 100, 20, 50, 3, 4],
    ['fangel1', [FANGEL_1_ATTACHING, FANGEL_1_DYING, FANGEL_1_STAYING, FANGEL_1_WALKING, FANGEL_1_ANGERING, FANGEL_1_HURTING], 70, 3, 0, 0, 3],
    ['fangel2', [FANGEL_2_ATTACHING, FANGEL_2_DYING, FANGEL_2_STAYING, FANGEL_2_WALKING, FANGEL_2_ANGERING, FANGEL_2_HURTING], 70, 3, 0, 0, 3],
    ['fangel3', [FANGEL_3_ATTACHING, FANGEL_3_DYING, FANGEL_3_STAYING, FANGEL_3_WALKING, FANGEL_3_ANGERING, FANGEL_3_HURTING], 70, 3, 0, 0, 3],

    ['golem1', [GOLEM_1_ATTACHING, GOLEM_1_DYING, GOLEM_1_STAYING, GOLEM_1_WALKING, GOLEM_1_ANGERING, GOLEM_1_HURTING], 70, 3, 0, 0, 1],
    ['golem2', [GOLEM_2_ATTACHING, GOLEM_2_DYING, GOLEM_2_STAYING, GOLEM_2_WALKING, GOLEM_2_ANGERING, GOLEM_2_HURTING], 70, 3, 0, 0, 1],
    ['golem3', [GOLEM_3_ATTACHING, GOLEM_3_DYING, GOLEM_3_STAYING, GOLEM_3_WALKING, GOLEM_3_ANGERING, GOLEM_3_HURTING], 70, 3, 0, 0, 1],

    ['minotaur1', [MINOTAUR_1_ATTACHING, MINOTAUR_1_DYING, MINOTAUR_1_STAYING, MINOTAUR_1_WALKING, MINOTAUR_1_ANGERING, MINOTAUR_1_HURTING], 70, 3, 0, 0, 3],
    ['minotaur2', [MINOTAUR_2_ATTACHING, MINOTAUR_2_DYING, MINOTAUR_2_STAYING, MINOTAUR_2_WALKING, MINOTAUR_2_ANGERING, MINOTAUR_2_HURTING], 70, 3, 0, 0, 3],
    ['minotaur3', [MINOTAUR_3_ATTACHING, MINOTAUR_3_DYING, MINOTAUR_3_STAYING, MINOTAUR_3_WALKING, MINOTAUR_3_ANGERING, MINOTAUR_3_HURTING], 70, 3, 0, 0, 3],

    ['reaper1', [REAPER_1_ATTACHING, REAPER_1_DYING, REAPER_1_STAYING, REAPER_1_WALKING, REAPER_1_ANGERING, REAPER_1_HURTING], 70, 3, 0, 0, 4],
    ['reaper2', [REAPER_2_ATTACHING, REAPER_2_DYING, REAPER_2_STAYING, REAPER_2_WALKING, REAPER_2_ANGERING, REAPER_2_HURTING], 70, 3, 0, 0, 4],
    ['reaper3', [REAPER_3_ATTACHING, REAPER_3_DYING, REAPER_3_STAYING, REAPER_3_WALKING, REAPER_3_ANGERING, REAPER_3_HURTING], 70, 3, 0, 0, 4],

    ['satyr1', [SATYR_1_ATTACHING, SATYR_1_DYING, SATYR_1_STAYING, SATYR_1_WALKING, SATYR_1_ANGERING, SATYR_1_HURTING], 70, 3, 0, 0, 3],
    ['satyr2', [SATYR_2_ATTACHING, SATYR_2_DYING, SATYR_2_STAYING, SATYR_2_WALKING, SATYR_2_ANGERING, SATYR_2_HURTING], 70, 3, 0, 0, 3],
    ['satyr3', [SATYR_3_ATTACHING, SATYR_3_DYING, SATYR_3_STAYING, SATYR_3_WALKING, SATYR_3_ANGERING, SATYR_3_HURTING], 70, 3, 0, 0, 3],

    ['wraith1', [WRAITH_1_ATTACHING, WRAITH_1_DYING, WRAITH_1_STAYING, WRAITH_1_WALKING, WRAITH_1_ANGERING, WRAITH_1_HURTING], 70, 3, 0, 0, 5],
    ['wraith2', [WRAITH_2_ATTACHING, WRAITH_2_DYING, WRAITH_2_STAYING, WRAITH_2_WALKING, WRAITH_2_ANGERING, WRAITH_2_HURTING], 70, 3, 0, 0, 5],
    ['wraith3', [WRAITH_3_ATTACHING, WRAITH_3_DYING, WRAITH_3_STAYING, WRAITH_3_WALKING, WRAITH_3_ANGERING, WRAITH_3_HURTING], 70, 3, 0, 0, 5],
]


def create_mob(what):
    if what == 1:
        r = MOB_TYPES[13]#randint(1, 2)]
        new_mob = Mob(r[0], r[1], r[2], r[3], r[4], r[5], r[6])
        MOBS.append(new_mob)
    else:
        r = MOB_TYPES[0]
        new_mob = Mob(r[0], r[1], r[2], r[3], r[4], r[5], r[6])
    return new_mob


player = create_mob(2)
hud_heal = Area(X * 0.025, X * 0.021, X * 0.24, X * 0.028, RED)
hud_armour = Area(X * 0.025, X * 0.061, X * 0.24, X * 0.028, WHITE)
hud_mana = Area(X * 0.025, X * 0.1, X * 0.24, X * 0.028, BLUE)
hud_exp = Area(X * 0.2, Y * 0.92, X * 0.6, Y * 0.04, GREEN)
stop_game = Area(X * 0.94, X * 0.01, X * 0.05, X * 0.05, BLACK)


def loading():
    global running_game, running_inventory, running_achievement, running_settings, running_menu, bg

    running = True
    count, bright, long = 100, 500, 0
    mw.fill((255, 255, 255))
    bar = Area(X * 0.3, Y * 0.7, long, Y * 0.05, RED)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        count -= 0.5
        if count < 0:
            running = False

        mw.fill((255, 255, 255)), mw.blit(preview, (0, 0))
        preview.set_alpha(bright), bar.draw()
        long += 2.5
        bar.set_size(long)

        bright -= 2
        if bright == 0:
            bright = 255

        pygame.display.update()
        clock.tick(FPS)

    mw.fill((0, 0, 0))
    menu()


def game():
    global running_game, running_inventory, running_achievement, running_settings, running_menu, bg, PLAYER_SIDE

    is_fighting = False

    bg = -X

    mw.fill((0, 0, 0))
    mw.blit(forest, (bg, 0))

    hud_heal.draw(), hud_armour.draw(), hud_mana.draw(), hud_exp.draw()
    mw.blit(BUTTONS[6], (X * 0.02, X * 0.02)), mw.blit(BUTTONS[6], (X * 0.02, X * 0.06))
    mw.blit(BUTTONS[6], (X * 0.02, X * 0.10)), mw.blit(BUTTONS[5], (X * 0.94, X * 0.01))
    mw.blit(BUTTONS[6], (X * 0.2, Y * 0.91))

    while running_game is True:

        PLAYER_STAYING_ANIM.update(0.3, PLAYER_SIDE)
        mw.blit(forest, (bg, 0))
        mw.blit(PLAYER_STAYING_ANIM.image, PLAYER_POS)
        draw_hud(False)

        if randint(0, 100) == 1:
            create_mob(1)

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                xx, yy = pygame.mouse.get_pos()
                # satyr_fighting.update(0.5)
                # mw.blit(satyr_fighting.image, (x, y))
                is_fighting = True

                if stop_game.collidepoint(xx, yy):
                    running_game = False
                    running_menu = True
                    menu()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                pass

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    pass

                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    pass

                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    PLAYER_SIDE = True

                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    PLAYER_SIDE = False

                if event.key == pygame.K_f or event.key == pygame.K_SPACE:
                    is_fighting = True
                    attaching()

            # quite
            if event.type == pygame.QUIT:
                running_game = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            if PLAYER_POS[1] >= Y * 0.45:
                PLAYER_POS[1] -= 1
                game_moving()

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            if PLAYER_POS[1] <= Y * 0.55:
                PLAYER_POS[1] += 1
                game_moving()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            game_moving(False)
            for mob in MOBS:
                mob.x += PLAYER_SPEED

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            game_moving(True)
            for mob in MOBS:
                mob.x -= PLAYER_SPEED

        if is_fighting:
            PLAYER_ATTACHING_ANIM.update(2, PLAYER_SIDE)
            mw.blit(PLAYER_ATTACHING_ANIM.image, PLAYER_POS)
            attaching()
            if PLAYER_ATTACHING_ANIM.index == 0:
                is_fighting = False

        draw_mobs()

        pygame.display.update()
        clock.tick(FPS)


def inventory():
    global running_game, running_inventory, running_achievement, running_settings, running_menu

    while running_inventory is True:
        pass


def achievement():
    global running_game, running_inventory, running_achievement, running_settings, running_menu


def settings():
    global running_game, running_inventory, running_achievement, running_settings, running_menu
    print('settings')

    while running_settings is True:

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                xx, yy = pygame.mouse.get_pos()

                if stop_game.collidepoint(xx, yy):
                    running_menu = True
                    running_settings = False
                    menu()


def menu():
    global running_game, running_inventory, running_achievement, running_settings, running_menu

    button_start = Area(150, 100, 380, 100, BLACK)
    button_inventory = Area(150, 250, 380, 100, BLACK)
    button_achievement = Area(150, 400, 380, 100, BLACK)
    button_settings = Area(150, 550, 380, 100, BLACK)
    button_exit = Area(150, 700, 380, 100, BLACK)

    menu_weather = Animation(MENU_WEATHER, 10, 2)

    while running_menu is True:

        menu_weather.update(0.1)
        mw.blit(menu_weather.image, (0, 0))

        mw.blit(castle, (0, 0))
        mw.blit(hill, (0, Y * 0.45))
        # mw.blit(title, (200, 100))
        menu_moving(200)

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                xx, yy = pygame.mouse.get_pos()

                if button_start.collidepoint(xx, yy):
                    running_menu = False
                    running_game = True
                    time.sleep(0.1)
                    game()

                if button_inventory.collidepoint(xx, yy):
                    running_menu = False
                    running_inventory = True
                    time.sleep(0.1)
                    inventory()

                if button_achievement.collidepoint(xx, yy):
                    running_menu = False
                    running_achievement = True
                    time.sleep(0.1)
                    achievement()

                if button_settings.collidepoint(xx, yy):
                    running_menu = False
                    running_settings = True
                    time.sleep(0.1)
                    settings()

                if button_exit.collidepoint(xx, yy):
                    running_menu = False
                    time.sleep(0.1)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                pass

            # quite
            if event.type == pygame.QUIT:
                # save_variables()
                running_menu = False

        mw.blit(BUTTONS[0], (150, 100)), mw.blit(BUTTONS[1], (150, 250)), mw.blit(BUTTONS[2], (150, 400))
        mw.blit(BUTTONS[3], (150, 550)), mw.blit(BUTTONS[4], (150, 700))

        pygame.display.update()
        clock.tick(FPS)


def menu_moving(seconds):
    global moving_timer, moving_interval, moving_X, moving_Y, moving_obj
    moving_timer += seconds

    if moving_timer >= moving_interval:
        moving_timer = 0
        if moving_X >= (X // 2) - (X * 0.1):
            moving_X += X // 200
            moving_Y += Y // 400
            if moving_X >= X:
                if moving_obj == 1:
                    moving_obj = 2
                else:
                    moving_obj = 1
                moving_X, moving_Y = -X * 0.2, Y // 3
        else:
            moving_X += X // 200
            moving_Y -= Y // 400

    if moving_obj == 1:
        mw.blit(SUN, (moving_X, moving_Y))
    elif moving_obj == 2:
        mw.blit(MOON, (moving_X, moving_Y))
    mw.blit(castle, (0, 0))


def game_moving(direction=None):
    global bg, background_speed

    if direction is True:
        bg -= background_speed

    if direction is False:
        bg += background_speed

    if bg >= 0:
        bg = -X * 2
    if bg <= -X * 2:
        bg = -X

    draw_hud(True)

    if direction is None:
        PLAYER_WALKING_ANIM.update(0.5)
    else:
        PLAYER_WALKING_ANIM.update(0.5, not direction)
    mw.blit(PLAYER_WALKING_ANIM.image, PLAYER_POS)


def draw_hud(what):
    global bg

    if what:
        mw.fill((0, 0, 0))
        mw.blit(forest, (bg, 0))

    hud_heal.draw(), hud_armour.draw(), hud_mana.draw(), hud_exp.draw()
    mw.blit(BUTTONS[6], (X * 0.02, X * 0.02)), mw.blit(BUTTONS[6], (X * 0.02, X * 0.06))
    mw.blit(BUTTONS[6], (X * 0.02, X * 0.10)), mw.blit(BUTTONS[5], (X * 0.94, X * 0.01))
    mw.blit(BUTTONS[6], (X * 0.2, Y * 0.91))


def draw_mob(who, what):
    global MOBS
    for mob in MOBS:
        mob.sp_anim[mob.do].update(0.3)
        mw.blit(mob.sp_anim[mob.do].image, (mob.x, mob.y))
    who.update(0.5)
    mw.blit(who.image, (what.x, what.y))


def draw_mobs():
    global MOBS
    for mob in MOBS:
        if PLAYER_POS[0] - mob.x <= 0:
            if abs(PLAYER_POS[0] - mob.x) > X * 0.7:
                mob.do = 2
            elif abs(PLAYER_POS[0] - mob.x) > X * 0.6:
                mob.count_angering += 1
                if mob.count_angering > 3:
                    mob.do = 3
                    mob.x -= mob.speed
                else:
                    mob.do = 4
            elif abs(PLAYER_POS[0] - mob.x) > X * 0.1:
                mob.do = 3
                mob.x -= mob.speed
            elif 0 <= abs(PLAYER_POS[0] - mob.x) <= X * 0.1:
                mob.do = 0
                mob.hit(player, mob.damage)
        else:
            mob.reverse()
        mob.sp_anim[mob.do].update(0.3)
        mw.blit(mob.sp_anim[mob.do].image, (mob.x, mob.y))


def attaching():
    global MOBS, PLAYER_POS
    for ii in range(len(MOBS)):
        if abs(PLAYER_POS[0] - MOBS[ii].x) <= X * 0.1:
            MOBS[ii].beat(player, player.damage)
            break


def lose():
    pass


def save_variables(table, column, var):
    pass


loading()
