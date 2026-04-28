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

def get_food():
    while True:
        x = random.randrange(0, WIDTH, CELL)
        y = random.randrange(0, HEIGHT, CELL)
        if (x, y) not in snake:
            return (x, y)

food = get_food()

score = 0
level = 1
speed = 7

running = True
game_over = False

while running:
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

        if new_head == food:
            score += 1
            food = get_food()
        else:
            snake.pop()

        if score // 4 + 1 > level:
            level = score // 4 + 1
            speed += 2

    screen.fill((0, 0, 0))

    for segment in snake:
        pygame.draw.rect(screen, (0, 255, 0), (segment[0], segment[1], CELL, CELL))

    pygame.draw.rect(screen, (255, 0, 0), (food[0], food[1], CELL, CELL))

    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    level_text = font.render(f"Level: {level}", True, (255, 255, 255))

    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 40))

    if game_over:
        over = font.render("Game Over", True, (255, 0, 0))
        restart = font.render("Press SPACE to continue", True, (255, 255, 255))
        screen.blit(over, (230, 250))
        screen.blit(restart, (210, 300))

        if keys[pygame.K_SPACE]:
            snake = [(300, 300)]
            direction = (CELL, 0)
            food = get_food()
            score = 0
            level = 1
            speed = 7
            game_over = False

    pygame.display.flip()
    clock.tick(speed)

pygame.quit()