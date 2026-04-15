import pygame
import sys
from player import Player

pygame.init()

screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Music Player")

font = pygame.font.SysFont(None, 36)

player = Player()
clock = pygame.time.Clock()

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
            if event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

    screen.fill((255, 255, 255))

    track_text = font.render("Track: " + player.get_current_track(), True, (0, 0, 0))
    pos_text = font.render("Time: " + str(player.get_position()) + " sec", True, (0, 0, 0))

    screen.blit(track_text, (50, 150))
    screen.blit(pos_text, (50, 200))

    pygame.display.flip()
    clock.tick(60)