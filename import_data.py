from settings import DATA_DIR
import os

try:
    money_file = open(os.path.join(DATA_DIR, 'money.txt'))
except FileNotFoundError:
    money_file = open(os.path.join(DATA_DIR, 'money.txt'), "w")
    money_file.write("0")
    money_file = open(os.path.join(DATA_DIR, 'money.txt'))

money = int(money_file.read())
money_file.close()

try:
    stats_file = open(os.path.join(DATA_DIR, 'stats.txt'))
except FileNotFoundError:
    stats_file = open(os.path.join(DATA_DIR, 'stats.txt'), "w")
    stats_file.write("Power_lvl 1 \nShield_lvl 1 \nAtk_speed_lvl 1")
    stats_file = open(os.path.join(DATA_DIR, 'stats.txt'))

try:
    with open(os.path.join(DATA_DIR, 'sound.txt')) as sound_file:
        all_sound_state = sound_file.readlines()
        sound_state = int(all_sound_state[0].split()[1])
        music_state = int(all_sound_state[1].split()[1])
except FileNotFoundError:
    with open(os.path.join(DATA_DIR, 'sound.txt'), "w") as sound_file:
        sound_file.write("Sound_state 1 \nMusic_state 1")
        sound_state = 1
        music_state = 1

try:
    with open(os.path.join(DATA_DIR, 'highscore.txt')) as highscore_file:
        highscore = int(highscore_file.read())
except FileNotFoundError:
    with open(os.path.join(DATA_DIR, 'highscore.txt'), "w") as highscore_file:
        highscore_file.write("0")
        highscore = 0

stats = stats_file.readlines()
stats_file.close()
