import pygame
from images import volume_mixer


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
