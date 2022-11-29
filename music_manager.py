import pygame
import os
from settings import SOUND_DIR


class MusicManager:
    """Класс, объект которого может изменять музыку и создавать звуки"""

    def __init__(self):
        self.all_sounds = set()
        self.shoot_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, 'pew.wav'))
        self.expl_sounds = []
        for snd in ['expl3.wav', 'expl6.wav']:
            self.sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, snd))
            self.expl_sounds.append(self.sound)
            self.all_sounds.add(self.sound)
        pygame.mixer.music.load(os.path.join(SOUND_DIR, 'Wonderful.mp3'))
        pygame.mixer.music.set_volume(1)
        self.shield_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, 'pow4.wav'))
        self.power_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, 'pow5.wav'))
        self.fart_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, 'fart.wav'))

        self.all_sounds.add(self.shoot_sound)
        self.all_sounds.add(self.shield_sound)
        self.all_sounds.add(self.power_sound)
        self.all_sounds.add(self.fart_sound)

    def music_init(self):
        """Инициализирует музыку"""
        pygame.mixer.music.load(os.path.join(SOUND_DIR, 'Wonderful.mp3'))
        pygame.mixer.music.set_volume(1)
        pygame.mixer.music.play(loops=-1)

    def change_music(self):
        """Меняет музыку"""
        pygame.mixer.music.load(os.path.join(SOUND_DIR, 'unstoppable_driver.wav'))
        pygame.mixer.music.set_volume(1)
        pygame.mixer.music.play(loops=-1)
