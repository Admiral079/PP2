import pygame
import sys
from ball import Ball

pygame.init()

screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Moving Ball")

clock = pygame.time.Clock()
ball = Ball()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                ball.move_up()
            if event.key == pygame.K_DOWN:
                ball.move_down()
            if event.key == pygame.K_LEFT:
                ball.move_left()
            if event.key == pygame.K_RIGHT:
                ball.move_right()

    screen.fill((255, 255, 255))

    pygame.draw.circle(screen, (255, 0, 0), (ball.x, ball.y), ball.radius)

    pygame.display.flip()
    clock.tick(60)