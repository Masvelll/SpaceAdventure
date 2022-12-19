import pygame
import random
import os
from player import Player
from rendering import draw_text, draw_shield_bar, draw_energy_bar, draw_lives
from game import Game
from settings import sound_state, music_state, WIDTH, HEIGHT, FPS, BLACK, DATA_DIR
from images import explosion_anim, background_rect, background, powerup_images, heart_mini_img
from music_manager import MusicManager
from spawn_manager import SpawnManager
from menus import Shop, MainMenu, Pause, GameOverScreen, Settings

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


# Функция для вывода текста (можно не париться, создавая отдельные label)
font_name = pygame.font.match_font('droidsans')
music_manager = MusicManager()

# Добавление основных групп
powerups = pygame.sprite.Group()

# Процесс игры

game = Game(music_manager)
spawn_manager = SpawnManager(game)
running = True
while running:
    if game.game_over:
        game.entity_reset(music_manager)
        music_manager.music_init()

        for snd in music_manager.all_sounds:
            snd.set_volume(sound_state / 3)
        pygame.mixer.music.set_volume(music_state / 3)

        player = Player(game.all_sprites, game.bullets, music_manager)
        main_menu = MainMenu(display, clock)
        shop = Shop(display, clock, player)
        pause = Pause(display, clock, game)
        settings = Settings(display, clock, game, music_manager)
        game_over_screen = GameOverScreen(display, clock, player, main_menu.show_menu, settings.show_settings,
                                          shop.show_shop, game)
        if not game.first_game:
            game_over_screen.show_game_over_screen()
        else:
            main_menu.show_menu(shop.show_shop, settings.show_settings, game.highscore)

        screen = pygame.display.set_mode((WIDTH * 1.2, HEIGHT * 1.2))
        game.all_sprites.add(player)
        game.game_over = False
        game.first_game = False
        spawn_manager.boss_here = False

        for i in range(8):
            spawn_manager.newmob(game)

        game.score = 0
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pause.show_pause(settings.show_settings, game_over_screen.show_game_over_screen)

        if event.type == pygame.KEYUP:
            pass

    game.all_sprites.update()

    if game.score >= game.limit and game.stage == 0:
        game.next_level(music_manager, spawn_manager)

    now = pygame.time.get_ticks()
    if now - game.last_spawn > game.spawn_rate and game.stage == 1:
        game.last_spawn = now
        game.spawn_rate *= 0.9
        spawn_manager.spawn_enemy(game)

    if game.score >= 7000 and not spawn_manager.boss_here:
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

        if game.score > game.highscore:
            game.highscore = game.score
            highscore_file = open(os.path.join(DATA_DIR, 'highscore.txt'), 'w')
            highscore_file.write(str(game.score))
            highscore_file.close()

        game.game_over = True

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
            game.score += 50 + hit.radius  # Очки считаются от радиуса
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
                game.score += 5000 + hit.radius  # Очки считаются от радиуса
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
                    game.score += 5000 + hit.radius  # Очки считаются от радиуса
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
            game.score += 500
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
    draw_text(display, str(game.score), 22, WIDTH / 2, 10)
    draw_text(display, 'Power Lvl ' + str(pow_lev), 23, WIDTH - 60, 30)
    draw_shield_bar(display, 5, 5, player.shield, player)
    draw_energy_bar(display, WIDTH - 110, 5, (now - player.power_time) // 100, player.power)
    draw_lives(display, 12, 25, player.lives, heart_mini_img)
    screen.blit(pygame.transform.scale(display, (WIDTH * 1.2, HEIGHT * 1.2)), (0, 0))
    pygame.display.flip()

pygame.quit()
