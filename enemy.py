import pygame
import random
from bullet import EnemyBullet
from images import enemy_img
from settings import WIDTH


class Enemy(pygame.sprite.Sprite):
    def __init__(self, all_sprites, enemy_bullets):
        pygame.sprite.Sprite.__init__(self)
        self.image = enemy_img
        self.image = pygame.transform.scale(self.image, (50, 38))
        self.rect = self.image.get_rect()
        self.radius = 20

        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(2, 4)

        self.shoot_delay = 400
        self.last_shot = pygame.time.get_ticks()
        self.lives = 10

        self.all_sprites = all_sprites
        self.enemy_bullets = enemy_bullets

    def update(self):
        self.shoot()
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        if self.rect.top >= 10:
            self.speedy = 0
        if self.rect.right > WIDTH or self.rect.left < 0:
            self.speedx *= -1

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            enemy_bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
            self.all_sprites.add(enemy_bullet)
            self.enemy_bullets.add(enemy_bullet)
