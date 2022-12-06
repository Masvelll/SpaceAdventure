import pygame
from music_manager import MusicManager
from mob import Mob
from enemy import Enemy


class SpawnManager:
    def __init__(self, game):
        self.game = game
        self.music_changer = MusicManager()
        self.stop = False

    def newmob(self, game):
        """Создаёт метеорит"""
        m = Mob(self.stop)
        game.all_sprites.add(m)
        game.mobs.add(m)

    def spawn_enemy(self, game):
        """Создаёт врага"""
        m = Enemy(game.all_sprites, game.enemy_bullets)
        game.all_sprites.add(m)
        game.enemies.add(m)
