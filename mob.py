import pygame
from settings import BLACK, WIDTH, HEIGHT
import random
from images import meteor_images


class Mob(pygame.sprite.Sprite):
    """Класс метеоритов"""

    def __init__(self, is_stop):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width / 2.6)
        self.dif = 0
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1 + self.dif, 8 + self.dif)
        self.speedx = random.randrange(-3, 3)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()
        self.lives = int(self.rect.width / 30 + 1)
        self.stop = is_stop

    # Вращение метеоритов
    def rotate(self):
        """Вращает метеорит"""
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

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx

        if (
                self.rect.top > HEIGHT + 10 or self.rect.top < 0 or self.rect.left > WIDTH or self.rect.right < 0) and self.stop:
            self.kill()

        if self.rect.top > HEIGHT + 10:  # Если моб уходит вниз, то тпхаем его наверх
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1 + self.dif, 8 + self.dif)
