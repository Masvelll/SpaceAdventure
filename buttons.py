import pygame
from settings import font_name, WHITE


class Button:
    def __init__(self, surf, text, size, x, y, callback):
        """

        :param surf: поверхность, на которую рисуется кнопка
        :param text: текст кнопки
        :param size: размер шрифта текста
        :param x: координата центра по х
        :param y: координата центра по у
        :param callback: функция, которую вызывает кнопка при нажатии
        """

        self.active = False
        self.x = x
        self.y = y
        self.size = size
        self.text = text
        self.surf = surf

        self.font = pygame.font.Font(font_name, self.size)
        self.text_surface = self.font.render(text, True, WHITE)
        self.rect = self.text_surface.get_rect()
        self.callback = callback

    def clicked(self):
        """Вызывает указанную в конструкторе функцию"""
        self.callback()

    def update(self):
        """Обновляет кнопку (подрисовывает > <, если она нажата)"""
        if self.active:
            text = '> ' + self.text + ' <'
        else:
            text = self.text

        self.text_surface = self.font.render(text, True, WHITE)
        self.rect = self.text_surface.get_rect()
        self.rect.midtop = (self.x, self.y)


def button_reset(all_buttons, current_button):
    """Возвращает кнопку в прежнее состояние,
    если происходит переключение на следующую кнопку
    """

    for i in range(len(all_buttons)):
        if i != current_button:
            all_buttons[i].active = False


def button_check(current_button, button_amount, all_buttons):
    """Проверяет нажатые с клавиатуры кнопки,
    переключает кнопку на следующую или выполняет функцию кнопки
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                current_button = (current_button + 1) % button_amount
            if event.key == pygame.K_UP:
                current_button = (current_button - 1) % button_amount

            if event.key == pygame.K_RETURN:
                all_buttons[current_button].clicked()

    return current_button


def button_update(all_buttons):
    for but in all_buttons:
        but.update()
        but.surf.blit(but.text_surface, but.rect)
