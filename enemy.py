import pygame
import random
from bullet import EnemyBullet, BossBullet
from images import enemy_img, boss_img, boss_shoot
from settings import WIDTH


class Enemy(pygame.sprite.Sprite):
    def __init__(self, all_sprites, enemy_bullets):
        pygame.sprite.Sprite.__init__(self)
        self.image = enemy_img
        self.image = pygame.transform.scale(self.image, (50, 38))
        self.rect = self.image.get_rect()
        self.radius = 80

        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(2, 4)

        self.shoot_delay = 500
        self.shoot_anim_delay = 200
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
class Boss(pygame.sprite.Sprite):
    def __init__(self, all_sprites, boss_bullets):
        pygame.sprite.Sprite.__init__(self)
        self.image = boss_img
        self.image = pygame.transform.scale(self.image, (200, 200))
        self.rect = self.image.get_rect()
        self.radius = 50

        self.rect.x = 240
        self.rect.y = 100
        self.speedy = random.randrange(-2, 2)
        self.speedx = random.randrange(-2, 2)
        self.lives = 1000

        self.shoot_delay = 5000
        self.current_shot = 0
        self.last_shot = pygame.time.get_ticks()
        self.last_change_img = pygame.time.get_ticks()
        self.charging = False

        self.all_sprites = all_sprites
        self.boss_bullets = boss_bullets

    def update(self):
        self.shoot()
        self.charge()
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        if self.rect.top <= 10 or self.rect.bottom >= 400:
            self.speedy *= -1
        if self.rect.right > WIDTH or self.rect.left < 0:
            self.speedx *= -1


    def shoot(self):
        now = pygame.time.get_ticks()



        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            boss_bullet = BossBullet(self.rect.centerx + 5, self.rect.bottom - 70)
            laser = BossBullet(self.rect.centerx + 5, self.rect.bottom - 70)
            self.all_sprites.add(boss_bullet, laser)
            self.boss_bullets.add(boss_bullet)

    def charge(self):
        now = pygame.time.get_ticks()
        if now - self.last_change_img > 50 and self.charging:

            self.current_shot = (self.current_shot + 1) % 11
            self.image = boss_shoot[self.current_shot]
            self.image = pygame.transform.scale(self.image, (200, 200))
            self.last_change_img = now
            print("changed image", self.current_shot)
        self.charging = False
        if now - self.last_shot > self.shoot_delay - 650:
            self.charging = True
        if self.charging == False:
            self.image = boss_shoot[0]
            self.current_shot = 0
            self.image = pygame.transform.scale(self.image, (200, 200))
        ########################################################
