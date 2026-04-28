import pygame
from db import get_or_create_player, get_top10, get_best_score, save_game
from TSIS_snake import run_game

pygame.init()

WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake TSIS")

font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 48)

clock = pygame.time.Clock()

state = "menu"

username = ""
player_id = None
best_score = 0

#button
def draw_button(text, x, y):
    rect = pygame.Rect(x, y, 200, 50)
    pygame.draw.rect(screen, (70, 70, 70), rect)
    label = font.render(text, True, (255, 255, 255))
    screen.blit(label, (x + 40, y + 10))
    return rect

#main loop
running = True

while running:
    screen.fill((0, 0, 0))
    mouse = pygame.mouse.get_pos()
    click = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            click = True

        if state == "menu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username != "":
                    player_id = get_or_create_player(username)
                    best_score = get_best_score(player_id)
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    username += event.unicode

    #menu
    if state == "menu":

        title = big_font.render("SNAKE", True, (255, 255, 255))
        screen.blit(title, (220, 100))

        input_box = font.render("Name: " + username, True, (255, 255, 255))
        screen.blit(input_box, (180, 200))

        play_btn = draw_button("Play", 200, 260)
        lead_btn = draw_button("Leaderboard", 200, 330)
        quit_btn = draw_button("Quit", 200, 400)

        if click:
            if play_btn.collidepoint(mouse) and username:
                player_id = get_or_create_player(username)
                best_score = get_best_score(player_id)

                score, level = run_game(best_score)  # запускаем игру
                save_game(player_id, score, level)

            if lead_btn.collidepoint(mouse):
                state = "leaderboard"

            if quit_btn.collidepoint(mouse):
                running = False

    #leaderboard
    elif state == "leaderboard":

        title = big_font.render("TOP 10", True, (255, 255, 255))
        screen.blit(title, (220, 50))

        data = get_top10()

        y = 120
        for i, row in enumerate(data):
            text = font.render(
                f"{i+1}. {row[0]}  {row[1]}  lvl:{row[2]}",
                True,
                (255, 255, 255),
            )
            screen.blit(text, (100, y))
            y += 35

        back_btn = draw_button("Back", 200, 500)

        if click and back_btn.collidepoint(mouse):
            state = "menu"

    pygame.display.flip()
    clock.tick(60)

pygame.quit()