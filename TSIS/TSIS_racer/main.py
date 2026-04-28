import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame

from persistence import CAR_COLORS, DIFFICULTIES, add_leaderboard_entry, clean_name, load_leaderboard, load_settings, save_settings
from racer import SCREEN_HEIGHT, SCREEN_WIDTH, RacerGame, SoundBank
from ui import BG, Button, TextInput, draw_text, draw_title


class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Racer")
        self.clock = pygame.time.Clock()
        self.fonts = {
            "small": pygame.font.SysFont(None, 24),
            "medium": pygame.font.SysFont(None, 32),
            "large": pygame.font.SysFont(None, 52),
        }
        self.settings = load_settings()
        self.board = load_leaderboard()
        self.sounds = SoundBank(self.settings["sound"])
        self.name_input = TextInput((120, 140, 160, 40), self.settings["username"])
        self.state = "menu"
        self.game = None
        self.running = True

    def save_pref(self):
        self.settings = save_settings(self.settings)
        self.sounds.set_enabled(self.settings["sound"])

    def start_game(self):
        self.settings["username"] = clean_name(self.name_input.text or self.settings["username"])
        self.name_input.text = self.settings["username"]
        self.save_pref()
        self.game = RacerGame(self.settings, self.settings["username"], self.sounds)
        self.state = "game"

    def save_result(self):
        if self.game and not self.game.saved:
            self.board = add_leaderboard_entry(self.game.summary())
            self.game.saved = True

    def menu_buttons(self):
        return {
            "play": Button((110, 330, 180, 40), "Play"),
            "leaderboard": Button((110, 380, 180, 40), "Leaderboard"),
            "settings": Button((110, 430, 180, 40), "Settings"),
            "quit": Button((110, 480, 180, 40), "Quit", (200, 80, 80)),
        }

    def settings_buttons(self):
        return {
            "sound": Button((260, 170, 90, 36), "Toggle"),
            "color_l": Button((210, 255, 36, 36), "<", (230, 190, 70)),
            "color_r": Button((314, 255, 36, 36), ">", (230, 190, 70)),
            "diff_l": Button((210, 340, 36, 36), "<", (230, 190, 70)),
            "diff_r": Button((314, 340, 36, 36), ">", (230, 190, 70)),
            "back": Button((110, 500, 180, 40), "Back", (200, 80, 80)),
        }

    def over_buttons(self):
        return {
            "retry": Button((110, 470, 180, 40), "Retry", (80, 180, 110)),
            "menu": Button((110, 520, 180, 40), "Main Menu", (200, 80, 80)),
        }

    def loop(self):
        while self.running:
            dt = self.clock.tick(60) / 1000
            self.events()
            self.update(dt)
            self.draw()
            pygame.display.flip()
        pygame.quit()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif self.state == "menu":
                self.name_input.handle(event)
                for name, button in self.menu_buttons().items():
                    if button.clicked(event):
                        if name == "play":
                            self.start_game()
                        elif name == "leaderboard":
                            self.board = load_leaderboard()
                            self.state = "leaderboard"
                        elif name == "settings":
                            self.state = "settings"
                        else:
                            self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.start_game()
            elif self.state == "settings":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = "menu"
                order = list(CAR_COLORS)
                diff = DIFFICULTIES
                for name, button in self.settings_buttons().items():
                    if button.clicked(event):
                        if name == "sound":
                            self.settings["sound"] = not self.settings["sound"]
                        elif name == "color_l":
                            i = (order.index(self.settings["car_color"]) - 1) % len(order)
                            self.settings["car_color"] = order[i]
                        elif name == "color_r":
                            i = (order.index(self.settings["car_color"]) + 1) % len(order)
                            self.settings["car_color"] = order[i]
                        elif name == "diff_l":
                            i = (diff.index(self.settings["difficulty"]) - 1) % len(diff)
                            self.settings["difficulty"] = diff[i]
                        elif name == "diff_r":
                            i = (diff.index(self.settings["difficulty"]) + 1) % len(diff)
                            self.settings["difficulty"] = diff[i]
                        else:
                            self.state = "menu"
                        self.save_pref()
            elif self.state == "leaderboard":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = "menu"
                if Button((110, 540, 180, 40), "Back", (200, 80, 80)).clicked(event):
                    self.state = "menu"
            elif self.state == "game":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = "menu"
                elif self.game:
                    self.game.handle_key(event)
            elif self.state == "game_over":
                for name, button in self.over_buttons().items():
                    if button.clicked(event):
                        self.state = "menu" if name == "menu" else "game"
                        if name == "retry":
                            self.start_game()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = "menu"

    def update(self, dt):
        if self.state == "game" and self.game:
            if self.game.update(dt) != "running":
                self.save_result()
                self.state = "game_over"

    def draw(self):
        if self.state == "game" and self.game:
            self.game.draw(self.screen, self.fonts)
            return

        self.screen.fill(BG)
        if self.state == "menu":
            draw_title(self.screen, self.fonts["large"], "Racer", 70)
            draw_text(self.screen, self.fonts["small"], "Username", (120, 112))
            self.name_input.draw(self.screen, self.fonts["medium"], "Username")
            color = tuple(CAR_COLORS[self.settings["car_color"]])
            pygame.draw.rect(self.screen, color, (178, 210, 44, 68))
            pygame.draw.rect(self.screen, (240, 240, 240), (186, 220, 28, 12))
            draw_text(self.screen, self.fonts["small"], f"Color: {self.settings['car_color']}", (140, 290))
            draw_text(self.screen, self.fonts["small"], f"Difficulty: {self.settings['difficulty']}", (130, 310))
            for button in self.menu_buttons().values():
                button.draw(self.screen, self.fonts["medium"])
        elif self.state == "settings":
            draw_title(self.screen, self.fonts["large"], "Settings", 70)
            draw_text(self.screen, self.fonts["medium"], f"Sound: {'On' if self.settings['sound'] else 'Off'}", (50, 176))
            draw_text(self.screen, self.fonts["medium"], f"Car color: {self.settings['car_color']}", (50, 260))
            draw_text(self.screen, self.fonts["medium"], f"Difficulty: {self.settings['difficulty']}", (50, 345))
            pygame.draw.rect(self.screen, tuple(CAR_COLORS[self.settings["car_color"]]), (260, 250, 40, 60))
            for button in self.settings_buttons().values():
                button.draw(self.screen, self.fonts["medium"])
        elif self.state == "leaderboard":
            draw_title(self.screen, self.fonts["large"], "Leaderboard", 70)
            draw_text(self.screen, self.fonts["small"], "Rank   Name        Score   Distance", (45, 120))
            y = 160
            for i, row in enumerate(self.board[:10], start=1):
                line = f"{i:>2}.   {row['name']:<10}  {row['score']:<6}  {row['distance']}m"
                draw_text(self.screen, self.fonts["small"], line, (45, y))
                y += 32
            Button((110, 540, 180, 40), "Back", (200, 80, 80)).draw(self.screen, self.fonts["medium"])
        elif self.state == "game_over":
            title = "Finished" if self.game and self.game.status == "finished" else "Game Over"
            draw_title(self.screen, self.fonts["large"], title, 80)
            if self.game:
                result = self.game.summary()
                draw_text(self.screen, self.fonts["medium"], f"Player: {result['name']}", (90, 170))
                draw_text(self.screen, self.fonts["medium"], f"Score: {result['score']}", (90, 220))
                draw_text(self.screen, self.fonts["medium"], f"Distance: {result['distance']}m", (90, 270))
                draw_text(self.screen, self.fonts["medium"], f"Coins: {result['coins']}", (90, 320))
            for button in self.over_buttons().values():
                button.draw(self.screen, self.fonts["medium"])


if __name__ == "__main__":
    App().loop()