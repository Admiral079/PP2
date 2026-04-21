import pygame
import random

pygame.init()

WIDTH = 400
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 64)

def reset_game():
    player = pygame.Rect(180, 500, 40, 60)
    enemy = pygame.Rect(random.randint(0, WIDTH-40), -60, 40, 60)
    coins = []
    score = 0
    coin_spawn_time = 0
    return player, enemy, coins, score, coin_spawn_time

difficulty = "Normal"

player_speed = 5
enemy_speed = 5

def apply_difficulty():
    global player_speed, enemy_speed
    if difficulty == "Easy":
        player_speed = 5 * 1.5
        enemy_speed = 5 / 2
    elif difficulty == "Normal":
        player_speed = 5
        enemy_speed = 5
    elif difficulty == "Hard":
        player_speed = 5
        enemy_speed = 5 * 2

apply_difficulty()

player, enemy, coins, score, coin_spawn_time = reset_game()

coin_speed = 5

state = "menu"
running = True

while running:
    screen.fill((30, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if state == "game":
                    state = "pause"
                elif state == "pause":
                    state = "game"

    keys = pygame.key.get_pressed()

    if state == "menu":
        title = big_font.render("Racer", True, (255, 255, 255))
        start = font.render("SPACE - Start", True, (255, 255, 255))
        diff = font.render(f"Difficulty: {difficulty}", True, (255, 255, 0))
        change = font.render("D - change difficulty", True, (200, 200, 200))

        screen.blit(title, (120, 200))
        screen.blit(start, (110, 300))
        screen.blit(diff, (110, 350))
        screen.blit(change, (70, 390))

        if keys[pygame.K_d]:
            if difficulty == "Easy":
                difficulty = "Normal"
            elif difficulty == "Normal":
                difficulty = "Hard"
            else:
                difficulty = "Easy"
            apply_difficulty()
            pygame.time.delay(200)

        if keys[pygame.K_SPACE]:
            player, enemy, coins, score, coin_spawn_time = reset_game()
            state = "game"

    elif state == "game":
        if keys[pygame.K_LEFT] and player.x > 0:
            player.x -= player_speed
        if keys[pygame.K_RIGHT] and player.x < WIDTH - player.width:
            player.x += player_speed

        enemy.y += enemy_speed

        if enemy.y > HEIGHT:
            enemy.y = -60
            enemy.x = random.randint(0, WIDTH-40)

        coin_spawn_time += 1
        if coin_spawn_time > 40:
            coin = pygame.Rect(random.randint(0, WIDTH-20), -20, 20, 20)
            coins.append(coin)
            coin_spawn_time = 0

        for coin in coins:
            coin.y += coin_speed

        coins = [c for c in coins if c.y < HEIGHT]

        for coin in coins[:]:
            if player.colliderect(coin):
                coins.remove(coin)
                score += 1

        if player.colliderect(enemy):
            state = "game_over"

        pygame.draw.rect(screen, (0, 200, 255), player)
        pygame.draw.rect(screen, (255, 0, 0), enemy)

        for coin in coins:
            pygame.draw.rect(screen, (255, 255, 0), coin)

        text = font.render(f"Coins: {score}", True, (255, 255, 255))
        screen.blit(text, (250, 10))

    elif state == "pause":
        pause_text = big_font.render("Paused", True, (255, 255, 255))
        cont = font.render("ESC - Continue", True, (255, 255, 255))
        diff = font.render(f"Difficulty: {difficulty}", True, (255, 255, 0))
        change = font.render("D - change difficulty", True, (200, 200, 200))

        screen.blit(pause_text, (120, 250))
        screen.blit(cont, (90, 320))
        screen.blit(diff, (110, 360))
        screen.blit(change, (70, 400))

        if keys[pygame.K_d]:
            if difficulty == "Easy":
                difficulty = "Normal"
            elif difficulty == "Normal":
                difficulty = "Hard"
            else:
                difficulty = "Easy"
            apply_difficulty()
            pygame.time.delay(200)

    elif state == "game_over":
        over_text = big_font.render("Game Over", True, (255, 0, 0))
        restart_text = font.render("SPACE - Restart", True, (255, 255, 255))
        menu_text = font.render("M - Menu", True, (255, 255, 255))
        score_text = font.render(f"Coins: {score}", True, (255, 255, 255))

        screen.blit(over_text, (80, 240))
        screen.blit(restart_text, (90, 310))
        screen.blit(menu_text, (130, 350))
        screen.blit(score_text, (250, 10))

        if keys[pygame.K_SPACE]:
            player, enemy, coins, score, coin_spawn_time = reset_game()
            state = "game"

        if keys[pygame.K_m]:
            state = "menu"

    pygame.display.flip()
    clock.tick(60)

pygame.quit()