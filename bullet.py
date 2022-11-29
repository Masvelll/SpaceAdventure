import pygame
import os
import sys
from settings import HEIGHT

config_name = 'myapp.cfg'

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

config_path = os.path.join(application_path, config_name)

IMG_DIR = os.path.join(application_path, 'img')
bullet_images = {
    'lg': pygame.image.load(os.path.join(IMG_DIR, "laserGreen10.png")),
    'sm': pygame.image.load(os.path.join(IMG_DIR, "laserGreen13.png"))
}

enemy_bullet_img = pygame.image.load(os.path.join(IMG_DIR, "laserRed06.png"))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_images[size]
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy

        if self.rect.bottom < 0:
            self.kill()


# Класс пуль врага
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = enemy_bullet_img
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = 10

    def update(self):
        self.rect.y += self.speedy

        if self.rect.bottom > HEIGHT:
            self.kill()
