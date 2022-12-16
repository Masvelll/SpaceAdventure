import os
import sys
import pygame

#  Game setup
WIDTH = 480
HEIGHT = 600
FPS = 60

#  Colors
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

#  Fonts
font_name = pygame.font.match_font('droidsans')

#  Directories
config_name = 'myapp.cfg'
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)
config_path = os.path.join(application_path, config_name)

IMG_DIR = os.path.join(application_path, 'img')
DATA_DIR = os.path.join(application_path, 'data')
SOUND_DIR = os.path.join(application_path, 'snd')

#  Importing files
with open(os.path.join(DATA_DIR, 'sound.txt')) as sound_file:
    all_sound_state = sound_file.readlines()
    sound_state = int(all_sound_state[0].split()[1])
    music_state = int(all_sound_state[1].split()[1])

with open(os.path.join(DATA_DIR, 'highscore.txt')) as highscore_file:
    highscore = int(highscore_file.read())
