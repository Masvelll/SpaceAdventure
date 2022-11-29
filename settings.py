import os
import sys

#  Game setup
W = 480
H = 600
FPS = 60

#  Directories
config_name = 'myapp.cfg'
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)
config_path = os.path.join(application_path, config_name)

img_dir = os.path.join(application_path, 'img')
data_dir = os.path.join(application_path, 'data')


#  UI
