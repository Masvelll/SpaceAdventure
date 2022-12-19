import pygame
from settings import music_state, sound_state, highscore
from player import Player


class Game:
    """Класс, объект которого содержит все основные параметры игры"""

    def __init__(self, music_manager):
        self.wait = False

        self.stage = 0
        self.limit = 5000
        self.relax = 0
        self.score = 0
        self.last_spawn = pygame.time.get_ticks()
        self.spawn_rate = 15000

        self.music_state = music_state
        self.sound_state = sound_state
        self.highscore = highscore
        self.game_over = True
        self.first_game = True
        self.music_manager = music_manager

        self.all_sprites = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.boss_bullets = pygame.sprite.Group()
        self.boss = pygame.sprite.Group()
    def entity_reset(self, music_manager):
        highscore = self.highscore
        score = self.score
        first_game = self.first_game

        self.__init__(music_manager)
        self.first_game = first_game
        self.score = score
        self.highscore = highscore

    def next_level(self, music_manager, spawn_manager):
        """Переходит в усложнённый режим игры"""
        if not self.wait:
            self.relax = pygame.time.get_ticks()
            self.wait = True
            spawn_manager.stop = True
            music_manager.change_music()

        now = pygame.time.get_ticks()
        if now - self.relax >= 9000:
            self.wait = False
            spawn_manager.stop = False

            self.stage = 1
            self.limit = 999999

            for i in range(20):
                spawn_manager.newmob(self)
