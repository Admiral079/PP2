import pygame
import sys
from player import Player

pygame.init()

screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Music Player")

font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)

player = Player()
clock = pygame.time.Clock()

def format_time(seconds):
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                player.play()
            if event.key == pygame.K_s:
                player.stop()
            if event.key == pygame.K_n:
                player.next()
            if event.key == pygame.K_b:
                player.prev()
            if event.key == pygame.K_SPACE:
                if player.playing:
                    player.pause()
                else:
                    player.unpause()
            if event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

    screen.fill((255, 255, 255))

    track_name = player.get_current_track().split('\\')[-1]
    track_text = font.render("Track: " + track_name, True, (0, 0, 0))
    
    current_time = player.get_position()
    time_text = font.render("Time: " + format_time(current_time), True, (0, 0, 0))
    
    if player.playing:
        status = "Playing"
        status_color = (0, 128, 0)
    else:
        status = "Paused"
        status_color = (255, 0, 0)
    
    status_text = font.render("Status: " + status, True, status_color)
    
    instructions = [
        "Controls:",
        "P - Play",
        "S - Stop",
        "N - Next track",
        "B - Previous track",
        "SPACE - Pause/Resume",
        "Q - Quit"
    ]
    
    screen.blit(track_text, (50, 80))
    screen.blit(time_text, (50, 130))
    screen.blit(status_text, (50, 180))
    
    y_offset = 250
    for instruction in instructions:
        inst_text = small_font.render(instruction, True, (100, 100, 100))
        screen.blit(inst_text, (50, y_offset))
        y_offset += 25

    pygame.display.flip()
    clock.tick(60)