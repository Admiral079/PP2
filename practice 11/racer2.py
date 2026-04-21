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

difficulty = "Normal"
difficulty_index = 1
difficulties = ["Easy", "Normal", "Hard"]

def apply_difficulty():
    global player_speed, enemy_speed
    if difficulty == "Easy":
        player_speed = 5 / 1.5
        enemy_speed = 5 / 2
    elif difficulty == "Normal":
        player_speed = 5
        enemy_speed = 5
    else:
        player_speed = 5
        enemy_speed = 5 * 2

def reset_game():
    player = pygame.Rect(180, 500, 40, 60)
    enemy = pygame.Rect(random.randint(0, WIDTH-40), -60, 40, 60)
    coins = []
    score = 0
    coin_timer = 0
    return player, enemy, coins, score, coin_timer

apply_difficulty()

player, enemy, coins, score, coin_timer = reset_game()

coin_speed = 5
state = "menu"

running = True

while running:
    screen.fill((30, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if state == "menu":
                if event.key == pygame.K_UP:
                    difficulty_index = (difficulty_index - 1) % 3
                    difficulty = difficulties[difficulty_index]
                    apply_difficulty()
                elif event.key == pygame.K_DOWN:
                    difficulty_index = (difficulty_index + 1) % 3
                    difficulty = difficulties[difficulty_index]
                    apply_difficulty()
            
            if state == "game" and event.key == pygame.K_ESCAPE:
                state = "pause"
            elif state == "pause" and event.key == pygame.K_ESCAPE:
                state = "game"

    keys = pygame.key.get_pressed()

    if state == "menu":
        title = big_font.render("Racer", True, (255, 255, 255))
        start = font.render("SPACE - Start", True, (255, 255, 255))
        
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))
        screen.blit(start, (WIDTH//2 - start.get_width()//2, 300))
        
        y_offset = 380
        for i, diff_option in enumerate(difficulties):
            if diff_option == difficulty:
                diff_text = font.render(f"> {diff_option} <", True, (255, 255, 0))
            else:
                diff_text = font.render(f"  {diff_option}", True, (200, 200, 200))
            screen.blit(diff_text, (WIDTH//2 - diff_text.get_width()//2, y_offset))
            y_offset += 30
        
        hint = font.render("UP/DOWN - Change difficulty", True, (150, 150, 150))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, 500))

        if keys[pygame.K_SPACE]:
            player, enemy, coins, score, coin_timer = reset_game()
            state = "game"

    elif state == "game":
        if keys[pygame.K_LEFT] and player.x > 0:
            player.x -= player_speed
        if keys[pygame.K_RIGHT] and player.x < WIDTH - player.width:
            player.x += player_speed

        enemy.y += enemy_speed
        if enemy.y > HEIGHT:
            enemy.y = -60
            enemy.x = random.randint(0, WIDTH - 40)

        coin_timer += 1
        if coin_timer > 35:
            weight = random.choice([1, 2, 3])
            if weight == 1:
                color = (255, 255, 0)
                value = 1
                size = 15
            elif weight == 2:
                color = (0, 255, 0)
                value = 3
                size = 18
            else:
                color = (255, 0, 255)
                value = 5
                size = 22

            coin = {
                "rect": pygame.Rect(random.randint(0, WIDTH-30), -20, size, size),
                "value": value,
                "color": color
            }
            coins.append(coin)
            coin_timer = 0

        for coin in coins:
            coin["rect"].y += coin_speed

        coins = [c for c in coins if c["rect"].y < HEIGHT]

        for coin in coins[:]:
            if player.colliderect(coin["rect"]):
                score += coin["value"]
                coins.remove(coin)

        if score > 0 and score % 10 == 0:
            enemy_speed += 0.05

        if player.colliderect(enemy):
            state = "game_over"

        pygame.draw.rect(screen, (0, 200, 255), player)
        pygame.draw.rect(screen, (255, 0, 0), enemy)

        for coin in coins:
            pygame.draw.rect(screen, coin["color"], coin["rect"])

        text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(text, (WIDTH - text.get_width() - 10, 10))
        
        diff_text = font.render(f"{difficulty}", True, (200, 200, 200))
        screen.blit(diff_text, (10, 10))
        
        pause_hint = font.render("ESC - Pause", True, (150, 150, 150))
        screen.blit(pause_hint, (WIDTH//2 - pause_hint.get_width()//2, HEIGHT - 30))

    elif state == "pause":
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        paused_text = big_font.render("PAUSED", True, (255, 255, 255))
        screen.blit(paused_text, (WIDTH//2 - paused_text.get_width()//2, HEIGHT//2 - 50))
        
        resume_text = font.render("ESC - Resume", True, (255, 255, 255))
        screen.blit(resume_text, (WIDTH//2 - resume_text.get_width()//2, HEIGHT//2 + 20))
        
        menu_text = font.render("M - Menu", True, (255, 255, 255))
        screen.blit(menu_text, (WIDTH//2 - menu_text.get_width()//2, HEIGHT//2 + 60))
        
        if keys[pygame.K_m]:
            state = "menu"
            player, enemy, coins, score, coin_timer = reset_game()

    elif state == "game_over":
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(100)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        over = big_font.render("Game Over", True, (255, 0, 0))
        restart = font.render("SPACE - Restart", True, (255, 255, 255))
        menu = font.render("M - Menu", True, (255, 255, 255))
        
        final_score = font.render(f"Final Score: {score}", True, (255, 255, 0))

        screen.blit(over, (WIDTH//2 - over.get_width()//2, 200))
        screen.blit(final_score, (WIDTH//2 - final_score.get_width()//2, 280))
        screen.blit(restart, (WIDTH//2 - restart.get_width()//2, 360))
        screen.blit(menu, (WIDTH//2 - menu.get_width()//2, 400))

        if keys[pygame.K_SPACE]:
            player, enemy, coins, score, coin_timer = reset_game()
            state = "game"

        if keys[pygame.K_m]:
            state = "menu"
            player, enemy, coins, score, coin_timer = reset_game()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()