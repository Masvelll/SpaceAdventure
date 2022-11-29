import pygame
import os
from settings import H, W
from bullet import Bullet, EnemyBullet
import sys

config_name = 'myapp.cfg'
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

config_path = os.path.join(application_path, config_name)

img_dir = os.path.join(application_path, 'img')
player_img = pygame.image.load(os.path.join(img_dir, "playerShip2_green.png"))

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