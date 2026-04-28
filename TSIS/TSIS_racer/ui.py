import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame


BG = (28, 28, 28)
PANEL = (45, 45, 45)
TEXT = (240, 240, 240)
MUTED = (180, 180, 180)
ACCENT = (70, 150, 235)


class Button:
    def __init__(self, rect, text, color=ACCENT):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color

    def draw(self, surface, font):
        mouse = pygame.mouse.get_pos()
        color = tuple(min(255, c + 20) for c in self.color) if self.rect.collidepoint(mouse) else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, TEXT, self.rect, 2)
        label = font.render(self.text, True, TEXT)
        surface.blit(label, label.get_rect(center=self.rect.center))

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


class TextInput:
    def __init__(self, rect, text=""):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.active = False

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
        elif self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key != pygame.K_RETURN and event.unicode.isprintable() and len(self.text) < 12:
                self.text += event.unicode

    def draw(self, surface, font, label):
        title = font.render(label, True, MUTED)
        surface.blit(title, (self.rect.x, self.rect.y - 28))
        pygame.draw.rect(surface, PANEL, self.rect)
        pygame.draw.rect(surface, ACCENT if self.active else MUTED, self.rect, 2)
        text = font.render(self.text, True, TEXT)
        surface.blit(text, (self.rect.x + 10, self.rect.y + 9))
        if self.active:
            x = self.rect.x + 12 + text.get_width()
            pygame.draw.line(surface, TEXT, (x, self.rect.y + 9), (x, self.rect.bottom - 9), 2)


def draw_title(surface, font, text, y):
    title = font.render(text, True, TEXT)
    surface.blit(title, title.get_rect(center=(surface.get_width() // 2, y)))


def draw_text(surface, font, text, pos, color=TEXT):
    surface.blit(font.render(text, True, color), pos)
