import pygame
import os
from settings import IMG_DIR, BLACK, WIDTH, HEIGHT

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

background = pygame.image.load(os.path.join(IMG_DIR, 'starfield.png'))
background_rect = background.get_rect()
player_img = pygame.image.load(os.path.join(IMG_DIR, "playerShip2_green.png"))
pygame.display.set_icon(player_img)

meteor_images = []
meteor_list = ['meteorBrown_big1.png', 'meteorBrown_med1.png',
               'meteorBrown_med1.png', 'meteorBrown_med3.png',
               'meteorBrown_small1.png', 'meteorBrown_small2.png',
               'meteorBrown_tiny1.png']
for img in meteor_list:
    meteor_images.append(pygame.image.load(os.path.join(IMG_DIR, img)).convert())

enemy_img = pygame.image.load(os.path.join(IMG_DIR, "playerShip1_red.png"))

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

heart_img = pygame.image.load(os.path.join(IMG_DIR, 'heart.png')).convert()
heart_mini_img = pygame.transform.scale(heart_img, (25, 25))
heart_mini_img.set_colorkey(BLACK)

powerup_images = {
    'shield': pygame.image.load(os.path.join(IMG_DIR, 'shield_gold.png')),
    'gun': pygame.image.load(os.path.join(IMG_DIR, 'bolt_gold.png'))

}

bullet_images = {
    'lg': pygame.image.load(os.path.join(IMG_DIR, "laserGreen10.png")),
    'sm': pygame.image.load(os.path.join(IMG_DIR, "laserGreen13.png"))
}

enemy_bullet_img = pygame.image.load(os.path.join(IMG_DIR, "laserRed06.png"))
