import pygame
import random
import os
from player import Player
from rendering import draw_text, draw_shield_bar, draw_energy_bar, draw_lives
from game import Game
from buttons import Button, button_reset, button_check, button_update
from settings import sound_state, music_state, WIDTH, HEIGHT, FPS, WHITE, BLACK, IMG_DIR, DATA_DIR
from images import explosion_anim, background_rect, background, powerup_images, heart_mini_img
from music_manager import MusicManager
from spawn_manager import SpawnManager
from menus import Shop

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
display = pygame.Surface((WIDTH, HEIGHT))
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

# Инициализируем игрока и мобов

music_manager = MusicManager()


# Пауза
def pause():
    global game_over
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.flip()
    play_background = pygame.display.get_surface()
    play_background_rect = play_background.get_rect()

    button1 = Button(display, "Continue", 40, WIDTH / 2, HEIGHT / 2.5 - 100)
    button2 = Button(display, "Settings", 40, WIDTH / 2, HEIGHT / 2.5)
    button3 = Button(display, "Give up", 40, WIDTH / 2, HEIGHT / 2.5 + 100)
    button4 = Button(display, "Exit", 40, WIDTH / 2, HEIGHT / 2.5 + 200)
    all_buttons = (button1, button2, button3, button4)

    waiting = True
    current_button = 0
    while waiting:

        clock.tick(FPS)
        display.blit(background, background_rect)
        draw_text(display, "Pause", 82, WIDTH / 2, HEIGHT / 20)

        button_reset(all_buttons, current_button)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    current_button = (current_button + 1) % 4
                if event.key == pygame.K_UP:
                    current_button = (current_button - 1) % 4
                if event.key == pygame.K_ESCAPE:
                    waiting = False

                if event.key == pygame.K_RETURN:
                    if current_button == 0:
                        screen = pygame.display.set_mode((WIDTH * 1.2, HEIGHT * 1.2))
                        waiting = False
                    if current_button == 1:
                        show_settings()
                    if current_button == 2:
                        game_over = True
                        display.blit(background, background_rect)
                        pygame.display.flip()
                        waiting = False
                    if current_button == 3:
                        pygame.quit()
                        exit()

        all_buttons[current_button].active = True
        for but in all_buttons:
            but.update()
            but.surf.blit(but.text_surface, but.rect)

        screen.blit(pygame.transform.scale(display, (WIDTH, HEIGHT)), (0, 0))
        pygame.display.flip()


# Долгожданная менюшка
def menu(show_shop):
    def stop_waiting():
        nonlocal waiting
        waiting = False

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    button1 = Button(display, "Play", 40, WIDTH / 2, HEIGHT * 4 / 7 - 160, stop_waiting)
    button2 = Button(display, "Shop", 40, WIDTH / 2, HEIGHT * 4 / 7 - 80, show_shop)
    button3 = Button(display, "Settings", 40, WIDTH / 2, HEIGHT * 4 / 7, show_settings)
    button4 = Button(display, "Exit", 40, WIDTH / 2, HEIGHT * 4 / 7 + 80, pygame.quit)
    all_buttons = (button1, button2, button3, button4)
    button_amount = len(all_buttons)

    waiting = True
    current_button = 0
    while waiting:
        clock.tick(FPS)

        display.blit(background, background_rect)
        draw_text(display, "Space Adventure", 64, WIDTH / 2, HEIGHT / 10)
        draw_text(display, "Your highscore >> " + str(game.highscore), 28, WIDTH / 2, HEIGHT - 50)

        button_reset(all_buttons, current_button)
        current_button = button_check(current_button, button_amount, all_buttons)

        all_buttons[current_button].active = True
        button_update(all_buttons)

        screen.blit(pygame.transform.scale(display, (WIDTH, HEIGHT)), (0, 0))
        pygame.display.flip()


# Настройки

def show_settings():
    button1 = Button(display, "Sound", 40, WIDTH / 2, HEIGHT / 2 - 100)
    button2 = Button(display, "Music", 40, WIDTH / 2, HEIGHT / 2)
    button3 = Button(display, "Back", 40, WIDTH / 2, HEIGHT / 2 + 100)
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

        display.blit(background, background_rect)
        draw_text(display, "Settings", 64, WIDTH / 2, HEIGHT / 10)

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
        mixers.draw(display)

        screen.blit(pygame.transform.scale(display, (WIDTH, HEIGHT)), (0, 0))
        pygame.display.flip()


def game_over_screen(scor):
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    button1 = Button(display, "Play again", 40, WIDTH / 2, HEIGHT / 2 - 100)
    button2 = Button(display, "Back to menu", 40, WIDTH / 2, HEIGHT / 2)
    button3 = Button(display, "Exit", 40, WIDTH / 2, HEIGHT / 2 + 100)
    all_buttons = (button1, button2, button3)

    added_money = int(((scor // 500) ** (4 / 3)) // 2)
    player.money += added_money

    money_file = open(os.path.join(DATA_DIR, 'money.txt'), 'w')
    money_file.write(str(player.money))
    money_file.close()

    waiting = True
    cnt = 0
    while waiting:
        clock.tick(FPS)

        display.blit(background, background_rect)
        draw_text(display, "Game Over", 64, WIDTH / 2, HEIGHT / 10)
        draw_text(display, "You got {} money!".format(added_money), 30, WIDTH / 2, HEIGHT / 10 + 80)
        draw_text(display, "Your score >> " + str(scor), 28, WIDTH / 2, HEIGHT - 50)

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
                        screen = pygame.display.set_mode((WIDTH * 1.2, HEIGHT * 1.2))
                        waiting = False
                    if cnt == 1:
                        menu(player)
                        display.blit(background, background_rect)
                        pygame.display.flip()
                        waiting = False
                    if cnt == 2:
                        pygame.quit()
                        exit()

        all_buttons[cnt].active = True
        for but in all_buttons:
            but.update()
            but.surf.blit(but.text_surface, but.rect)

        screen.blit(pygame.transform.scale(display, (WIDTH, HEIGHT)), (0, 0))
        pygame.display.flip()
        # print(button1.active, button2.active, button3.active)


# Добавление основных групп
powerups = pygame.sprite.Group()

# Процесс игры

game = Game(music_manager)
spawn_manager = SpawnManager(game)
game_over = True
running = True
while running:
    if game_over:
        music_manager.music_init()

        for snd in music_manager.all_sounds:
            snd.set_volume(sound_state / 3)
        pygame.mixer.music.set_volume(music_state / 3)

        player = Player(game.all_sprites, game.bullets, music_manager)
        shop = Shop(display, player, clock)
        if not game.first_game:
            game_over_screen(score)
        else:
            menu(shop.show_shop)

        screen = pygame.display.set_mode((WIDTH * 1.2, HEIGHT * 1.2))
        game.all_sprites.add(player)
        game_over = False
        player.rect.centerx = WIDTH / 2
        player.rect.bottom = HEIGHT - 10

        game.first_game = False

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

    if score >= 700 and not spawn_manager.boss_here:
        #spawn_manager.stop = True
        spawn_manager.boss_here = True
        spawn_manager.spawn_boss(game)

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

    # Проверка коллайда "БОСС - пуля"
    hits = pygame.sprite.groupcollide(game.boss, game.bullets, False, True, pygame.sprite.collide_circle)
    # logger.debug(hits)
    if hits:
        for hit in list(hits.values())[0]:
            hit_obj = [x for x in hits.keys()][0]

            hit_obj.lives -= 1
            if hit_obj.lives > 0:
                random.choice(music_manager.expl_sounds).play()
                expl_center = (hit.rect.center[0], hit.rect.center[1])
                expl = Explosion(expl_center, 'sm')
                game.all_sprites.add(expl)
            else:
                hit.kill()
                score += 5000 + hit.radius  # Очки считаются от радиуса
                random.choice(music_manager.expl_sounds).play()
                expl = Explosion(hit.rect.center, 'lg')
                game.all_sprites.add(expl)
                if random.random() > 0.9 + player.power / 170 - 0.01:
                    pov = Pow(hit.rect.center)
                    game.all_sprites.add(pov)
                    powerups.add(pov)
                spawn_manager.newmob(game)
            hit.kill()

        # Проверка коллайда "БОСС - пуля"
        hits = pygame.sprite.groupcollide(game.boss, game.bullets, False, True, pygame.sprite.collide_circle)
        # logger.debug(hits)
        if hits:
            for hit in list(hits.values())[0]:
                hit_obj = [x for x in hits.keys()][0]

                hit_obj.lives -= 1
                if hit_obj.lives > 0:
                    random.choice(music_manager.expl_sounds).play()
                    expl_center = (hit.rect.center[0], hit.rect.center[1])
                    expl = Explosion(expl_center, 'sm')
                    game.all_sprites.add(expl)
                else:
                    hit.kill()
                    score += 5000 + hit.radius  # Очки считаются от радиуса
                    random.choice(music_manager.expl_sounds).play()
                    expl = Explosion(hit.rect.center, 'lg')
                    game.all_sprites.add(expl)
                    if random.random() > 0.9 + player.power / 170 - 0.01:
                        pov = Pow(hit.rect.center)
                        game.all_sprites.add(pov)
                        powerups.add(pov)
                    spawn_manager.newmob(game)
                hit.kill()

    # Проверка коллайда "БОСС - метеорит"
    hits = pygame.sprite.groupcollide(game.boss, game.mobs, False, True, pygame.sprite.collide_circle)
    # logger.debug(hits)
    if hits:
        for hit in list(hits.values())[0]:
            hit_obj = [x for x in hits.keys()][0]

            hit_obj.lives -= 1
            if hit_obj.lives > 0:
                random.choice(music_manager.expl_sounds).play()
                expl_center = (hit.rect.center[0], hit.rect.center[1])
                expl = Explosion(expl_center, 'sm')
                game.all_sprites.add(expl)
            else:
                hit.kill()
                random.choice(music_manager.expl_sounds).play()
                expl = Explosion(hit.rect.center, 'lg')
                game.all_sprites.add(expl)
            hit.kill()

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

        # Вжух от босса
    hits = pygame.sprite.spritecollide(player, game.boss_bullets, True)
    for hit in hits:
        player.shield -= 10000
        expl = Explosion(hit.rect.center, 'sm')
        game.all_sprites.add(expl)
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
    display.fill(BLACK)
    display.blit(background, background_rect)
    game.all_sprites.draw(display)
    draw_text(display, str(score), 22, WIDTH / 2, 10)
    draw_text(display, 'Power Lvl ' + str(pow_lev), 23, WIDTH - 60, 30)
    draw_shield_bar(display, 5, 5, player.shield, player)
    draw_energy_bar(display, WIDTH - 110, 5, (now - player.power_time) // 100, player.power)
    draw_lives(display, 12, 25, player.lives, heart_mini_img)
    screen.blit(pygame.transform.scale(display, (WIDTH * 1.2, HEIGHT * 1.2)), (0, 0))
    pygame.display.flip()

pygame.quit()
