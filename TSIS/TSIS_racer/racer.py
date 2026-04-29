import os
import random

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame

from persistence import CAR_COLORS


SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
ROAD_X = 60
ROAD_W = 280
LANES = 4
LANE_W = ROAD_W // LANES
PLAYER_Y = SCREEN_HEIGHT - 90

PROFILES = {
    "Easy": {"speed": 220, "enemy_speed": 250, "finish": 2600, "enemy_gap": 1.15, "coin_gap": 0.95},
    "Normal": {"speed": 260, "enemy_speed": 300, "finish": 3400, "enemy_gap": 0.95, "coin_gap": 0.8},
    "Hard": {"speed": 300, "enemy_speed": 350, "finish": 4300, "enemy_gap": 0.8, "coin_gap": 0.7},
}

ENEMY_COLORS = [
    (220, 70, 70),
    (230, 140, 60),
    (180, 80, 220),
    (70, 180, 240),
]


class SoundBank:
    def __init__(self, enabled=True):
        self.enabled = bool(enabled)

    def set_enabled(self, enabled):
        self.enabled = bool(enabled)

    def play(self, _name):
        return


class RacerGame:
    def __init__(self, settings, username, sounds):
        self.settings = settings
        self.username = username
        self.sounds = sounds
        self.profile = PROFILES.get(settings["difficulty"], PROFILES["Normal"])
        self.player_color = tuple(CAR_COLORS.get(settings["car_color"], CAR_COLORS["Blue"]))
        self.finish_distance = self.profile["finish"]
        self.reset()

    def reset(self):
        self.player_lane = 1
        self.player = pygame.Rect(self.lane_x(self.player_lane), PLAYER_Y, 40, 64)
        self.distance = 0.0
        self.coin_total = 0
        self.status = "running"
        self.saved = False
        self.message = "Use LEFT and RIGHT"
        self.message_timer = 2.0
        self.traffic = []
        self.coins = []
        self.enemy_timer = 0.0
        self.coin_timer = 0.0

    def lane_x(self, lane, width=40):
        return ROAD_X + lane * LANE_W + (LANE_W - width) // 2

    def progress(self):
        return min(1.0, self.distance / self.finish_distance)

    def score(self):
        return int(self.distance) + self.coin_total * 50

    def summary(self):
        return {
            "name": self.username,
            "score": self.score(),
            "distance": int(self.distance),
            "coins": self.coin_total,
        }

    def handle_key(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_LEFT:
            self.player_lane = max(0, self.player_lane - 1)
        elif event.key == pygame.K_RIGHT:
            self.player_lane = min(LANES - 1, self.player_lane + 1)
        self.player.x = self.lane_x(self.player_lane)

    def choose_lane(self, items, avoid_player=False):
        lanes = list(range(LANES))
        random.shuffle(lanes)
        for lane in lanes:
            if avoid_player and lane == self.player_lane:
                continue
            blocked = False
            for item in items:
                if item["lane"] == lane and item["rect"].y < 130:
                    blocked = True
                    break
            if not blocked:
                return lane
        fallback = [lane for lane in range(LANES) if not (avoid_player and lane == self.player_lane)]
        return random.choice(fallback or list(range(LANES)))

    def spawn_enemy(self):
        lane = self.choose_lane(self.traffic, avoid_player=True)
        rect = pygame.Rect(self.lane_x(lane), -80, 40, 64)
        color = random.choice(ENEMY_COLORS)
        self.traffic.append({"lane": lane, "rect": rect, "color": color})

    def spawn_coin(self):
        lane = self.choose_lane(self.traffic + self.coins)
        size = 18
        rect = pygame.Rect(self.lane_x(lane, size), -size - 10, size, size)
        self.coins.append({"lane": lane, "rect": rect, "value": 1})

    def update(self, dt):
        if self.status != "running":
            return self.status

        if self.message_timer > 0:
            self.message_timer -= dt

        level_speed = self.progress() * 70
        road_speed = self.profile["speed"] + level_speed
        enemy_speed = self.profile["enemy_speed"] + level_speed
        self.distance += road_speed * dt * 0.55

        self.enemy_timer -= dt
        self.coin_timer -= dt

        if self.enemy_timer <= 0:
            self.spawn_enemy()
            self.enemy_timer = random.uniform(self.profile["enemy_gap"], self.profile["enemy_gap"] + 0.35)

        if self.coin_timer <= 0:
            self.spawn_coin()
            self.coin_timer = random.uniform(self.profile["coin_gap"], self.profile["coin_gap"] + 0.4)

        for enemy in self.traffic:
            enemy["rect"].y += int(enemy_speed * dt)

        for coin in self.coins:
            coin["rect"].y += int((road_speed + 40) * dt)

        self.traffic = [enemy for enemy in self.traffic if enemy["rect"].top < SCREEN_HEIGHT]
        self.coins = [coin for coin in self.coins if coin["rect"].top < SCREEN_HEIGHT]

        for coin in self.coins[:]:
            if self.player.colliderect(coin["rect"]):
                self.coin_total += coin["value"]
                self.coins.remove(coin)

        for enemy in self.traffic:
            if self.player.colliderect(enemy["rect"]):
                self.status = "game_over"
                self.message = "Crash"
                return self.status

        if self.distance >= self.finish_distance:
            self.status = "finished"

        return self.status

    def draw_car(self, surface, rect, color):
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, (25, 25, 25), rect, 2)
        glass = pygame.Rect(rect.x + 8, rect.y + 8, rect.width - 16, 14)
        pygame.draw.rect(surface, (220, 240, 255), glass)
        bumper = pygame.Rect(rect.x + 6, rect.bottom - 12, rect.width - 12, 6)
        pygame.draw.rect(surface, (40, 40, 40), bumper)

    def draw_road(self, surface):
        surface.fill((25, 125, 25))
        pygame.draw.rect(surface, (70, 70, 70), (ROAD_X, 0, ROAD_W, SCREEN_HEIGHT))
        pygame.draw.line(surface, (255, 255, 255), (ROAD_X, 0), (ROAD_X, SCREEN_HEIGHT), 4)
        pygame.draw.line(surface, (255, 255, 255), (ROAD_X + ROAD_W, 0), (ROAD_X + ROAD_W, SCREEN_HEIGHT), 4)

        for lane in range(1, LANES):
            x = ROAD_X + lane * LANE_W
            for y in range(20, SCREEN_HEIGHT, 60):
                pygame.draw.rect(surface, (230, 230, 230), (x - 2, y, 4, 30))

    def draw(self, surface, fonts):
        small = fonts["small"]
        medium = fonts["medium"]

        self.draw_road(surface)

        self.draw_car(surface, self.player, self.player_color)

        for enemy in self.traffic:
            self.draw_car(surface, enemy["rect"], enemy["color"])

        for coin in self.coins:
            pygame.draw.ellipse(surface, (255, 220, 60), coin["rect"])
            pygame.draw.ellipse(surface, (180, 140, 20), coin["rect"], 2)

        pygame.draw.rect(surface, (25, 25, 25), (10, 10, SCREEN_WIDTH - 20, 90))
        pygame.draw.rect(surface, (220, 220, 220), (10, 10, SCREEN_WIDTH - 20, 90), 2)

        surface.blit(medium.render(f"Score: {self.score()}", True, (240, 240, 240)), (18, 16))
        surface.blit(small.render(f"Coins: {self.coin_total}", True, (255, 220, 90)), (18, 48))
        surface.blit(small.render(f"Distance: {int(self.distance)} / {self.finish_distance} m", True, (240, 240, 240)), (120, 48))
        surface.blit(small.render(f"Difficulty: {self.settings['difficulty']}", True, (210, 210, 210)), (18, 72))

        if self.message_timer > 0:
            text = small.render(self.message, True, (255, 240, 120))
            surface.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, 118)))