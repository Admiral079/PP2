import pygame
import random

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
        x = random.randrange(0, WIDTH, CELL)
        y = random.randrange(0, HEIGHT, CELL)
        pos = (x, y)
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

running = True
game_over = False

while running:
    current_time = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if not game_over:
        if keys[pygame.K_UP] and direction != (0, CELL):
            direction = (0, -CELL)
        if keys[pygame.K_DOWN] and direction != (0, -CELL):
            direction = (0, CELL)
        if keys[pygame.K_LEFT] and direction != (CELL, 0):
            direction = (-CELL, 0)
        if keys[pygame.K_RIGHT] and direction != (-CELL, 0):
            direction = (CELL, 0)

        head_x = snake[0][0] + direction[0]
        head_y = snake[0][1] + direction[1]
        new_head = (head_x, head_y)

        if head_x < 0 or head_x >= WIDTH or head_y < 0 or head_y >= HEIGHT:
            game_over = True

        if new_head in snake:
            game_over = True

        snake.insert(0, new_head)

        ate_food = False
        for i, food_pos in enumerate(foods):
            if new_head == food_pos:
                weight = food_weights[i]
                score += weight
                ate_food = True
                foods.pop(i)
                food_weights.pop(i)
                food_timers.pop(i)
                break

        if ate_food:
            new_food = get_food()
            foods.append(new_food[0])
            food_weights.append(new_food[1])
            food_timers.append(new_food[2])
        else:
            snake.pop()

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

        if score // 4 + 1 > level:
            level = score // 4 + 1
            speed += 2

    screen.fill((0, 0, 0))

    for segment in snake:
        pygame.draw.rect(screen, (0, 255, 0), (segment[0], segment[1], CELL, CELL))

    for i, food_pos in enumerate(foods):
        if food_weights[i] == 1:
            color = (255, 0, 0)
        elif food_weights[i] == 2:
            color = (255, 255, 0)
        else:
            color = (255, 165, 0)
        pygame.draw.rect(screen, color, (food_pos[0], food_pos[1], CELL, CELL))

    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    level_text = font.render(f"Level: {level}", True, (255, 255, 255))

    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 40))

    if game_over:
        over = font.render("Game Over", True, (255, 0, 0))
        restart = font.render("Press SPACE", True, (255, 255, 255))
        screen.blit(over, (230, 250))
        screen.blit(restart, (210, 300))

        if keys[pygame.K_SPACE]:
            snake = [(300, 300)]
            direction = (CELL, 0)
            foods = []
            food_weights = []
            food_timers = []
            new_food = get_food()
            foods.append(new_food[0])
            food_weights.append(new_food[1])
            food_timers.append(new_food[2])
            score = 0
            level = 1
            speed = 7
            game_over = False

    pygame.display.flip()
    clock.tick(speed)

pygame.quit()