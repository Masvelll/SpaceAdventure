import pygame
import random
import os
from player import Player
from enemy import Enemy
#from bullet import Bullet, EnemyBullet
from game import Game
from settings import DATA_DIR, sound_state, music_state, WIDTH, HEIGHT, FPS, WHITE, BLACK, RED, GREEN, YELLOW, IMG_DIR
from images import explosion_anim, enemy_img, background_rect, background, powerup_images, heart_mini_img
from music_manager import MusicManager
from spawn_manager import SpawnManager
import logging

from logging import config

log_config = {
    "version": 1,
    "root": {
        "handlers": ["console"],
        "level": "INFO"
    },
    "handlers": {
        "console": {
            "formatter": "std_out",
            "class": "logging.StreamHandler",
            "level": "DEBUG"
        }
    },
    "formatters": {
        "std_out": {
            "format": "%(asctime)s : %(levelname)s : %(module)s : %(funcName)s : %(lineno)d : %(message)s",
            "datefmt": "%d-%m-%Y %I:%M:%S"
        }
    },
}

config.dictConfig(log_config)

logger = logging.getLogger(__name__)

pygame.init()
pygame.mixer.init()  # это для звука (на будущее)
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # почему некоторые пишут screen, а некоторые surface?
pygame.display.set_caption("Space Adventure")  # лень придумывать название
clock = pygame.time.Clock()

volume_mixer = []
for i in range(4):
    filename = 'volume{}.png'.format(i)
    img = pygame.image.load(os.path.join(IMG_DIR, filename))
    img = pygame.transform.scale(img, (50, 30))

    volume_mixer.append(img)

# Пара игровых глобальных параметров
score = 0


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

        if self.rect.top > HEIGHT:
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


# Инициализируем игрока и мобов

music_manager = MusicManager()
game = Game(music_manager)

spawn_manager = SpawnManager(game)
mobs = pygame.sprite.Group()
player = Player(game.all_sprites, game.bullets, music_manager)

for i in range(8):
    spawn_manager.newmob(game)


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

    button1 = Button(screen, "Continue", 40, WIDTH / 2, HEIGHT / 2.5 - 100)
    button2 = Button(screen, "Settings", 40, WIDTH / 2, HEIGHT / 2.5)
    button3 = Button(screen, "Give up", 40, WIDTH / 2, HEIGHT / 2.5 + 100)
    button4 = Button(screen, "Exit", 40, WIDTH / 2, HEIGHT / 2.5 + 200)
    all_buttons = (button1, button2, button3, button4)

    waiting = True
    cnt = 0
    while waiting:

        clock.tick(FPS)
        # Нужно зарисовывать экран картинкой со всеми игровыми элементами, но я хз как её получить
        # Пробовал через pygame.display.get_surface(), не вышло
        screen.blit(background, background_rect)  # << Проблема тут  !!!
        draw_text(screen, "Pause", 82, WIDTH / 2, HEIGHT / 20)

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
    button1 = Button(screen, "Play", 40, WIDTH / 2, HEIGHT * 4 / 7 - 160)
    button2 = Button(screen, "Shop", 40, WIDTH / 2, HEIGHT * 4 / 7 - 80)
    button3 = Button(screen, "Settings", 40, WIDTH / 2, HEIGHT * 4 / 7)
    button4 = Button(screen, "Exit", 40, WIDTH / 2, HEIGHT * 4 / 7 + 80)
    all_buttons = (button1, button2, button3, button4)

    waiting = True
    cnt = 0
    while waiting:
        clock.tick(FPS)

        screen.blit(background, background_rect)
        draw_text(screen, "Space Adventure", 64, WIDTH / 2, HEIGHT / 10)
        draw_text(screen, "Your highscore >> " + str(game.highscore), 28, WIDTH / 2, HEIGHT - 50)

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
    button1 = Button(screen, "Sound", 40, WIDTH / 2, HEIGHT / 2 - 100)
    button2 = Button(screen, "Music", 40, WIDTH / 2, HEIGHT / 2)
    button3 = Button(screen, "Back", 40, WIDTH / 2, HEIGHT / 2 + 100)
    all_buttons = (button1, button2, button3)

    state1 = game.sound_state
    state2 = game.music_state

    mixer1 = Mixer(WIDTH / 2 + 100, HEIGHT / 2 - 95, state1)
    mixer2 = Mixer(WIDTH / 2 + 100, HEIGHT / 2 + 5, state2)
    all_mixers = (mixer1, mixer2)
    mixers = pygame.sprite.Group()
    mixers.add(mixer1)
    mixers.add(mixer2)

    waiting = True
    cnt = 0
    while waiting:
        clock.tick(FPS)

        screen.blit(background, background_rect)
        draw_text(screen, "Settings", 64, WIDTH / 2, HEIGHT / 10)

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
        sound_file = open(os.path.join(DATA_DIR, 'sound.txt'), 'w')
        sound_file.write('Sound_state {}\n'.format(state1))
        sound_file.write('Music_state {}\n'.format(state2))
        # Sound_state = All_sound_state[0].split()[1]
        # Music_state = All_sound_state[1].split()[1]
        sound_file.close()

        for snd in music_manager.all_sounds:
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

    button1 = Button(screen, "Power lvl " + Upgrade_Levels[0], 30, WIDTH / 2, HEIGHT / 2.3 - 100)
    button2 = Button(screen, "Shield lvl " + Upgrade_Levels[1], 30, WIDTH / 2, HEIGHT / 2.3)
    button3 = Button(screen, "Atk Speed lvl " + Upgrade_Levels[2], 30, WIDTH / 2, HEIGHT / 2.3 + 100)
    button4 = Button(screen, "Back", 30, WIDTH / 2, HEIGHT / 2.3 + 200)
    all_buttons = (button1, button2, button3, button4)

    waiting = True
    cnt = 0
    while waiting:
        clock.tick(FPS)

        screen.blit(background, background_rect)
        draw_text(screen, "Shop", 64, WIDTH / 2, HEIGHT / 10)
        draw_text(screen, "Your money >> " + str(player.money), 28, WIDTH / 2, HEIGHT - 50)
        draw_text(screen, "Info:", 35, WIDTH / 2 + 100, HEIGHT / 2.3 - 110)
        outline_rect = pygame.Rect(WIDTH / 2 - 10, HEIGHT / 2 - 100, 220, 70)
        pygame.draw.rect(screen, WHITE, outline_rect, 3)
        outline_rect = pygame.Rect(WIDTH / 2 - 10, HEIGHT / 2 - 30, 220, 30)
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

                    money_file = open(os.path.join(DATA_DIR, 'money.txt'), 'w')
                    money_file.write(str(player.money))
                    money_file.close()

                    stats_file = open(os.path.join(DATA_DIR, 'stats.txt'), 'w')
                    stats_file.write('Power_lvl {}\n'.format(player.Power_lvl))
                    stats_file.write('Shield_lvl {}\n'.format(player.Shield_lvl))
                    stats_file.write('Atk_speed_lvl {}\n'.format(player.Atkspeed_lvl))
                    stats_file.close()

        if cnt == 0:
            draw_text(screen, "Increases starting", 30, WIDTH / 2 + 100, HEIGHT / 2.3 - 50)
            draw_text(screen, "power lvl", 30, WIDTH / 2 + 100, HEIGHT / 2.3 - 20)
            if player.Power_lvl == MAX:
                text = '--'
            else:
                text = str(power_cost)
            draw_text(screen, "Upgrade cost >> " + text, 30, WIDTH / 2 + 100, HEIGHT / 2.3 + 15)
        if cnt == 1:
            draw_text(screen, "Increases maximum", 30, WIDTH / 2 + 100, HEIGHT / 2.3 - 50)
            draw_text(screen, "shield value", 30, WIDTH / 2 + 100, HEIGHT / 2.3 - 20)
            if player.Shield_lvl == MAX:
                text = '--'
            else:
                text = str(shield_cost)
            draw_text(screen, "Upgrade cost >> " + text, 30, WIDTH / 2 + 100, HEIGHT / 2.3 + 15)
        if cnt == 2:
            draw_text(screen, "Increases attack", 30, WIDTH / 2 + 100, HEIGHT / 2.3 - 50)
            draw_text(screen, "speed of your ship", 30, WIDTH / 2 + 100, HEIGHT / 2.3 - 20)
            if player.Atkspeed_lvl == MAX:
                text = '--'
            else:
                text = str(atkspeed_cost)
            draw_text(screen, "Upgrade cost >> " + text, 30, WIDTH / 2 + 100, HEIGHT / 2.3 + 15)
        if cnt == 3:
            draw_text(screen, "Choose an upgrade", 30, WIDTH / 2 + 100, HEIGHT / 2.3 - 50)
            draw_text(screen, "Upgrade cost >>  --", 30, WIDTH / 2 + 100, HEIGHT / 2.3 + 15)
        all_buttons[cnt].active = True
        for but in all_buttons:
            but.update()
            but.rect.left = 20
            but.surf.blit(but.text_surface, but.rect)

        pygame.display.flip()
        # print(button1.active, button2.active, button3.active)


def game_over_screen(scor):
    button1 = Button(screen, "Play again", 40, WIDTH / 2, HEIGHT / 2 - 100)
    button2 = Button(screen, "Back to menu", 40, WIDTH / 2, HEIGHT / 2)
    button3 = Button(screen, "Exit", 40, WIDTH / 2, HEIGHT / 2 + 100)
    all_buttons = (button1, button2, button3)

    added_money = int(((scor // 500) ** (4 / 3)) // 2)
    player.money += added_money

    money_file = open(os.path.join(DATA_DIR, 'money.txt'), 'WIDTH')
    money_file.write(str(player.money))
    money_file.close()

    waiting = True
    cnt = 0
    while waiting:
        clock.tick(FPS)

        screen.blit(background, background_rect)
        draw_text(screen, "Game Over", 64, WIDTH / 2, HEIGHT / 10)
        draw_text(screen, "You got {} money!".format(added_money), 30, WIDTH / 2, HEIGHT / 10 + 80)
        draw_text(screen, "Your score >> " + str(scor), 28, WIDTH / 2, HEIGHT - 50)

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
                        menu(player)
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
        music_manager.music_init()

        for snd in music_manager.all_sounds:
            snd.set_volume(sound_state / 3)
        pygame.mixer.music.set_volume(music_state / 3)

        if not game.first_game:
            game_over_screen(score)
        else:
            menu()

        game_over = False
        game.first_game = False
        # all_sprites = pygame.sprite.Group()

        # mobs = pygame.sprite.Group()
        # enemies = pygame.sprite.Group()

        # bullets = pygame.sprite.Group()
        # enemy_bullets = pygame.sprite.Group()

        game.all_sprites.add(player)

        game.stage = 0
        game.limit = 5000
        game.spawn_rate = 15000

        for i in range(8):
            spawn_manager.newmob(game)

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

    game.all_sprites.update()

    if score >= game.limit and game.stage == 0:
        game.next_level(music_manager, spawn_manager)

    now = pygame.time.get_ticks()
    if now - game.last_spawn > game.spawn_rate and game.stage == 1:
        game.last_spawn = now
        game.spawn_rate *= 0.9
        spawn_manager.spawn_enemy(game)

    # Проверка коллайда "игрок - моб"
    hits = pygame.sprite.spritecollide(player, game.mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius * 2
        expl = Explosion(hit.rect.center, 'sm')
        game.all_sprites.add(expl)
        spawn_manager.newmob(game)
        if player.shield <= 0:
            death_explosion = Explosion(player.rect.center, 'player')
            game.all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = player.maxshield
            music_manager.fart_sound.play()
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
            music_manager.shield_sound.play()
        if hit.type == 'gun':
            player.powerup()
            music_manager.power_sound.play()

    # Проверка смерти игрока и анимации его смерти
    if not player.alive and not death_explosion.alive():

        if score > game.highscore:
            game.highscore = score
            highscore_file = open(os.path.join(DATA_DIR, 'highscore.txt'), 'w')
            highscore_file.write(str(score))
            highscore_file.close()

        game_over = True

    # Проверка коллайда "моб - пуля"
    hits = pygame.sprite.groupcollide(game.mobs, game.bullets, False, True)
    # logger.debug(hits)
    for hit in hits:
        hit.lives -= 1
        if hit.lives > 0:
            random.choice(music_manager.expl_sounds).play()
            expl_center = (hit.rect.center[0], hit.rect.bottom)
            expl = Explosion(expl_center, 'sm')
            game.all_sprites.add(expl)
        else:
            hit.kill()
            score += 50 + hit.radius  # Очки считаются от радиуса
            random.choice(music_manager.expl_sounds).play()
            expl = Explosion(hit.rect.center, 'lg')
            game.all_sprites.add(expl)
            if random.random() > 0.9 + player.power / 170 - 0.01:
                pov = Pow(hit.rect.center)
                game.all_sprites.add(pov)
                powerups.add(pov)
            spawn_manager.newmob(game)

    # Проверка коллайда "игрок - вражеская пуля"
    hits = pygame.sprite.spritecollide(player, game.enemy_bullets, True)
    for hit in hits:
        player.shield -= 50
        expl = Explosion(hit.rect.center, 'sm')
        game.all_sprites.add(expl)
        spawn_manager.newmob(game)
        if player.shield <= 0:
            death_explosion = Explosion(player.rect.center, 'player')
            game.all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = player.maxshield
            music_manager.fart_sound.play()
        if player.lives == 0:
            player.alive = False

    # Проверка коллайда "пуля - враг"
    hits = pygame.sprite.groupcollide(game.enemies, game.bullets, False, True)
    for hit in hits:
        hit.lives -= 1
        if hit.lives > 0:
            random.choice(music_manager.expl_sounds).play()
            expl_center = (hit.rect.center[0], hit.rect.bottom)
            expl = Explosion(expl_center, 'sm')
            game.all_sprites.add(expl)
        else:
            hit.kill()
            score += 500
            random.choice(music_manager.expl_sounds).play()
            expl = Explosion(hit.rect.center, 'lg')
            game.all_sprites.add(expl)
            if random.random() > 0.9 + player.power / 170 - 0.01:
                pov = Pow(hit.rect.center)
                game.all_sprites.add(pov)
                powerups.add(pov)

    if player.power >= 4:
        pow_lev = 'MAX'
    else:
        pow_lev = player.power
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    game.all_sprites.draw(screen)
    draw_text(screen, str(score), 22, WIDTH / 2, 10)
    draw_text(screen, 'Power Lvl ' + str(pow_lev), 23, WIDTH - 60, 30)
    draw_shield_bar(screen, 5, 5, player.shield)
    draw_energy_bar(screen, WIDTH - 110, 5, (now - player.power_time) // 100)
    draw_lives(screen, 12, 25, player.lives, heart_mini_img)
    pygame.display.flip()

pygame.quit()
