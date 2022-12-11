import pygame
from music_manager import MusicManager
from mob import Mob
from enemy import Enemy, Boss


class SpawnManager:
    def __init__(self, game):
        self.game = game
        self.music_changer = MusicManager()
        self.stop = False
        self.boss_here = False

    def newmob(self, game):
        """Создаёт метеорит"""
        if not self.stop:
            m = Mob(self.stop)
            game.all_sprites.add(m)
            game.mobs.add(m)

    def spawn_enemy(self, game):
        """Создаёт врага"""
        m = Enemy(game.all_sprites, game.enemy_bullets)
        game.all_sprites.add(m)
        game.enemies.add(m)

    def spawn_boss(self, game):
        m = Boss(game.all_sprites, game.boss_bullets)
        game.all_sprites.add(m)

