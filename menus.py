import pygame
from buttons import Button, button_reset, button_update, button_check
from settings import WIDTH, HEIGHT, FPS, DATA_DIR, WHITE
from images import background, background_rect
from rendering import draw_text
import os


class MainMenu:
    def __init__(self, display, clock):
        self.waiting = True
        self.display = display
        self.clock = clock

    def show_menu(self, show_shop, show_settings, highscore):
        def stop_waiting():
            nonlocal waiting
            waiting = False

        display = self.display
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        button_play = Button(display, "Play", 40, WIDTH / 2, HEIGHT * 4 / 7 - 160, stop_waiting)
        button_shop = Button(display, "Shop", 40, WIDTH / 2, HEIGHT * 4 / 7 - 80, show_shop)
        button_settings = Button(display, "Settings", 40, WIDTH / 2, HEIGHT * 4 / 7, show_settings)
        button_exit = Button(display, "Exit", 40, WIDTH / 2, HEIGHT * 4 / 7 + 80, pygame.quit)
        all_buttons = (button_play, button_shop, button_settings, button_exit)
        button_amount = len(all_buttons)

        waiting = True
        current_button = 0
        while waiting:
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


class Shop:
    def __init__(self, display, player, clock):
        self.display = display
        self.player = player
        self.clock = clock

        self.display = pygame.Surface((WIDTH, HEIGHT))
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

        self.stats = {
            "Shield": ["Shield lvl ", player.Shield_lvl],
            "Atkspeed": ["Atk Speed lvl ", player.Atkspeed_lvl],
            "Power": ["Power lvl ", player.Power_lvl]
        }

    def increase_stat(self, stat_type, button):
        """Увеличивает уровень определённой характеристики игрока"""
        cost = 50 * self.stats[stat_type][1]
        print(self.stats[stat_type][0], self.stats[stat_type][1])
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
        print("written", self.stats)
        print(self.player.Power_lvl, self.player.Shield_lvl, self.player.Atkspeed_lvl)
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

    def lvl_text(self, stat_lvl):
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

        button_power, button_shield, button_atkspeed, button_back = self.create_buttons()
        all_buttons = (button_power, button_shield, button_atkspeed, button_back)

        waiting = True
        current_button = 0
        while waiting:
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
                            waiting = False

                        self.money_write()

            self.show_description(current_button)
            all_buttons[current_button].active = True
            for but in all_buttons:
                but.update()
                but.rect.left = 20
                but.surf.blit(but.text_surface, but.rect)

            self.screen.blit(pygame.transform.scale(self.display, (WIDTH, HEIGHT)), (0, 0))
            pygame.display.flip()
