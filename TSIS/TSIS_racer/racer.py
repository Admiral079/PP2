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
CHECKPOINT_DISTANCE = 1000

PROFILES = {
    "Easy": {"road": 220, "traffic": 230, "traffic_gap": 1.35, "hazard_gap": 1.8, "event_gap": 3.2, "power_gap": 6.2},
    "Normal": {"road": 250, "traffic": 270, "traffic_gap": 1.15, "hazard_gap": 1.55, "event_gap": 2.9, "power_gap": 5.8},
    "Hard": {"road": 290, "traffic": 320, "traffic_gap": 0.95, "hazard_gap": 1.3, "event_gap": 2.5, "power_gap": 5.2},
}

COIN_TYPES = [
    (1, (255, 230, 60), 14),
    (3, (80, 230, 100), 18),
    (5, (230, 90, 220), 22),
]

POWER_COLORS = {
    "nitro": (70, 200, 255),
    "shield": (90, 220, 120),
    "repair": (255, 170, 70),
}

OBSTACLE_COLORS = {
    "barrier": (230, 140, 50),
    "oil": (20, 20, 20),
    "pothole": (110, 75, 45),
    "slow": (220, 190, 70),
}

EVENT_COLORS = {
    "moving_barrier": (220, 90, 90),
    "speed_bump": (210, 170, 90),
    "boost_strip": (70, 210, 250),
}

ENEMY_COLORS = [
    (220, 70, 70),
    (90, 180, 240),
    (230, 140, 60),
    (180, 80, 220),
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
        self.profile = PROFILES[settings["difficulty"]]
        self.player_color = tuple(CAR_COLORS[settings["car_color"]])
        self.reset()

    def reset(self):
        self.player_lane = 1
        self.player = pygame.Rect(self.lane_x(self.player_lane), PLAYER_Y, 40, 64)
        self.distance = 0.0
        self.coin_total = 0
        self.score_bonus = 0
        self.status = "running"
        self.saved = False

        self.message = "Arrow keys: LEFT / RIGHT"
        self.message_timer = 2.0

        self.active_power = None
        self.power_timer = 0.0
        self.slow_timer = 0.0
        self.boost_timer = 0.0
        self.next_checkpoint = CHECKPOINT_DISTANCE

        self.coins = []
        self.traffic = []
        self.obstacles = []
        self.events = []
        self.powerups = []

        self.coin_timer = 0.35
        self.traffic_timer = 0.8
        self.hazard_timer = 1.0
        self.event_timer = 2.5
        self.powerup_timer = 4.0

    def lane_x(self, lane, width=40):
        return ROAD_X + lane * LANE_W + (LANE_W - width) // 2

    def level(self):
        return 1 + int(self.distance // 1200)

    def score(self):
        return int(self.distance) + self.coin_total * 20 + self.score_bonus

    def summary(self):
        return {
            "name": self.username,
            "score": self.score(),
            "distance": int(self.distance),
            "coins": self.coin_total,
        }

    def set_message(self, text, duration):
        self.message = text
        self.message_timer = duration

    def handle_key(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_LEFT:
            self.player_lane = max(0, self.player_lane - 1)
        elif event.key == pygame.K_RIGHT:
            self.player_lane = min(LANES - 1, self.player_lane + 1)
        self.player.x = self.lane_x(self.player_lane)

    def lane_free(self, lane, groups):
        for group in groups:
            for item in group:
                if item["lane"] == lane and item["rect"].y < 140:
                    return False
        return True

    def choose_lane(self, avoid_player=False, groups=()):
        lanes = list(range(LANES))
        random.shuffle(lanes)
        for lane in lanes:
            if avoid_player and lane == self.player_lane:
                continue
            if self.lane_free(lane, groups):
                return lane
        return None

    def spawn_coin(self):
        lane = self.choose_lane(False, [self.coins, self.powerups])
        if lane is None:
            return
        value, color, size = random.choices(COIN_TYPES, weights=[6, 3, 2], k=1)[0]
        rect = pygame.Rect(self.lane_x(lane, size), -size - 12, size, size)
        self.coins.append({"lane": lane, "rect": rect, "value": value, "color": color})

    def spawn_traffic(self):
        lane = self.choose_lane(True, [self.traffic, self.obstacles, self.events])
        if lane is None:
            return
        rect = pygame.Rect(self.lane_x(lane), -72, 40, 64)
        self.traffic.append(
            {
                "lane": lane,
                "rect": rect,
                "speed": random.randint(-10, 45),
                "color": random.choice(ENEMY_COLORS),
            }
        )

    def spawn_obstacle(self):
        kinds = {
            "barrier": (54, 22),
            "oil": (46, 18),
            "pothole": (42, 18),
            "slow": (56, 22),
        }
        lane = self.choose_lane(True, [self.traffic, self.obstacles, self.events])
        if lane is None:
            return
        kind = random.choice(list(kinds))
        width, height = kinds[kind]
        rect = pygame.Rect(self.lane_x(lane, width), -height - 10, width, height)
        self.obstacles.append({"lane": lane, "rect": rect, "kind": kind})

    def spawn_event(self):
        lane = self.choose_lane(True, [self.traffic, self.obstacles, self.events])
        if lane is None:
            return

        kind = random.choice(["moving_barrier", "speed_bump", "boost_strip"])
        if kind == "moving_barrier":
            rect = pygame.Rect(self.lane_x(lane, 58), -24, 58, 18)
            self.events.append({"lane": lane, "rect": rect, "kind": kind, "dx": 2})
        elif kind == "speed_bump":
            rect = pygame.Rect(ROAD_X + lane * LANE_W + 8, -16, LANE_W - 16, 10)
            self.events.append({"lane": lane, "rect": rect, "kind": kind})
        else:
            rect = pygame.Rect(ROAD_X + lane * LANE_W + 8, -20, LANE_W - 16, 14)
            self.events.append({"lane": lane, "rect": rect, "kind": kind})

    def spawn_powerup(self):
        if self.active_power:
            return
        lane = self.choose_lane(False, [self.coins, self.powerups])
        if lane is None:
            return
        kind = random.choice(["nitro", "shield", "repair"])
        rect = pygame.Rect(self.lane_x(lane, 24), -34, 24, 24)
        self.powerups.append({"lane": lane, "rect": rect, "kind": kind, "time": 6.0})

    def collect_power(self, kind):
        self.active_power = kind
        if kind == "nitro":
            self.power_timer = random.uniform(3.0, 5.0)
        else:
            self.power_timer = 0.0
        self.score_bonus += 40
        self.set_message(f"{kind.title()} active", 1.2)

    def consume_shield(self, text):
        if self.active_power == "shield":
            self.active_power = None
            self.power_timer = 0.0
            self.set_message(text, 1.2)
            return True
        return False

    def consume_repair(self, text):
        if self.active_power == "repair":
            self.active_power = None
            self.power_timer = 0.0
            self.set_message(text, 1.2)
            return True
        return False

    def road_speed(self):
        speed = self.profile["road"] + (self.level() - 1) * 22
        speed += self.coin_total * 1.5
        if self.active_power == "nitro":
            speed += 120
        if self.boost_timer > 0:
            speed += 70
        if self.slow_timer > 0:
            speed -= 90
        return max(150, speed)

    def traffic_speed(self):
        speed = self.profile["traffic"] + (self.level() - 1) * 30
        speed += self.coin_total * 3
        if self.active_power == "nitro":
            speed += 35
        return speed

    def update_timers(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt

        if self.active_power == "nitro":
            self.power_timer -= dt
            if self.power_timer <= 0:
                self.active_power = None
                self.power_timer = 0.0
                self.set_message("Nitro finished", 1.0)

        if self.slow_timer > 0:
            self.slow_timer -= dt

        if self.boost_timer > 0:
            self.boost_timer -= dt

    def update_spawns(self, dt):
        game_level = self.level()

        self.coin_timer -= dt
        self.traffic_timer -= dt
        self.hazard_timer -= dt
        self.event_timer -= dt
        self.powerup_timer -= dt

        if self.coin_timer <= 0:
            self.spawn_coin()
            self.coin_timer = random.uniform(0.45, 0.8)

        if self.traffic_timer <= 0:
            self.spawn_traffic()
            gap = self.profile["traffic_gap"] - 0.05 * min(game_level - 1, 8)
            self.traffic_timer = max(0.4, gap)

        if self.hazard_timer <= 0:
            self.spawn_obstacle()
            gap = self.profile["hazard_gap"] - 0.06 * min(game_level - 1, 8)
            self.hazard_timer = max(0.5, gap)

        if self.event_timer <= 0:
            self.spawn_event()
            gap = self.profile["event_gap"] - 0.05 * min(game_level - 1, 8)
            self.event_timer = max(1.5, gap)

        if self.powerup_timer <= 0:
            self.spawn_powerup()
            self.powerup_timer = random.uniform(self.profile["power_gap"], self.profile["power_gap"] + 2.0)

    def move_objects(self, dt, road_speed, traffic_speed):
        for item in self.coins:
            item["rect"].y += int((road_speed + 20) * dt)

        for item in self.traffic:
            item["rect"].y += int((traffic_speed + item["speed"]) * dt)

        for item in self.obstacles:
            item["rect"].y += int((road_speed + 15) * dt)

        for item in self.events:
            item["rect"].y += int((road_speed + 10) * dt)
            if item["kind"] == "moving_barrier":
                item["rect"].x += item["dx"]
                left = ROAD_X + item["lane"] * LANE_W + 4
                right = ROAD_X + (item["lane"] + 1) * LANE_W - item["rect"].width - 4
                if item["rect"].x <= left or item["rect"].x >= right:
                    item["dx"] *= -1

        for item in self.powerups:
            item["rect"].y += int((road_speed + 20) * dt)
            item["time"] -= dt

    def clear_old_objects(self):
        self.coins = [item for item in self.coins if item["rect"].top < SCREEN_HEIGHT]
        self.traffic = [item for item in self.traffic if item["rect"].top < SCREEN_HEIGHT]
        self.obstacles = [item for item in self.obstacles if item["rect"].top < SCREEN_HEIGHT]
        self.events = [item for item in self.events if item["rect"].top < SCREEN_HEIGHT]
        self.powerups = [item for item in self.powerups if item["rect"].top < SCREEN_HEIGHT and item["time"] > 0]

    def checkpoint_logic(self):
        while self.distance >= self.next_checkpoint:
            self.score_bonus += 100
            self.set_message(f"Checkpoint {self.next_checkpoint} m", 1.2)
            self.next_checkpoint += CHECKPOINT_DISTANCE

    def handle_coin_collisions(self):
        for coin in self.coins[:]:
            if self.player.colliderect(coin["rect"]):
                self.coin_total += coin["value"]
                self.score_bonus += coin["value"] * 5
                self.coins.remove(coin)

    def handle_powerup_collisions(self):
        for item in self.powerups[:]:
            if self.player.colliderect(item["rect"]):
                self.collect_power(item["kind"])
                self.powerups.remove(item)

    def handle_traffic_collisions(self):
        for item in self.traffic[:]:
            if self.player.colliderect(item["rect"]):
                if self.consume_shield("Shield blocked crash") or self.consume_repair("Repair fixed crash"):
                    self.traffic.remove(item)
                else:
                    self.status = "game_over"
                    self.set_message("Traffic crash", 1.5)
                    return True
        return False

    def handle_obstacle_collisions(self):
        for item in self.obstacles[:]:
            if not self.player.colliderect(item["rect"]):
                continue

            if item["kind"] == "barrier":
                if self.consume_shield("Shield blocked barrier") or self.consume_repair("Repair cleared barrier"):
                    self.obstacles.remove(item)
                else:
                    self.status = "game_over"
                    self.set_message("Barrier hit", 1.5)
                    return True
            elif item["kind"] in {"oil", "pothole", "slow"}:
                if self.consume_repair("Repair cleared hazard"):
                    pass
                else:
                    self.slow_timer = 1.1
                    self.set_message("Road hazard", 1.0)
                self.obstacles.remove(item)
        return False

    def handle_event_collisions(self):
        for item in self.events[:]:
            if not self.player.colliderect(item["rect"]):
                continue

            if item["kind"] == "boost_strip":
                self.boost_timer = 1.6
                self.score_bonus += 20
                self.set_message("Boost strip", 0.9)
            elif item["kind"] == "speed_bump":
                if self.consume_repair("Repair softened bump"):
                    pass
                else:
                    self.slow_timer = 0.8
                    self.set_message("Speed bump", 0.9)
            elif item["kind"] == "moving_barrier":
                if self.consume_shield("Shield blocked barrier") or self.consume_repair("Repair fixed crash"):
                    pass
                else:
                    self.status = "game_over"
                    self.set_message("Moving barrier", 1.5)
                    return True

            if item in self.events:
                self.events.remove(item)
        return False

    def update(self, dt):
        if self.status != "running":
            return self.status

        self.update_timers(dt)

        road_speed = self.road_speed()
        traffic_speed = self.traffic_speed()
        self.distance += road_speed * dt * 0.55

        self.checkpoint_logic()
        self.update_spawns(dt)
        self.move_objects(dt, road_speed, traffic_speed)
        self.clear_old_objects()

        self.handle_coin_collisions()
        self.handle_powerup_collisions()

        if self.handle_traffic_collisions():
            return self.status
        if self.handle_obstacle_collisions():
            return self.status
        if self.handle_event_collisions():
            return self.status

        return self.status

    def draw_road(self, surface):
        surface.fill((20, 120, 20))
        pygame.draw.rect(surface, (70, 70, 70), (ROAD_X, 0, ROAD_W, SCREEN_HEIGHT))
        pygame.draw.line(surface, (255, 255, 255), (ROAD_X, 0), (ROAD_X, SCREEN_HEIGHT), 4)
        pygame.draw.line(surface, (255, 255, 255), (ROAD_X + ROAD_W, 0), (ROAD_X + ROAD_W, SCREEN_HEIGHT), 4)

        for lane in range(1, LANES):
            x = ROAD_X + lane * LANE_W
            for y in range(20, SCREEN_HEIGHT, 60):
                pygame.draw.rect(surface, (230, 230, 230), (x - 2, y, 4, 30))

    def draw_car(self, surface, rect, color):
        pygame.draw.rect(surface, color, rect, border_radius=4)
        pygame.draw.rect(surface, (25, 25, 25), rect, 2, border_radius=4)
        glass = pygame.Rect(rect.x + 8, rect.y + 8, rect.width - 16, 14)
        pygame.draw.rect(surface, (220, 240, 255), glass, border_radius=3)
        wheel_w = 5
        for x in (rect.x - 2, rect.right - 3):
            pygame.draw.rect(surface, (25, 25, 25), (x, rect.y + 10, wheel_w, 12), border_radius=2)
            pygame.draw.rect(surface, (25, 25, 25), (x, rect.bottom - 22, wheel_w, 12), border_radius=2)
        pygame.draw.rect(surface, (255, 240, 180), (rect.x + 6, rect.y + 4, 8, 4))
        pygame.draw.rect(surface, (255, 240, 180), (rect.right - 14, rect.y + 4, 8, 4))

    def draw_coin(self, surface, item):
        rect = item["rect"]
        pygame.draw.ellipse(surface, item["color"], rect)
        inner = rect.inflate(-6, -6)
        pygame.draw.ellipse(surface, (255, 245, 200), inner, 2)
        pygame.draw.line(surface, (255, 255, 255), (rect.x + 4, rect.y + 6), (rect.x + 9, rect.y + 3), 2)

    def draw_obstacle(self, surface, item):
        rect = item["rect"]
        kind = item["kind"]

        if kind == "barrier":
            pygame.draw.rect(surface, OBSTACLE_COLORS[kind], rect)
            pygame.draw.rect(surface, (40, 40, 40), rect, 2)
            for offset in range(-rect.height, rect.width, 12):
                start = (rect.x + offset, rect.bottom)
                end = (rect.x + offset + 12, rect.y)
                pygame.draw.line(surface, (255, 255, 255), start, end, 3)
        elif kind == "oil":
            pygame.draw.ellipse(surface, OBSTACLE_COLORS[kind], rect)
            pygame.draw.ellipse(surface, (70, 70, 70), rect.inflate(-10, -8), 2)
            pygame.draw.circle(surface, (90, 90, 90), (rect.x + 12, rect.y + 7), 3)
        elif kind == "pothole":
            pygame.draw.ellipse(surface, OBSTACLE_COLORS[kind], rect)
            pygame.draw.ellipse(surface, (45, 25, 10), rect.inflate(-8, -6))
            pygame.draw.ellipse(surface, (140, 100, 60), rect, 2)
        else:
            pygame.draw.rect(surface, OBSTACLE_COLORS[kind], rect)
            pygame.draw.rect(surface, (35, 35, 35), rect, 2)
            for x in range(rect.x + 4, rect.right, 10):
                pygame.draw.line(surface, (40, 40, 40), (x, rect.y + 2), (x - 8, rect.bottom - 2), 2)

    def draw_event(self, surface, item):
        rect = item["rect"]
        kind = item["kind"]
        color = EVENT_COLORS[kind]

        if kind == "moving_barrier":
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (255, 255, 255), rect, 2)
            for x in range(rect.x + 5, rect.right, 12):
                pygame.draw.line(surface, (255, 255, 255), (x, rect.y + 2), (x - 8, rect.bottom - 2), 2)
        elif kind == "speed_bump":
            pygame.draw.rect(surface, color, rect, border_radius=6)
            pygame.draw.arc(surface, (120, 80, 40), rect.inflate(-8, 4), 0, 3.14, 2)
        else:
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (220, 250, 255), rect, 2)
            center_y = rect.centery
            for shift in (10, 24, 38):
                points = [
                    (rect.x + shift - 5, center_y - 4),
                    (rect.x + shift + 3, center_y),
                    (rect.x + shift - 5, center_y + 4),
                ]
                pygame.draw.polygon(surface, (230, 255, 255), points)

    def draw_powerup(self, surface, item, font):
        rect = item["rect"]
        kind = item["kind"]
        color = POWER_COLORS[kind]

        if kind == "shield":
            points = [
                (rect.centerx, rect.y),
                (rect.right, rect.centery),
                (rect.centerx, rect.bottom),
                (rect.x, rect.centery),
            ]
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, (20, 20, 20), points, 2)
        else:
            pygame.draw.rect(surface, color, rect, border_radius=4)
            pygame.draw.rect(surface, (20, 20, 20), rect, 2, border_radius=4)

        if kind == "nitro":
            pygame.draw.line(surface, (255, 255, 255), (rect.x + 7, rect.y + 5), (rect.centerx, rect.centery), 2)
            pygame.draw.line(surface, (255, 255, 255), (rect.centerx, rect.centery), (rect.x + 12, rect.bottom - 4), 2)
            pygame.draw.line(surface, (255, 255, 255), (rect.x + 12, rect.bottom - 4), (rect.right - 6, rect.centery), 2)
        elif kind == "shield":
            pygame.draw.circle(surface, (255, 255, 255), rect.center, 5, 2)
        else:
            pygame.draw.line(surface, (255, 255, 255), (rect.centerx, rect.y + 5), (rect.centerx, rect.bottom - 5), 3)
            pygame.draw.line(surface, (255, 255, 255), (rect.x + 5, rect.centery), (rect.right - 5, rect.centery), 3)

        tag = font.render(kind[0].upper(), True, (20, 20, 20))
        surface.blit(tag, tag.get_rect(center=(rect.centerx, rect.bottom + 12)))

    def draw_hud(self, surface, fonts):
        small = fonts["small"]
        medium = fonts["medium"]

        pygame.draw.rect(surface, (25, 25, 25), (10, 10, SCREEN_WIDTH - 20, 104))
        pygame.draw.rect(surface, (220, 220, 220), (10, 10, SCREEN_WIDTH - 20, 104), 2)

        surface.blit(medium.render(f"Score: {self.score()}", True, (240, 240, 240)), (18, 14))
        surface.blit(small.render(f"Coins: {self.coin_total}", True, (255, 220, 90)), (18, 48))
        surface.blit(small.render(f"Distance: {int(self.distance)} m", True, (240, 240, 240)), (120, 48))
        surface.blit(small.render(f"Level: {self.level()}", True, (210, 210, 210)), (18, 74))

        left = max(0, self.next_checkpoint - int(self.distance))
        surface.blit(small.render(f"Next checkpoint: {left} m", True, (210, 210, 210)), (120, 74))

        if self.active_power == "nitro":
            power_text = f"Nitro {self.power_timer:.1f}s"
        elif self.active_power == "shield":
            power_text = "Shield ready"
        elif self.active_power == "repair":
            power_text = "Repair ready"
        else:
            power_text = "None"
        surface.blit(small.render(f"Power: {power_text}", True, (240, 240, 240)), (220, 22))

        if self.message_timer > 0:
            text = small.render(self.message, True, (255, 240, 120))
            surface.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, 132)))

    def draw(self, surface, fonts):
        self.draw_road(surface)

        for item in self.events:
            self.draw_event(surface, item)

        for item in self.obstacles:
            self.draw_obstacle(surface, item)

        for item in self.coins:
            self.draw_coin(surface, item)

        for item in self.powerups:
            self.draw_powerup(surface, item, fonts["small"])

        for item in self.traffic:
            self.draw_car(surface, item["rect"], item["color"])

        if self.active_power == "shield":
            pygame.draw.rect(surface, (90, 220, 255), self.player.inflate(10, 10), 2, border_radius=6)
        if self.active_power == "nitro":
            flame = [
                (self.player.centerx, self.player.bottom + 8),
                (self.player.centerx - 6, self.player.bottom - 2),
                (self.player.centerx + 6, self.player.bottom - 2),
            ]
            pygame.draw.polygon(surface, (255, 180, 70), flame)

        self.draw_car(surface, self.player, self.player_color)
        self.draw_hud(surface, fonts)