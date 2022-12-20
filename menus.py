import pygame
from buttons import Button, button_reset, button_update, button_check
from settings import WIDTH, HEIGHT, FPS, DATA_DIR, WHITE
from images import background, background_rect
from rendering import draw_text
from objects import Mixer
import os


class Menu:
    """Абстрактный класс для окон меню"""

    def __init__(self, display, clock):
        self.waiting = True
        self.display = display
        self.clock = clock
        self.waiting = True

    def stop_waiting(self):
        """Заканчивает процесс показа окна соответствующего меню"""
        self.waiting = False

    @staticmethod
    def menu_exit():
        """Выходит из игры"""
        pygame.quit()
        exit()


class MainMenu(Menu):
    def __init__(self, display, clock):
        super().__init__(display, clock)

    def show_menu(self, show_shop, show_settings, highscore):
        display = self.display
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        button_play = Button(display, "Play", 40, WIDTH / 2, HEIGHT * 4 / 7 - 160, super().stop_waiting)
        button_shop = Button(display, "Shop", 40, WIDTH / 2, HEIGHT * 4 / 7 - 80, show_shop)
        button_settings = Button(display, "Settings", 40, WIDTH / 2, HEIGHT * 4 / 7, show_settings)
        button_exit = Button(display, "Exit", 40, WIDTH / 2, HEIGHT * 4 / 7 + 80, self.menu_exit)
        all_buttons = (button_play, button_shop, button_settings, button_exit)
        button_amount = len(all_buttons)

        self.waiting = True
        current_button = 0
        while self.waiting:
            self.clock.tick(FPS)

            display.blit(background, background_rect)
            draw_text(display, "Space Adventure", 64, WIDTH / 2, HEIGHT / 10)
            draw_text(display, "Your highscore >> " + str(highscore), 28, WIDTH / 2, HEIGHT - 50)

            button_reset(all_buttons, current_button)
            current_button = button_check(current_button, button_amount, all_buttons)

            all_buttons[current_button].active = True
            button_update(all_buttons)

            screen.blit(pygame.transform.scale(display, (WIDTH, HEIGHT)), (0, 0))
            pygame.display.flip()


class Settings(Menu):
    def __init__(self, display, clock, game, music_manager):
        super().__init__(display, clock)
        self.game = game
        self.music_manager = music_manager
        self.sound_state = self.game.sound_state
        self.music_state = self.game.music_state

    def sound_increase(self, current_button):
        """Увеичвает громкость звука или музыки"""
        if current_button == 0:
            self.sound_state += 1
            if self.sound_state > 3:
                self.sound_state = 3
        if current_button == 1:
            self.music_state += 1
            if self.music_state > 3:
                self.music_state = 3

    def sound_decrease(self, current_button):
        """Уменьшает громкость звука или музыка"""
        if current_button == 0:
            self.sound_state -= 1
            if self.sound_state > 3:
                self.sound_state = 3
        if current_button == 1:
            self.music_state -= 1
            if self.music_state > 3:
                self.music_state = 3

    def write_sound(self):
        """Загружает данные в файл"""
        sound_file = open(os.path.join(DATA_DIR, 'sound.txt'), 'w')
        sound_file.write('Sound_state {}\n'.format(self.sound_state))
        sound_file.write('Music_state {}\n'.format(self.music_state))
        sound_file.close()

    def set_sound(self):
        """Ставит громкость игры так же, как у показателей"""
        self.game.sound_state = self.sound_state
        self.game.music_state = self.music_state

        for snd in self.music_manager.all_sounds:
            snd.set_volume(self.sound_state / 3)
        pygame.mixer.music.set_volume(self.music_state / 3)

    def show_settings(self):
        def skip():
            pass

        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        button_sound = Button(self.display, "Sound", 40, WIDTH / 2, HEIGHT / 2 - 100, skip)
        button_music = Button(self.display, "Music", 40, WIDTH / 2, HEIGHT / 2, skip)
        button_back = Button(self.display, "Back", 40, WIDTH / 2, HEIGHT / 2 + 100, skip)
        all_buttons = (button_sound, button_music, button_back)

        mixer_sound = Mixer(WIDTH / 2 + 100, HEIGHT / 2 - 95, self.sound_state)
        mixer_music = Mixer(WIDTH / 2 + 100, HEIGHT / 2 + 5, self.music_state)
        mixers = pygame.sprite.Group()
        mixers.add(mixer_sound)
        mixers.add(mixer_music)

        waiting = True
        current_button = 0
        while waiting:
            self.clock.tick(FPS)

            self.display.blit(background, background_rect)
            draw_text(self.display, "Settings", 64, WIDTH / 2, HEIGHT / 10)

            button_reset(all_buttons, current_button)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        current_button = (current_button + 1) % 3
                    if event.key == pygame.K_UP:
                        current_button = (current_button - 1) % 3

                    if event.key == pygame.K_RETURN:
                        if current_button == 2:
                            waiting = False
                    if event.key == pygame.K_RIGHT:
                        self.sound_increase(current_button)
                    if event.key == pygame.K_LEFT:
                        self.sound_decrease(current_button)

            all_buttons[current_button].active = True
            button_update(all_buttons)

            mixer_sound.state = self.sound_state
            mixer_music.state = self.music_state
            self.set_sound()

            mixers.update()
            mixers.draw(self.display)

            screen.blit(pygame.transform.scale(self.display, (WIDTH, HEIGHT)), (0, 0))
            pygame.display.flip()


class GameOverScreen(Menu):
    def __init__(self, display, clock, player, show_menu, show_settings, show_shop, game):
        super().__init__(display, clock)
        self.player = player

        self.show_menu = show_menu
        self.show_settings = show_settings
        self.show_shop = show_shop

        self.game = game

    def write_money(self):
        money_file = open(os.path.join(DATA_DIR, 'money.txt'), 'w')
        money_file.write(str(self.player.money))
        money_file.close()

    def show_game_over_screen(self):
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        button1 = Button(self.display, "Play again", 40, WIDTH / 2, HEIGHT / 2 - 50, self.stop_waiting)
        button2 = Button(self.display, "Back to menu", 40, WIDTH / 2, HEIGHT / 2 + 50, self.show_menu)
        button3 = Button(self.display, "Exit", 40, WIDTH / 2, HEIGHT / 2 + 150, self.menu_exit)
        all_buttons = (button1, button2, button3)

        added_money = int(((self.game.score // 500) ** (4 / 3)) // 2)
        self.player.money += added_money
        self.write_money()

        waiting = True
        cnt = 0
        while waiting:
            self.clock.tick(FPS)

            self.display.blit(background, background_rect)
            draw_text(self.display, "Game Over", 64, WIDTH / 2, HEIGHT / 10)
            draw_text(self.display, "You got {} money!".format(added_money), 30, WIDTH / 2, HEIGHT / 10 + 120)
            draw_text(self.display, "Your score >> " + str(self.game.score), 28, WIDTH / 2, HEIGHT - 50)

            for i in range(len(all_buttons)):
                if i != cnt:
                    all_buttons[i].active = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        cnt = (cnt + 1) % 3
                    if event.key == pygame.K_UP:
                        cnt = (cnt - 1) % 3

                    if event.key == pygame.K_RETURN:
                        if cnt == 0:
                            screen = pygame.display.set_mode((WIDTH * 1.2, HEIGHT * 1.2))
                            waiting = False
                        if cnt == 1:
                            self.show_menu(self.show_shop, self.show_settings, self.game.highscore)
                            self.display.blit(background, background_rect)
                            pygame.display.flip()
                            waiting = False
                        if cnt == 2:
                            pygame.quit()
                            exit()

            all_buttons[cnt].active = True
            button_update(all_buttons)

            screen.blit(pygame.transform.scale(self.display, (WIDTH, HEIGHT)), (0, 0))
            pygame.display.flip()


class Pause(Menu):
    def __init__(self, display, clock, game):
        super().__init__(display, clock)
        self.game = game
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

    def stop_waiting(self):
        self.screen = pygame.display.set_mode((WIDTH * 1.2, HEIGHT * 1.2))
        self.waiting = False

    def give_up(self):
        self.game.game_over = True
        self.waiting = False

    def show_pause(self, show_settings):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.flip()

        button1 = Button(self.display, "Continue", 40, WIDTH / 2, HEIGHT / 2.5 - 100, self.stop_waiting)
        button2 = Button(self.display, "Settings", 40, WIDTH / 2, HEIGHT / 2.5, show_settings)
        button3 = Button(self.display, "Give up", 40, WIDTH / 2, HEIGHT / 2.5 + 100, self.give_up)
        button4 = Button(self.display, "Exit", 40, WIDTH / 2, HEIGHT / 2.5 + 200, super().menu_exit)
        all_buttons = (button1, button2, button3, button4)
        button_amount = len(all_buttons)

        self.waiting = True
        current_button = 0
        while self.waiting:

            self.clock.tick(FPS)
            self.display.blit(background, background_rect)
            draw_text(self.display, "Pause", 82, WIDTH / 2, HEIGHT / 20)

            button_reset(all_buttons, current_button)

            current_button = button_check(current_button, button_amount, all_buttons)

            all_buttons[current_button].active = True
            for but in all_buttons:
                but.update()
                but.surf.blit(but.text_surface, but.rect)

            self.screen.blit(pygame.transform.scale(self.display, (WIDTH, HEIGHT)), (0, 0))
            pygame.display.flip()


class Shop(Menu):
    def __init__(self, display, clock, player):
        super().__init__(display, clock)
        self.player = player

        self.stats = {
            "Shield": ["Shield lvl ", player.Shield_lvl],
            "Atkspeed": ["Atk Speed lvl ", player.Atkspeed_lvl],
            "Power": ["Power lvl ", player.Power_lvl]
        }

    def increase_stat(self, stat_type, button):
        """Увеличивает уровень определённой характеристики игрока"""
        cost = 50 * self.stats[stat_type][1]
        if self.stats[stat_type][1] < 3 and self.player.money >= cost:
            self.stats[stat_type][1] += 1
            self.player.money -= cost
            if self.stats[stat_type][1] < 3:
                text = self.stats[stat_type][0] + str(self.stats[stat_type][1])
            else:
                text = self.stats[stat_type][0] + "MAX"
            button.text = text
        return self.stats[stat_type][1]

    def money_write(self):
        """Записывает значение количества денег в файл"""
        money_file = open(os.path.join(DATA_DIR, 'money.txt'), 'w')
        money_file.write(str(self.player.money))
        money_file.close()

        stats_file = open(os.path.join(DATA_DIR, 'stats.txt'), 'w')
        stats_file.write('Power_lvl {}\n'.format(self.stats["Power"][1]))
        stats_file.write('Shield_lvl {}\n'.format(self.stats["Shield"][1]))
        stats_file.write('Atk_speed_lvl {}\n'.format(self.stats["Atkspeed"][1]))
        stats_file.close()

    def show_description(self, current_button):
        """Показывает описание улучшений"""
        maximum = 3
        power_cost = 50 * self.player.Power_lvl
        shield_cost = 50 * self.player.Shield_lvl
        atkspeed_cost = 50 * self.player.Atkspeed_lvl

        if current_button == 0:
            draw_text(self.display, "Increases starting", 30, WIDTH / 2 + 100, HEIGHT / 2.3 - 50)
            draw_text(self.display, "power lvl", 30, WIDTH / 2 + 100, HEIGHT / 2.3 - 20)
            if self.player.Power_lvl == maximum:
                text = '--'
            else:
                text = str(power_cost)
            draw_text(self.display, "Upgrade cost >> " + text, 30, WIDTH / 2 + 100, HEIGHT / 2.3 + 15)
        if current_button == 1:
            draw_text(self.display, "Increases maximum", 30, WIDTH / 2 + 100, HEIGHT / 2.3 - 50)
            draw_text(self.display, "shield value", 30, WIDTH / 2 + 100, HEIGHT / 2.3 - 20)
            if self.player.Shield_lvl == maximum:
                text = '--'
            else:
                text = str(shield_cost)
            draw_text(self.display, "Upgrade cost >> " + text, 30, WIDTH / 2 + 100, HEIGHT / 2.3 + 15)
        if current_button == 2:
            draw_text(self.display, "Increases attack", 30, WIDTH / 2 + 100, HEIGHT / 2.3 - 50)
            draw_text(self.display, "speed of your ship", 30, WIDTH / 2 + 100, HEIGHT / 2.3 - 20)
            if self.player.Atkspeed_lvl == maximum:
                text = '--'
            else:
                text = str(atkspeed_cost)
            draw_text(self.display, "Upgrade cost >> " + text, 30, WIDTH / 2 + 100, HEIGHT / 2.3 + 15)
        if current_button == 3:
            draw_text(self.display, "Choose an upgrade", 30, WIDTH / 2 + 100, HEIGHT / 2.3 - 50)
            draw_text(self.display, "Upgrade cost >>  --", 30, WIDTH / 2 + 100, HEIGHT / 2.3 + 15)

    def create_buttons(self):
        def skip():
            pass

        button_power = Button(self.display, "Power lvl " + self.lvl_text(self.player.Power_lvl), 30, WIDTH / 2,
                              HEIGHT / 2.3 - 100,
                              skip())
        button_shield = Button(self.display, "Shield lvl " + self.lvl_text(self.player.Shield_lvl), 30, WIDTH / 2,
                               HEIGHT / 2.3, skip())
        button_atkspeed = Button(self.display, "Atk Speed lvl " + self.lvl_text(self.player.Atkspeed_lvl), 30,
                                 WIDTH / 2,
                                 HEIGHT / 2.3 + 100,
                                 skip())
        button_back = Button(self.display, "Back", 30, WIDTH / 2, HEIGHT / 2.3 + 200, skip())

        return button_power, button_shield, button_atkspeed, button_back

    @staticmethod
    def lvl_text(stat_lvl):
        """Возвращает текст, отображённый на кнопке по уровню переданной характеристики"""
        if stat_lvl == 3:
            return "MAX"
        return str(stat_lvl)

    def draw_main_window(self):
        """Прорисовывает основное окно магазина"""
        self.display.blit(background, background_rect)
        draw_text(self.display, "Shop", 64, WIDTH / 2, HEIGHT / 10)
        draw_text(self.display, "Your money >> " + str(self.player.money), 28, WIDTH / 2, HEIGHT - 50)
        draw_text(self.display, "Info:", 35, WIDTH / 2 + 100, HEIGHT / 2.3 - 110)
        outline_rect = pygame.Rect(WIDTH / 2 - 10, HEIGHT / 2 - 100, 220, 70)
        pygame.draw.rect(self.display, WHITE, outline_rect, 3)
        outline_rect = pygame.Rect(WIDTH / 2 - 10, HEIGHT / 2 - 30, 220, 30)
        pygame.draw.rect(self.display, WHITE, outline_rect, 3)

    def show_shop(self):

        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        button_power, button_shield, button_atkspeed, button_back = self.create_buttons()
        all_buttons = (button_power, button_shield, button_atkspeed, button_back)

        current_button = 0
        self.waiting = True
        while self.waiting:
            self.clock.tick(FPS)
            self.draw_main_window()

            power_cost = 50 * self.player.Power_lvl
            shield_cost = 50 * self.player.Shield_lvl
            atkspeed_cost = 50 * self.player.Atkspeed_lvl

            button_reset(all_buttons, current_button)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        current_button = (current_button + 1) % 4
                    if event.key == pygame.K_UP:
                        current_button = (current_button - 1) % 4

                    if event.key == pygame.K_RETURN:
                        if current_button == 0 and self.player.Power_lvl < 3 and self.player.money >= power_cost:
                            self.player.Power_lvl = self.increase_stat("Power", button_power)
                        if current_button == 1 and self.player.Shield_lvl < 3 and self.player.money >= shield_cost:
                            self.player.Shield_lvl = self.increase_stat("Shield", button_shield)
                        if current_button == 2 and self.player.Atkspeed_lvl < 3 and self.player.money >= atkspeed_cost:
                            self.player.Atkspeed_lvl = self.increase_stat("Atkspeed", button_atkspeed)
                        if current_button == 3:
                            self.waiting = False

                        self.money_write()
                        self.player.update_parameters()

            self.show_description(current_button)
            all_buttons[current_button].active = True
            for but in all_buttons:
                but.update()
                but.rect.left = 20
                but.surf.blit(but.text_surface, but.rect)

            screen.blit(pygame.transform.scale(self.display, (WIDTH, HEIGHT)), (0, 0))
            pygame.display.flip()
