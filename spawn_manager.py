import pygame
from music_manager import MusicManager
from mob import Mob


class SpawnManager:
    def __init__(self, game):
        self.game = game
        self.music_changer = MusicManager()

    def newmob(self, game):
        """Создаёт метеорит"""
        m = Mob()
        game.all_sprites.add(m)
        game.mobs.add(m)

    def spawn_enemy(self):
        """Создаёт врага"""
        pass
