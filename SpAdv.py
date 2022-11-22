import pygame
import random
import os
from sys import exit
# from player import Player
from bullet import Bullet, EnemyBullet

W = 480
H = 600
FPS = 60

GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

pygame.init()
pygame.mixer.init()  # это для звука (на будущее)
screen = pygame.display.set_mode((W, H))  # почему некоторые пишут screen, а некоторые surface?
pygame.display.set_caption("Space Adventure")  # лень придумывать название
clock = pygame.time.Clock()

import sys

config_name = 'myapp.cfg'

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

config_path = os.path.join(application_path, config_name)

# Загрузка изображений
img_dir = os.path.join(application_path, 'img')
background = pygame.image.load(os.path.join(img_dir, 'starfield.png'))
background_rect = background.get_rect()
player_img = pygame.image.load(os.path.join(img_dir, "playerShip2_green.png"))
pygame.display.set_icon(player_img)

meteor_images = []
meteor_list = ['meteorBrown_big1.png', 'meteorBrown_med1.png',
               'meteorBrown_med1.png', 'meteorBrown_med3.png',
               'meteorBrown_small1.png', 'meteorBrown_small2.png',
               'meteorBrown_tiny1.png']
for img in meteor_list:
    meteor_images.append(pygame.image.load(os.path.join(img_dir, img)).convert())

enemy_img = pygame.image.load(os.path.join(img_dir, "playerShip1_red.png"))

explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(os.path.join(img_dir, filename))
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(os.path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)

heart_img = pygame.image.load(os.path.join(img_dir, 'heart.png')).convert()
heart_mini_img = pygame.transform.scale(heart_img, (25, 25))
heart_mini_img.set_colorkey(BLACK)

powerup_images = {
    'shield': pygame.image.load(os.path.join(img_dir, 'shield_gold.png')),
    'gun': pygame.image.load(os.path.join(img_dir, 'bolt_gold.png'))

}

volume_mixer = []
for i in range(4):
    filename = 'volume{}.png'.format(i)
    img = pygame.image.load(os.path.join(img_dir, filename))
    img = pygame.transform.scale(img, (50, 30))

    volume_mixer.append(img)

# Загрузка звука
all_sounds = set()
snd_dir = os.path.join(application_path, 'snd')
shoot_sound = pygame.mixer.Sound(os.path.join(snd_dir, 'pew.wav'))
expl_sounds = []
for snd in ['expl3.wav', 'expl6.wav']:
    sound = pygame.mixer.Sound(os.path.join(snd_dir, snd))
    expl_sounds.append(sound)
    all_sounds.add(sound)
pygame.mixer.music.load(os.path.join(snd_dir, 'Wonderful.mp3'))
pygame.mixer.music.set_volume(1)
shield_sound = pygame.mixer.Sound(os.path.join(snd_dir, 'pow4.wav'))
power_sound = pygame.mixer.Sound(os.path.join(snd_dir, 'pow5.wav'))
fart_sound = pygame.mixer.Sound(os.path.join(snd_dir, 'fart.wav'))

all_sounds.add(shoot_sound)
all_sounds.add(shield_sound)
all_sounds.add(power_sound)
all_sounds.add(fart_sound)

# Загрузка данных
data_dir = os.path.join(application_path, 'data')

sound_file = open(os.path.join(data_dir, 'sound.txt'))
All_sound_state = sound_file.readlines()
Sound_state = int(All_sound_state[0].split()[1])
Music_state = int(All_sound_state[1].split()[1])
sound_file.close()

highscore_file = open(os.path.join(data_dir, 'highscore.txt'))
Highscore = int(highscore_file.read())
highscore_file.close()

# Пара игровых глобальных параметров
score = 0


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.rect = self.image.get_rect()
        self.radius = 20
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = W / 2  # заводим центральное положение
        self.rect.bottom = H - 10
        self.speedx = 0  # это типа скорость, будем её к координате прибавлять
        self.shield = 100

        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()
        self.relax = 0
        self.alive = True

        money_file = open(os.path.join(data_dir, 'money.txt'))
        self.money = int(money_file.read())
        money_file.close()

        stats_file = open(os.path.join(data_dir, 'stats.txt'))
        stats = stats_file.readlines()
        self.Power_lvl = int(stats[0].split()[1])
        self.Shield_lvl = int(stats[1].split()[1])
        self.Atkspeed_lvl = int(stats[2].split()[1])
        stats_file.close()

        self.maxshield = 100 * (1 + self.Shield_lvl / 3)
        self.shield = 100 * (1 + self.Shield_lvl / 3)
        self.power = self.Power_lvl
        self.shoot_delay = 250 * (1 - (self.Atkspeed_lvl - 1) / 5)

    def update(self):
        self.speedx = 0
        keystate = pygame.key.get_pressed()  # Штука несёт зажатие каждой из клавиш
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx
        # Спросишь, нахрен так, можно же прост координаты менять,
        # но тут самом деле высокий замысел: при нажатии скорость изменится
        # и станет 0 только при отпускании клавиши, чтобы можно было перемещать
        # игрока, удерживая клавишу, уже кучу раз этот факт применяли, но я
        # ток сейчас понял. Хотя это если без get_pressed() делать. С ним можно и так.

        if self.rect.right > W:
            self.rect.right = W  # Забавно, меняем только координату
            # одной точки, но положение меняет вся фигура
        if self.rect.left < 0:
            self.rect.left = 0

        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = W / 2
            self.rect.bottom = H - 10

        POWERUP_TIME = 10000
        if self.power == 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()
        if self.power >= 3 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()
        if self.power > 4:
            self.power = 4

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top, 'lg')
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            if self.power == 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery, 'lg')
                bullet2 = Bullet(self.rect.right, self.rect.centery, 'lg')
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()
            if self.power == 3:
                bullet1 = Bullet(self.rect.centerx, self.rect.top, 'lg')
                bullet2 = Bullet(self.rect.right, self.rect.centery, 'sm')
                bullet3 = Bullet(self.rect.left, self.rect.centery, 'sm')
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                all_sprites.add(bullet3)
                bullets.add(bullet1)
                bullets.add(bullet2)
                bullets.add(bullet3)
                shoot_sound.play()
            if self.power >= 4:
                bullet1 = Bullet(self.rect.right + 5, self.rect.centery, 'sm')
                bullet2 = Bullet(self.rect.left - 5, self.rect.centery, 'sm')
                bullet3 = Bullet(self.rect.right - 10, self.rect.top, 'lg')
                bullet4 = Bullet(self.rect.left + 10, self.rect.top, 'lg')
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                all_sprites.add(bullet3)
                all_sprites.add(bullet4)
                bullets.add(bullet1)
                bullets.add(bullet2)
                bullets.add(bullet3)
                bullets.add(bullet4)
                shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (W / 2, H + 200)  # Телепортируем на время смерти

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()


# Класс метеоритов
class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width / 2.6)
        self.dif = 0
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(W - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1 + self.dif, 8 + self.dif)
        self.speedx = random.randrange(-3, 3)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()
        self.last_score = score
        self.lives = int(self.rect.width / 30 + 1)

    # Вращение метеоритов
    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            # print("rotated")
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def dif_increase(self):
        now = score
        if now - self.last_score > 500:
            self.dif += 1
            self.last_score = now

    def update(self):
        self.rotate()
        self.dif_increase()
        self.rect.y += self.speedy
        self.rect.x += self.speedx

        if (self.rect.top > H + 10 or self.rect.top < 0) and game.clear:
            self.kill()

        if self.rect.top > H + 10:  # Если моб уходит вниз, то тпхаем его наверх
            self.rect.x = random.randrange(W - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1 + self.dif, 8 + self.dif)


# Класс апгрейдов
class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy

        if self.rect.top > H:
            self.kill()


# Класс врывов
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


# Класс игры (здесь находятся основные параметры игры, а также функции для изменения уровней)
class Game():
    def __init__(self):
        self.clear = False
        self.wait = False

        self.stage = 0
        self.limit = 5000
        self.relax = 0
        self.last_spawn = pygame.time.get_ticks()
        self.spawn_rate = 15000

        self.music_state = Music_state
        self.sound_state = Sound_state
        self.highscore = Highscore
        self.first_game = True

    # Смена уровня
    def boss(self):
        if not self.wait:
            game.relax = pygame.time.get_ticks()
            self.wait = True
            self.clear = True
            # Смена музыки
            pygame.mixer.music.load(os.path.join(snd_dir, 'unstoppable_driver.wav'))
            pygame.mixer.music.set_volume(1)
            pygame.mixer.music.play(loops=-1)

        now = pygame.time.get_ticks()
        if now - game.relax >= 9000:
            self.wait = False
            self.clear = False

            self.stage = 1
            self.limit = 999999

            for i in range(20):
                newmob()


# Класс кнопок
class Button():
    def __init__(self, surf, text, size, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.active = False
        self.x = x
        self.y = y
        self.size = size
        self.text = text
        self.surf = surf

        self.font = pygame.font.Font(font_name, self.size)
        self.text_surface = self.font.render(text, True, WHITE)
        self.rect = self.text_surface.get_rect()

    def update(self):

        if self.active:
            text = '> ' + self.text + ' <'
        else:
            text = self.text

        self.text_surface = self.font.render(text, True, WHITE)
        self.rect = self.text_surface.get_rect()
        self.rect.midtop = (self.x, self.y)
        # self.surf.blit(self.text_surface, self.rect)


# Класс врагов
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = enemy_img
        self.image = pygame.transform.scale(self.image, (50, 38))
        self.rect = self.image.get_rect()
        self.radius = 20

        self.rect.x = random.randrange(W - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(2, 4)

        self.shoot_delay = 400
        self.last_shot = pygame.time.get_ticks()
        self.lives = 10

    def update(self):
        self.shoot()
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        if self.rect.top >= 10:
            self.speedy = 0
        if self.rect.right > W or self.rect.left < 0:
            self.speedx *= -1

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            enemy_bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
            all_sprites.add(enemy_bullet)
            enemy_bullets.add(enemy_bullet)


# Это показатель громкости
class Mixer(pygame.sprite.Sprite):
    def __init__(self, x, y, state):
        pygame.sprite.Sprite.__init__(self)

        self.state = state
        self.image = volume_mixer[self.state]
        self.rect = self.image.get_rect()

        self.rect.centerx = x
        self.rect.centery = y

    def update(self):
        self.image = volume_mixer[self.state]
        self.image = volume_mixer[self.state]
        center = self.rect.center

        self.rect = self.image.get_rect()
        self.rect.center = center


# Функция для вывода текста (можно не париться, создавая отдельные label)
font_name = pygame.font.match_font('droidsans')


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


all_sprites = pygame.sprite.Group()  # << для чего это? понятия не имею


# А всё понял, мы будем писать all_sprites.update(),
# чтобы не обновлять каждый спрайт по отдельности, умно, умно...

# Функции, создающие метеоритов и врагов
def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)


def newenemy():
    m = Enemy()
    all_sprites.add(m)
    enemies.add(m)


# Инициализируем игрока и мобов
player = Player()
game = Game()
all_sprites.add(player)
mobs = pygame.sprite.Group()

for i in range(8):
    newmob()


# Полоса здоровья
def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100 * (1 + player.Shield_lvl / 3)
    BAR_HEIGHT = 10
    fill = (pct / (100 * (1 + player.Shield_lvl / 3))) * BAR_LENGTH
    fill2 = BAR_LENGTH - fill
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    fill2_rect = pygame.Rect(x + fill, y, fill2, BAR_HEIGHT)
    pygame.draw.rect(surf, RED, fill2_rect)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


# Полоса энергии
def draw_energy_bar(surf, x, y, pct):
    if player.power == 1:
        pct = 100
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (1 - pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, YELLOW, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


# Прорисовка жизней
def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)


# Пауза
def pause():
    global game_over

    pygame.display.flip()
    play_background = pygame.display.get_surface()
    play_background_rect = play_background.get_rect()

    button1 = Button(screen, "Continue", 40, W / 2, H / 2.5 - 100)
    button2 = Button(screen, "Settings", 40, W / 2, H / 2.5)
    button3 = Button(screen, "Give up", 40, W / 2, H / 2.5 + 100)
    button4 = Button(screen, "Exit", 40, W / 2, H / 2.5 + 200)
    all_buttons = (button1, button2, button3, button4)

    waiting = True
    cnt = 0
    while waiting:

        clock.tick(FPS)
        # Нужно зарисовывать экран картинкой со всеми игровыми элементами, но я хз как её получить
        # Пробовал через pygame.display.get_surface(), не вышло
        screen.blit(background, background_rect)  # << Проблема тут  !!!
        draw_text(screen, "Pause", 82, W / 2, H / 20)

        for i in range(len(all_buttons)):
            if i != cnt:
                all_buttons[i].active = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    cnt = (cnt + 1) % 4
                if event.key == pygame.K_UP:
                    cnt = (cnt - 1) % 4
                if event.key == pygame.K_ESCAPE:
                    waiting = False

                if event.key == pygame.K_RETURN:
                    if cnt == 0:
                        waiting = False
                    if cnt == 1:
                        show_settings()
                    if cnt == 2:
                        game_over = True
                        screen.blit(background, background_rect)
                        pygame.display.flip()
                        waiting = False
                    if cnt == 3:
                        pygame.quit()
                        exit()

        all_buttons[cnt].active = True
        for but in all_buttons:
            but.update()
            but.surf.blit(but.text_surface, but.rect)
        pygame.display.flip()


# Долгожданная менюшка             
def menu():
    button1 = Button(screen, "Play", 40, W / 2, H * 4 / 7 - 160)
    button2 = Button(screen, "Shop", 40, W / 2, H * 4 / 7 - 80)
    button3 = Button(screen, "Settings", 40, W / 2, H * 4 / 7)
    button4 = Button(screen, "Exit", 40, W / 2, H * 4 / 7 + 80)
    all_buttons = (button1, button2, button3, button4)

    waiting = True
    cnt = 0
    while waiting:
        clock.tick(FPS)

        screen.blit(background, background_rect)
        draw_text(screen, "Space Adventure", 64, W / 2, H / 10)
        draw_text(screen, "Your highscore >> " + str(game.highscore), 28, W / 2, H - 50)

        for i in range(len(all_buttons)):
            if i != cnt:
                all_buttons[i].active = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    cnt = (cnt + 1) % 4
                if event.key == pygame.K_UP:
                    cnt = (cnt - 1) % 4

                if event.key == pygame.K_RETURN:
                    if cnt == 0:
                        waiting = False
                    if cnt == 1:
                        show_shop()
                    if cnt == 2:
                        show_settings()
                    if cnt == 3:
                        pygame.quit()
                        exit()

        all_buttons[cnt].active = True
        for but in all_buttons:
            but.update()
            but.surf.blit(but.text_surface, but.rect)
        pygame.display.flip()
        # print(button1.active, button2.active, button3.active)


# Настройки

def show_settings():
    button1 = Button(screen, "Sound", 40, W / 2, H / 2 - 100)
    button2 = Button(screen, "Music", 40, W / 2, H / 2)
    button3 = Button(screen, "Back", 40, W / 2, H / 2 + 100)
    all_buttons = (button1, button2, button3)

    state1 = game.sound_state
    state2 = game.music_state

    mixer1 = Mixer(W / 2 + 100, H / 2 - 95, state1)
    mixer2 = Mixer(W / 2 + 100, H / 2 + 5, state2)
    all_mixers = (mixer1, mixer2)
    mixers = pygame.sprite.Group()
    mixers.add(mixer1)
    mixers.add(mixer2)

    waiting = True
    cnt = 0
    while waiting:
        clock.tick(FPS)

        screen.blit(background, background_rect)
        draw_text(screen, "Settings", 64, W / 2, H / 10)

        for i in range(len(all_buttons)):
            if i != cnt:
                all_buttons[i].active = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    cnt = (cnt + 1) % 3
                if event.key == pygame.K_UP:
                    cnt = (cnt - 1) % 3

                if event.key == pygame.K_RETURN:
                    if cnt == 2:
                        waiting = False
                if event.key == pygame.K_RIGHT:
                    if cnt == 0:
                        state1 += 1
                        if state1 > 3:
                            state1 = 3
                    if cnt == 1:
                        state2 += 1
                        if state2 > 3:
                            state2 = 3
                if event.key == pygame.K_LEFT:
                    if cnt == 0:
                        state1 -= 1
                        if state1 < 0:
                            state1 = 0
                    if cnt == 1:
                        state2 -= 1
                        if state2 < 0:
                            state2 = 0

        all_buttons[cnt].active = True
        for but in all_buttons:
            but.update()
            but.surf.blit(but.text_surface, but.rect)

        mixer1.state = state1
        mixer2.state = state2
        game.sound_state = state1
        game.music_state = state2

        # Загрузка данных в файл для сохранения
        sound_file = open(os.path.join(data_dir, 'sound.txt'), 'w')
        sound_file.write('Sound_state {}\n'.format(state1))
        sound_file.write('Music_state {}\n'.format(state2))
        Sound_state = All_sound_state[0].split()[1]
        Music_state = All_sound_state[1].split()[1]
        sound_file.close()

        for snd in all_sounds:
            snd.set_volume(state1 / 3)
        pygame.mixer.music.set_volume(state2 / 3)

        for m in all_mixers:
            m.update()
        mixers.draw(screen)

        pygame.display.flip()


def show_shop():
    MAX = 3
    Upgrade_Levels = []
    for i in (player.Power_lvl, player.Shield_lvl, player.Atkspeed_lvl):
        if i == MAX:
            Upgrade_Levels.append('MAX')
        else:
            Upgrade_Levels.append(str(i))

    button1 = Button(screen, "Power lvl " + Upgrade_Levels[0], 30, W / 2, H / 2.3 - 100)
    button2 = Button(screen, "Shield lvl " + Upgrade_Levels[1], 30, W / 2, H / 2.3)
    button3 = Button(screen, "Atk Speed lvl " + Upgrade_Levels[2], 30, W / 2, H / 2.3 + 100)
    button4 = Button(screen, "Back", 30, W / 2, H / 2.3 + 200)
    all_buttons = (button1, button2, button3, button4)

    waiting = True
    cnt = 0
    while waiting:
        clock.tick(FPS)

        screen.blit(background, background_rect)
        draw_text(screen, "Shop", 64, W / 2, H / 10)
        draw_text(screen, "Your money >> " + str(player.money), 28, W / 2, H - 50)
        draw_text(screen, "Info:", 35, W / 2 + 100, H / 2.3 - 110)
        outline_rect = pygame.Rect(W / 2 - 10, H / 2 - 100, 220, 70)
        pygame.draw.rect(screen, WHITE, outline_rect, 3)
        outline_rect = pygame.Rect(W / 2 - 10, H / 2 - 30, 220, 30)
        pygame.draw.rect(screen, WHITE, outline_rect, 3)

        power_cost = 50 * player.Power_lvl
        shield_cost = 50 * player.Shield_lvl
        atkspeed_cost = 50 * player.Atkspeed_lvl

        for i in range(len(all_buttons)):
            if i != cnt:
                all_buttons[i].active = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    cnt = (cnt + 1) % 4
                if event.key == pygame.K_UP:
                    cnt = (cnt - 1) % 4

                if event.key == pygame.K_RETURN:
                    if cnt == 0 and player.Power_lvl < 3 and player.money >= power_cost:
                        player.Power_lvl += 1
                        player.money -= power_cost
                        if player.Power_lvl < 3:
                            text = "Power lvl " + str(player.Power_lvl)
                        else:
                            text = "Power lvl MAX"
                        button1.text = text
                    if cnt == 1 and player.Shield_lvl < 3 and player.money >= shield_cost:
                        player.Shield_lvl += 1
                        player.money -= shield_cost
                        if player.Shield_lvl < 3:
                            text = "Shield lvl " + str(player.Shield_lvl)
                        else:
                            text = "Shield lvl MAX"
                        button2.text = text
                    if cnt == 2 and player.Atkspeed_lvl < 3 and player.money >= atkspeed_cost:
                        player.Atkspeed_lvl += 1
                        player.money -= atkspeed_cost
                        if player.Atkspeed_lvl < 3:
                            text = "Atk speed lvl " + str(player.Atkspeed_lvl)
                        else:
                            text = "Atk speed lvl MAX"
                        button3.text = text
                    if cnt == 3:
                        waiting = False

                    money_file = open(os.path.join(data_dir, 'money.txt'), 'w')
                    money_file.write(str(player.money))
                    money_file.close()

                    stats_file = open(os.path.join(data_dir, 'stats.txt'), 'w')
                    stats_file.write('Power_lvl {}\n'.format(player.Power_lvl))
                    stats_file.write('Shield_lvl {}\n'.format(player.Shield_lvl))
                    stats_file.write('Atk_speed_lvl {}\n'.format(player.Atkspeed_lvl))
                    stats_file.close()

        if cnt == 0:
            draw_text(screen, "Increases starting", 30, W / 2 + 100, H / 2.3 - 50)
            draw_text(screen, "power lvl", 30, W / 2 + 100, H / 2.3 - 20)
            if player.Power_lvl == MAX:
                text = '--'
            else:
                text = str(power_cost)
            draw_text(screen, "Upgrade cost >> " + text, 30, W / 2 + 100, H / 2.3 + 15)
        if cnt == 1:
            draw_text(screen, "Increases maximum", 30, W / 2 + 100, H / 2.3 - 50)
            draw_text(screen, "shield value", 30, W / 2 + 100, H / 2.3 - 20)
            if player.Shield_lvl == MAX:
                text = '--'
            else:
                text = str(shield_cost)
            draw_text(screen, "Upgrade cost >> " + text, 30, W / 2 + 100, H / 2.3 + 15)
        if cnt == 2:
            draw_text(screen, "Increases attack", 30, W / 2 + 100, H / 2.3 - 50)
            draw_text(screen, "speed of your ship", 30, W / 2 + 100, H / 2.3 - 20)
            if player.Atkspeed_lvl == MAX:
                text = '--'
            else:
                text = str(atkspeed_cost)
            draw_text(screen, "Upgrade cost >> " + text, 30, W / 2 + 100, H / 2.3 + 15)
        if cnt == 3:
            draw_text(screen, "Choose an upgrade", 30, W / 2 + 100, H / 2.3 - 50)
            draw_text(screen, "Upgrade cost >>  --", 30, W / 2 + 100, H / 2.3 + 15)
        all_buttons[cnt].active = True
        for but in all_buttons:
            but.update()
            but.rect.left = 20
            but.surf.blit(but.text_surface, but.rect)

        pygame.display.flip()
        # print(button1.active, button2.active, button3.active)


def game_over_screen(scor):
    button1 = Button(screen, "Play again", 40, W / 2, H / 2 - 100)
    button2 = Button(screen, "Back to menu", 40, W / 2, H / 2)
    button3 = Button(screen, "Exit", 40, W / 2, H / 2 + 100)
    all_buttons = (button1, button2, button3)

    added_money = int(((scor // 500) ** (4 / 3)) // 2)
    player.money += added_money

    money_file = open(os.path.join(data_dir, 'money.txt'), 'w')
    money_file.write(str(player.money))
    money_file.close()

    waiting = True
    cnt = 0
    while waiting:
        clock.tick(FPS)

        screen.blit(background, background_rect)
        draw_text(screen, "Game Over", 64, W / 2, H / 10)
        draw_text(screen, "You got {} money!".format(added_money), 30, W / 2, H / 10 + 80)
        draw_text(screen, "Your score >> " + str(scor), 28, W / 2, H - 50)

        for i in range(len(all_buttons)):
            if i != cnt:
                all_buttons[i].active = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    cnt = (cnt + 1) % 3
                if event.key == pygame.K_UP:
                    cnt = (cnt - 1) % 3

                if event.key == pygame.K_RETURN:
                    if cnt == 0:
                        waiting = False
                    if cnt == 1:
                        menu()
                        screen.blit(background, background_rect)
                        pygame.display.flip()
                        waiting = False
                    if cnt == 2:
                        pygame.quit()
                        exit()

        all_buttons[cnt].active = True
        for but in all_buttons:
            but.update()
            but.surf.blit(but.text_surface, but.rect)
        pygame.display.flip()
        # print(button1.active, button2.active, button3.active)


# Добавление основных групп
powerups = pygame.sprite.Group()

# Процесс игры


game_over = True
running = True
while running:
    if game_over:
        pygame.mixer.music.load(os.path.join(snd_dir, 'Wonderful.mp3'))
        pygame.mixer.music.set_volume(1)
        pygame.mixer.music.play(loops=-1)

        for snd in all_sounds:
            snd.set_volume(Sound_state / 3)
        pygame.mixer.music.set_volume(Music_state / 3)

        if not game.first_game:
            game_over_screen(score)
        else:
            menu()

        game_over = False
        game.first_game = False
        all_sprites = pygame.sprite.Group()

        mobs = pygame.sprite.Group()
        enemies = pygame.sprite.Group()

        bullets = pygame.sprite.Group()
        enemy_bullets = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)

        game.stage = 0
        game.limit = 5000
        game.spawn_rate = 15000

        for i in range(8):
            newmob()

        score = 0
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pause()

        if event.type == pygame.KEYUP:
            pass

    all_sprites.update()  # << великая вещь

    if score >= game.limit and game.stage == 0:
        game.boss()

    now = pygame.time.get_ticks()
    if now - game.last_spawn > game.spawn_rate and game.stage == 1:
        game.last_spawn = now
        game.spawn_rate *= 0.9
        newenemy()

    # Проверка коллайда "игрок - моб"
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius * 2
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        newmob()
        if player.shield <= 0:
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = player.maxshield
            fart_sound.play()
        if player.lives == 0:
            player.alive = False
            player.shield = 0

    # Обработка апгрейдов
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'shield':
            player.shield += random.randrange(10, 30)
            if player.shield >= player.maxshield:
                player.shield = player.maxshield
            shield_sound.play()
        if hit.type == 'gun':
            player.powerup()
            power_sound.play()

    # Проверка смерти игрока и анимации его смерти
    if not player.alive and not death_explosion.alive():

        if score > game.highscore:
            game.highscore = score
            highscore_file = open(os.path.join(data_dir, 'highscore.txt'), 'w')
            highscore_file.write(str(score))
            highscore_file.close()

        game_over = True

    # Проверка коллайда "моб - пуля"
    hits = pygame.sprite.groupcollide(mobs, bullets, False, True)
    for hit in hits:
        hit.lives -= 1
        if hit.lives > 0:
            random.choice(expl_sounds).play()
            expl_center = (hit.rect.center[0], hit.rect.bottom)
            expl = Explosion(expl_center, 'sm')
            all_sprites.add(expl)
        else:
            hit.kill()
            score += 50 + hit.radius  # Очки считаются от радиуса
            random.choice(expl_sounds).play()
            expl = Explosion(hit.rect.center, 'lg')
            all_sprites.add(expl)
            if random.random() > 0.9 + player.power / 170 - 0.01:
                pov = Pow(hit.rect.center)
                all_sprites.add(pov)
                powerups.add(pov)
            newmob()

    # Проверка коллайда "игрок - вражеская пуля"
    hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
    for hit in hits:
        player.shield -= 50
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        newmob()
        if player.shield <= 0:
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = player.maxshield
            fart_sound.play()
        if player.lives == 0:
            player.alive = False

    # Проверка коллайда "пуля - враг"
    hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
    for hit in hits:
        hit.lives -= 1
        if hit.lives > 0:
            random.choice(expl_sounds).play()
            expl_center = (hit.rect.center[0], hit.rect.bottom)
            expl = Explosion(expl_center, 'sm')
            all_sprites.add(expl)
        else:
            hit.kill()
            score += 500
            random.choice(expl_sounds).play()
            expl = Explosion(hit.rect.center, 'lg')
            all_sprites.add(expl)
            if random.random() > 0.9 + player.power / 170 - 0.01:
                pov = Pow(hit.rect.center)
                all_sprites.add(pov)
                powerups.add(pov)

    if player.power >= 4:
        pow_lev = 'MAX'
    else:
        pow_lev = player.power
    # Эта штука, кста, рендерингом называется
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 22, W / 2, 10)
    draw_text(screen, 'Power Lvl ' + str(pow_lev), 23, W - 60, 30)
    draw_shield_bar(screen, 5, 5, player.shield)
    draw_energy_bar(screen, W - 110, 5, (now - player.power_time) // 100)
    draw_lives(screen, 12, 25, player.lives, heart_mini_img)

    # А вот чем отличется display.update() от этого?
    pygame.display.flip()

pygame.quit()  # У меня когда-то эта штука стояла в строке после running = False
# и я удивлялся, что игра не закрывается
