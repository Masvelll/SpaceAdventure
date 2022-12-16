import pygame
from images import enemy_bullet_img, bullet_images, boss_bullet_anim
from settings import HEIGHT


class PlayerBullet(pygame.sprite.Sprite):
    """Класс пуль игрока"""
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


class EnemyBullet(pygame.sprite.Sprite):
    """Класс пуль врагов"""
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


class BossBullet(pygame.sprite.Sprite):
    """Класс пуль Босса"""
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = boss_bullet_anim[0]
        self.rect = self.image.get_rect()
        self.rect.top = y
        self.rect.centerx = x
        self.speedy = 10
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 150

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(boss_bullet_anim):
                self.kill()
            else:
                center = self.rect.center
                self.image = boss_bullet_anim[self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


