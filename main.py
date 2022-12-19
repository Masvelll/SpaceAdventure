import pygame
import os
from player import Player
from rendering import draw_text, draw_shield_bar, draw_energy_bar, draw_lives
from game import Game
from settings import WIDTH, HEIGHT, FPS, BLACK, DATA_DIR
from import_data import sound_state, music_state
from images import background_rect, background, heart_mini_img
from music_manager import MusicManager
from spawn_manager import SpawnManager
from menus import Shop, MainMenu, Pause, GameOverScreen, Settings
from collision_manager import CollisionManager

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
pygame.display.set_caption("Space Adventure")
clock = pygame.time.Clock()


# Функция для вывода текста (можно не париться, создавая отдельные label)
font_name = pygame.font.match_font('droidsans')


# Процесс игры

music_manager = MusicManager()
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
        collision_manager = CollisionManager(player, game, spawn_manager, music_manager)
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

    collision_manager.process_all_collisions()

    # Проверка смерти игрока и анимации его смерти
    if not player.alive and not collision_manager.death_explosion.alive():

        if game.score > game.highscore:
            game.highscore = game.score
            highscore_file = open(os.path.join(DATA_DIR, 'highscore.txt'), 'w')
            highscore_file.write(str(game.score))
            highscore_file.close()

        game.game_over = True

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
