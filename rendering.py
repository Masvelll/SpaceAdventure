import pygame
from settings import RED, GREEN, WHITE, YELLOW

font_name = pygame.font.match_font('droidsans')


def draw_text(surf, text, size, x, y):
    """Прорисовывает текст"""
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def draw_shield_bar(surf, x, y, pct, player):
    """Прорисовывает полосу здоровья"""
    if pct < 0:
        pct = 0
    bar_length = 100 * (1 + player.Shield_lvl / 3)
    bar_height = 10
    fill = (pct / (100 * (1 + player.Shield_lvl / 3))) * bar_length
    fill2 = bar_length - fill
    outline_rect = pygame.Rect(x, y, bar_length, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    fill2_rect = pygame.Rect(x + fill, y, fill2, bar_height)
    pygame.draw.rect(surf, RED, fill2_rect)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


def draw_energy_bar(surf, x, y, pct, power):
    """Прорисовывает полосу энергии"""
    if power == 1:
        pct = 100
    if pct < 0:
        pct = 0
    bar_length = 100
    bar_height = 10
    fill = (1 - pct / 100) * bar_length
    outline_rect = pygame.Rect(x, y, bar_length, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(surf, YELLOW, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


def draw_lives(surf, x, y, lives, img):
    """Прорисовывает сердца здоровья"""
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)
