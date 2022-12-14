import pygame
import os
from settings import IMG_DIR, BLACK, WIDTH, HEIGHT

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Импорт фона
background = pygame.image.load(os.path.join(IMG_DIR, 'starfield.png'))
background_rect = background.get_rect()

# Импорт картинки игрока
player_img = pygame.image.load(os.path.join(IMG_DIR, "playerShip2_green.png"))
pygame.display.set_icon(player_img)

# Импорт картинок метеоритов
meteor_images = []
meteor_list = ['meteorBrown_big1.png', 'meteorBrown_med1.png',
               'meteorBrown_med1.png', 'meteorBrown_med3.png',
               'meteorBrown_small1.png', 'meteorBrown_small2.png',
               'meteorBrown_tiny1.png']
for img in meteor_list:
    meteor_images.append(pygame.image.load(os.path.join(IMG_DIR, img)).convert())

# Импорт картинок маленького кораблика и БОССА
enemy_img = pygame.image.load(os.path.join(IMG_DIR, "playerShip1_red.png"))
boss_img = pygame.image.load(os.path.join(IMG_DIR, "BOSS 1.png"))

# Импорт картинок сердец
heart_img = pygame.image.load(os.path.join(IMG_DIR, 'heart.png')).convert()
heart_mini_img = pygame.transform.scale(heart_img, (25, 25))
heart_mini_img.set_colorkey(BLACK)

# Импорт картинок картинок апгрейдов
powerup_images = {
    'shield': pygame.image.load(os.path.join(IMG_DIR, 'shield_gold.png')),
    'gun': pygame.image.load(os.path.join(IMG_DIR, 'bolt_gold.png'))
}

# Импорт картинок картинок пуль
bullet_images = {
    'lg': pygame.image.load(os.path.join(IMG_DIR, "laserGreen10.png")),
    'sm': pygame.image.load(os.path.join(IMG_DIR, "laserGreen13.png"))
}
enemy_bullet_img = pygame.image.load(os.path.join(IMG_DIR, "laserRed06.png"))

# Анимация взрыва
explosion_anim = {
    'lg': [],
    'sm': [],
    'player': []
}
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(os.path.join(IMG_DIR, filename))
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(os.path.join(IMG_DIR, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)

# Анимация выстрела БОССА
boss_shoot = []
for i in range(11):
    filename = ''
    filename = 'BOSS {}.png'.format(i + 1)
    img = pygame.image.load(os.path.join(IMG_DIR, filename))
    img.set_colorkey(BLACK)
    boss_shoot.append(img)
boss_bullet_anim = []
for i in range(5):
    filename = ''
    filename = 'Lazer{}.png'.format(i + 1)
    img = pygame.image.load(os.path.join(IMG_DIR, filename))
    img.set_colorkey(BLACK)
    boss_bullet_anim.append(img)

# Картинки громкости звука
volume_mixer = []
for i in range(4):
    filename = 'volume{}.png'.format(i)
    img = pygame.image.load(os.path.join(IMG_DIR, filename))
    img = pygame.transform.scale(img, (50, 30))

    volume_mixer.append(img)
