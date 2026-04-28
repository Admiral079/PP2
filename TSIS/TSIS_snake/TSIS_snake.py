import pygame
import random

def run_game(best_score):

    pygame.init()

    WIDTH = 600
    HEIGHT = 600
    CELL = 20

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    snake = [(300, 300)]
    direction = (CELL, 0)

    foods = []
    food_timers = []

    def get_food():
        while True:
            pos = (random.randrange(0, WIDTH, CELL),
                   random.randrange(0, HEIGHT, CELL))
            if pos not in snake and pos not in foods:
                weight = random.choice([1, 2, 3])
                return (pos, weight, pygame.time.get_ticks())

    food_data = get_food()
    foods.append(food_data[0])
    food_weights = [food_data[1]]
    food_timers.append(food_data[2])

    score = 0
    level = 1
    speed = 7

    # =========================
    # NEW TSIS REQUIREMENTS
    # =========================

    poison = None
    poison_timer = 0

    power_up = None
    power_type = None
    power_spawn_time = 0

    active_effect = None
    effect_timer = 0
    base_speed = speed
    shield = False

    obstacles = []

    def spawn_poison():
        nonlocal poison, poison_timer
        while True:
            pos = (random.randrange(0, WIDTH, CELL),
                   random.randrange(0, HEIGHT, CELL))
            if pos not in snake and pos not in foods:
                poison = pos
                poison_timer = pygame.time.get_ticks()
                break

    def spawn_power():
        nonlocal power_up, power_type, power_spawn_time
        types = ["speed", "slow", "shield"]
        while True:
            pos = (random.randrange(0, WIDTH, CELL),
                   random.randrange(0, HEIGHT, CELL))
            if pos not in snake and pos not in foods:
                power_up = pos
                power_type = random.choice(types)
                power_spawn_time = pygame.time.get_ticks()
                break

    def generate_obstacles():
        nonlocal obstacles
        obstacles = []
        for _ in range(level * 3):
            pos = (random.randrange(0, WIDTH, CELL),
                   random.randrange(0, HEIGHT, CELL))
            if pos not in snake:
                obstacles.append(pos)

    # =========================

    running = True
    game_over = False

    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return score, level

        keys = pygame.key.get_pressed()

        if not game_over:

            # runtime mechanics
            if poison is None and random.randint(0, 200) == 1:
                spawn_poison()

            if power_up is None and random.randint(0, 300) == 1:
                spawn_power()

            if poison and current_time - poison_timer > 6000:
                poison = None

            if power_up and current_time - power_spawn_time > 8000:
                power_up = None

            if active_effect and current_time - effect_timer > 5000:
                speed = base_speed + (level - 1) * 2
                active_effect = None

            if level >= 3 and len(obstacles) == 0:
                generate_obstacles()

            # controls
            if keys[pygame.K_UP] and direction != (0, CELL):
                direction = (0, -CELL)
            if keys[pygame.K_DOWN] and direction != (0, -CELL):
                direction = (0, CELL)
            if keys[pygame.K_LEFT] and direction != (CELL, 0):
                direction = (-CELL, 0)
            if keys[pygame.K_RIGHT] and direction != (-CELL, 0):
                direction = (CELL, 0)

            new_head = (snake[0][0] + direction[0],
                        snake[0][1] + direction[1])

            # collisions
            if new_head[0] < 0 or new_head[0] >= WIDTH or new_head[1] < 0 or new_head[1] >= HEIGHT:
                if shield:
                    shield = False
                else:
                    game_over = True

            if new_head in snake:
                if shield:
                    shield = False
                else:
                    game_over = True

            if new_head in obstacles:
                if shield:
                    shield = False
                else:
                    game_over = True

            snake.insert(0, new_head)

            ate_food = False
            for i, food_pos in enumerate(foods):
                if new_head == food_pos:
                    score += food_weights[i]
                    ate_food = True
                    foods.pop(i)
                    food_weights.pop(i)
                    food_timers.pop(i)
                    break

            # poison
            if poison and new_head == poison:
                for _ in range(2):
                    if len(snake) > 1:
                        snake.pop()
                if len(snake) <= 1:
                    game_over = True
                poison = None

            # power-up
            if power_up and new_head == power_up:
                if power_type == "speed":
                    speed += 4
                    active_effect = "speed"
                    effect_timer = current_time
                elif power_type == "slow":
                    speed = max(4, speed - 3)
                    active_effect = "slow"
                    effect_timer = current_time
                elif power_type == "shield":
                    shield = True

                power_up = None

            if not ate_food:
                snake.pop()
            else:
                new_food = get_food()
                foods.append(new_food[0])
                food_weights.append(new_food[1])
                food_timers.append(new_food[2])

            # remove old food
            for i in range(len(foods) - 1, -1, -1):
                if current_time - food_timers[i] > 5000:
                    foods.pop(i)
                    food_weights.pop(i)
                    food_timers.pop(i)

            if len(foods) == 0:
                new_food = get_food()
                foods.append(new_food[0])
                food_weights.append(new_food[1])
                food_timers.append(new_food[2])

            # level system
            if score // 4 + 1 > level:
                level = score // 4 + 1
                speed += 2

        # DRAW
        screen.fill((0, 0, 0))

        for segment in snake:
            pygame.draw.rect(screen, (0, 255, 0), (*segment, CELL, CELL))

        for i, food_pos in enumerate(foods):
            color = [(255,0,0),(255,255,0),(255,165,0)][food_weights[i]-1]
            pygame.draw.rect(screen, color, (*food_pos, CELL, CELL))

        if poison:
            pygame.draw.rect(screen, (139,0,0), (*poison, CELL, CELL))

        if power_up:
            colors = {"speed":(0,255,255),"slow":(0,0,255),"shield":(255,255,255)}
            pygame.draw.rect(screen, colors[power_type], (*power_up, CELL, CELL))

        for obs in obstacles:
            pygame.draw.rect(screen, (120,120,120), (*obs, CELL, CELL))

        screen.blit(font.render(f"Score: {score}", True, (255,255,255)), (10,10))
        screen.blit(font.render(f"Level: {level}", True, (255,255,255)), (10,40))
        screen.blit(font.render(f"Best: {best_score}", True, (200,200,200)), (10,70))

        if game_over:
            screen.blit(font.render("Game Over", True, (255,0,0)), (230,250))
            screen.blit(font.render("ESC - Menu", True, (255,255,255)), (220,300))

            if keys[pygame.K_ESCAPE]:
                return score, level

        pygame.display.flip()
        clock.tick(speed)