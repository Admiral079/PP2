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
    "Easy": {"road": 230, "traffic": 230, "finish": 3200, "traffic_gap": 1.4, "hazard_gap": 1.8},
    "Normal": {"road": 260, "traffic": 270, "finish": 4200, "traffic_gap": 1.2, "hazard_gap": 1.55},
    "Hard": {"road": 290, "traffic": 310, "finish": 5200, "traffic_gap": 1.0, "hazard_gap": 1.35},
}

COIN_TYPES = [(1, (255, 230, 60), 14), (3, (80, 230, 100), 18), (5, (230, 90, 220), 22)]
POWER_COLORS = {"nitro": (70, 200, 255), "shield": (80, 220, 120), "repair": (255, 170, 70)}


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
        self.finish_distance = self.profile["finish"]
        self.reset()

    def reset(self):
        self.player_lane = 1
        self.player = pygame.Rect(self.lane_x(self.player_lane), PLAYER_Y, 40, 64)
        self.distance = 0.0
        self.coin_total = 0
        self.score_bonus = 0
        self.enemy_bonus = 0.0
        self.status = "running"
        self.message = ""
        self.message_timer = 0.0
        self.active_power = None
        self.power_timer = 0.0
        self.slow_timer = 0.0
        self.boost_timer = 0.0
        self.next_checkpoint = 1000
        self.road_offset = 0.0
        self.saved = False
        self.coins = []
        self.traffic = []
        self.obstacles = []
        self.events = []
        self.powerups = []
        self.coin_timer = 0.4
        self.traffic_timer = 0.8
        self.hazard_timer = 1.0
        self.event_timer = 2.8
        self.powerup_timer = 4.0

    def lane_x(self, lane, width=40):
        return ROAD_X + lane * LANE_W + (LANE_W - width) // 2

    def progress(self):
        return min(1.0, self.distance / self.finish_distance)

    def score(self):
        return int(self.distance + self.coin_total * 20 + self.score_bonus)

    def summary(self):
        return {
            "name": self.username,
            "score": self.score(),
            "distance": int(self.distance),
            "coins": self.coin_total,
        }

    def handle_key(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.player_lane = max(0, self.player_lane - 1)
            elif event.key == pygame.K_RIGHT:
                self.player_lane = min(LANES - 1, self.player_lane + 1)
            self.player.x = self.lane_x(self.player_lane)

    def lane_free(self, lane, groups):
        if lane == self.player_lane:
            return False
        for group in groups:
            for item in group:
                if item["lane"] == lane and item["rect"].y < 140:
                    return False
        return True

    def random_lane(self, avoid_player=True, groups=()):
        lanes = list(range(LANES))
        random.shuffle(lanes)
        for lane in lanes:
            if not avoid_player or self.lane_free(lane, groups):
                return lane
        return None

    def spawn_coin(self):
        value, color, size = random.choices(COIN_TYPES, weights=[6, 3, 2], k=1)[0]
        lane = self.random_lane(False, [self.coins, self.powerups])
        if lane is None:
            return
        rect = pygame.Rect(self.lane_x(lane, size), -size - 10, size, size)
        self.coins.append({"lane": lane, "rect": rect, "value": value, "color": color})

    def spawn_traffic(self):
        lane = self.random_lane(True, [self.traffic, self.obstacles, self.events])
        if lane is None:
            return
        rect = pygame.Rect(self.lane_x(lane), -70, 40, 64)
        self.traffic.append({"lane": lane, "rect": rect, "speed": random.randint(-10, 40)})

    def spawn_obstacle(self):
        kinds = {
            "barrier": (54, 22),
            "oil": (46, 18),
            "pothole": (42, 18),
            "slow": (56, 22),
        }
        lane = self.random_lane(True, [self.traffic, self.obstacles, self.events])
        if lane is None:
            return
        kind = random.choice(list(kinds))
        w, h = kinds[kind]
        rect = pygame.Rect(self.lane_x(lane, w), -h - 10, w, h)
        self.obstacles.append({"lane": lane, "rect": rect, "kind": kind})

    def spawn_event(self):
        lane = self.random_lane(True, [self.traffic, self.obstacles, self.events])
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
        lane = self.random_lane(False, [self.coins, self.powerups])
        if lane is None:
            return
        kind = random.choice(["nitro", "shield", "repair"])
        rect = pygame.Rect(self.lane_x(lane, 22), -30, 22, 22)
        self.powerups.append({"lane": lane, "rect": rect, "kind": kind, "time": 5.5})

    def use_protection(self, text):
        if self.active_power == "shield":
            self.active_power, self.power_timer = None, 0.0
            self.message, self.message_timer = "Shield used", 1.2
            return True
        if self.active_power == "repair":
            self.active_power, self.power_timer = None, 0.0
            self.message, self.message_timer = text, 1.2
            return True
        self.status = "game_over"
        self.message = text
        return False

    def collect_power(self, kind):
        if self.active_power:
            self.score_bonus += 10
            return
        if kind == "nitro":
            self.active_power = "nitro"
            self.power_timer = random.uniform(3.0, 5.0)
        elif kind == "shield":
            self.active_power = "shield"
            self.power_timer = 0.0
        else:
            self.active_power = "repair"
            self.power_timer = 0.0
        self.score_bonus += 40
        self.message, self.message_timer = kind.title(), 1.0

    def update(self, dt):
        if self.status != "running":
            return self.status

        if self.message_timer > 0:
            self.message_timer -= dt
        if self.active_power == "nitro":
            self.power_timer -= dt
            if self.power_timer <= 0:
                self.active_power = None
                self.power_timer = 0.0
        if self.slow_timer > 0:
            self.slow_timer -= dt
        if self.boost_timer > 0:
            self.boost_timer -= dt

        level = self.progress()
        road_speed = self.profile["road"] + 50 * level + self.enemy_bonus
        if self.active_power == "nitro":
            road_speed += 120
        if self.boost_timer > 0:
            road_speed += 70
        if self.slow_timer > 0:
            road_speed -= 90
        road_speed = max(140, road_speed)
        traffic_speed = self.profile["traffic"] + 80 * level + self.enemy_bonus
        self.distance += road_speed * dt * 0.55
        self.road_offset = (self.road_offset + road_speed * dt) % 50

        while self.distance >= self.next_checkpoint and self.next_checkpoint < self.finish_distance:
            self.score_bonus += 100
            self.message = f"Checkpoint {self.next_checkpoint}m"
            self.message_timer = 1.3
            self.next_checkpoint += 1000

        self.coin_timer -= dt
        self.traffic_timer -= dt
        self.hazard_timer -= dt
        self.event_timer -= dt
        self.powerup_timer -= dt
        if self.coin_timer <= 0:
            self.spawn_coin()
            self.coin_timer = random.uniform(0.45, 0.7)
        if self.traffic_timer <= 0:
            self.spawn_traffic()
            self.traffic_timer = max(0.45, self.profile["traffic_gap"] - 0.45 * level)
        if self.hazard_timer <= 0:
            self.spawn_obstacle()
            self.hazard_timer = max(0.55, self.profile["hazard_gap"] - 0.4 * level)
        if self.event_timer <= 0:
            self.spawn_event()
            self.event_timer = random.uniform(2.5, 4.0)
        if self.powerup_timer <= 0:
            self.spawn_powerup()
            self.powerup_timer = random.uniform(5.5, 8.0)

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

        self.coins = [x for x in self.coins if x["rect"].top < SCREEN_HEIGHT]
        self.traffic = [x for x in self.traffic if x["rect"].top < SCREEN_HEIGHT]
        self.obstacles = [x for x in self.obstacles if x["rect"].top < SCREEN_HEIGHT]
        self.events = [x for x in self.events if x["rect"].top < SCREEN_HEIGHT]
        self.powerups = [x for x in self.powerups if x["rect"].top < SCREEN_HEIGHT and x["time"] > 0]

        for coin in self.coins[:]:
            if self.player.colliderect(coin["rect"]):
                self.coin_total += coin["value"]
                self.score_bonus += coin["value"] * 5
                self.enemy_bonus += 1.0
                self.coins.remove(coin)

        for power in self.powerups[:]:
            if self.player.colliderect(power["rect"]):
                self.collect_power(power["kind"])
                self.powerups.remove(power)

        for car in self.traffic[:]:
            if self.player.colliderect(car["rect"]):
                if self.use_protection("Traffic crash"):
                    self.traffic.remove(car)
                else:
                    return self.status

        for obj in self.obstacles[:]:
            if self.player.colliderect(obj["rect"]):
                if obj["kind"] == "barrier":
                    if self.use_protection("Barrier hit"):
                        self.obstacles.remove(obj)
                    else:
                        return self.status
                elif obj["kind"] in {"oil", "pothole", "slow"}:
                    if self.active_power == "repair":
                        self.active_power = None
                        self.message, self.message_timer = "Repair used", 1.0
                    else:
                        self.slow_timer = 1.0
                        self.message, self.message_timer = "Slow down", 1.0
                    self.obstacles.remove(obj)

        for event in self.events[:]:
            if self.player.colliderect(event["rect"]):
                if event["kind"] == "boost_strip":
                    self.boost_timer = 1.5
                    self.score_bonus += 20
                elif event["kind"] == "speed_bump":
                    self.slow_timer = 0.8
                elif event["kind"] == "moving_barrier":
                    if self.use_protection("Moving barrier"):
                        self.events.remove(event)
                    else:
                        return self.status
                if event in self.events:
                    self.events.remove(event)

        if self.distance >= self.finish_distance:
            self.status = "finished"
            self.score_bonus += 150
        return self.status

    def draw(self, surface, fonts):
        small, medium = fonts["small"], fonts["medium"]
        surface.fill((20, 120, 20))
        pygame.draw.rect(surface, (70, 70, 70), (ROAD_X, 0, ROAD_W, SCREEN_HEIGHT))
        pygame.draw.line(surface, (255, 255, 255), (ROAD_X, 0), (ROAD_X, SCREEN_HEIGHT), 4)
        pygame.draw.line(surface, (255, 255, 255), (ROAD_X + ROAD_W, 0), (ROAD_X + ROAD_W, SCREEN_HEIGHT), 4)
        for lane in range(1, LANES):
            x = ROAD_X + lane * LANE_W
            for y in range(-50, SCREEN_HEIGHT, 50):
                pygame.draw.rect(surface, (230, 230, 230), (x - 2, y + int(self.road_offset), 4, 28))

        pygame.draw.rect(surface, self.player_color, self.player)
        pygame.draw.rect(surface, (20, 20, 20), self.player, 2)
        if self.active_power == "shield":
            pygame.draw.rect(surface, (90, 220, 255), self.player.inflate(8, 8), 2)

        for item in self.traffic:
            pygame.draw.rect(surface, (220, 70, 70), item["rect"])
        for item in self.coins:
            pygame.draw.ellipse(surface, item["color"], item["rect"])
        for item in self.obstacles:
            color = {"barrier": (230, 140, 50), "oil": (10, 10, 10), "pothole": (110, 70, 40), "slow": (220, 190, 70)}
            shape = color[item["kind"]]
            draw = pygame.draw.ellipse if item["kind"] in {"oil", "pothole"} else pygame.draw.rect
            draw(surface, shape, item["rect"])
        for item in self.events:
            color = {"moving_barrier": (220, 90, 90), "speed_bump": (240, 210, 90), "boost_strip": (70, 210, 250)}
            pygame.draw.rect(surface, color[item["kind"]], item["rect"])
        for item in self.powerups:
            pygame.draw.rect(surface, POWER_COLORS[item["kind"]], item["rect"])
            letter = small.render(item["kind"][0].upper(), True, (20, 20, 20))
            surface.blit(letter, letter.get_rect(center=item["rect"].center))

        pygame.draw.rect(surface, (25, 25, 25), (10, 10, SCREEN_WIDTH - 20, 90))
        pygame.draw.rect(surface, (220, 220, 220), (10, 10, SCREEN_WIDTH - 20, 90), 2)
        surface.blit(medium.render(f"Score: {self.score()}", True, (240, 240, 240)), (18, 16))
        surface.blit(small.render(f"Coins: {self.coin_total}", True, (255, 220, 90)), (18, 46))
        surface.blit(small.render(f"Distance: {int(self.distance)} / {self.finish_distance} m", True, (240, 240, 240)), (120, 46))
        remain = max(0, int(self.finish_distance - self.distance))
        surface.blit(small.render(f"Left: {remain} m", True, (210, 210, 210)), (18, 72))
        power = "None"
        if self.active_power == "nitro":
            power = f"Nitro {self.power_timer:.1f}s"
        elif self.active_power:
            power = self.active_power.title()
        surface.blit(small.render(f"Power: {power}", True, (240, 240, 240)), (220, 72))
        if self.message_timer > 0:
            msg = small.render(self.message, True, (255, 240, 120))
            surface.blit(msg, msg.get_rect(center=(SCREEN_WIDTH // 2, 118)))