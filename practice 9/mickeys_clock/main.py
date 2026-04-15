import pygame
import sys
from clock import Clock

pygame.init()

screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("Mickey Clock")

bg = pygame.image.load("mickeyclock.jpeg")
bg = pygame.transform.scale(bg, (600, 600))

right_hand = pygame.image.load("right_hand.png")
left_hand = pygame.image.load("left_hand.png")

right_hand = pygame.transform.scale(right_hand, (300, 300))
left_hand = pygame.transform.scale(left_hand, (300, 300))

center = (300, 300)

clock = pygame.time.Clock()
clock_obj = Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    clock_obj.update()

    min_angle = clock_obj.get_minute_angle()
    sec_angle = clock_obj.get_second_angle()

    rotated_min = pygame.transform.rotate(right_hand, min_angle)
    rotated_sec = pygame.transform.rotate(left_hand, sec_angle)

    rect_min = rotated_min.get_rect(center=center)
    rect_sec = rotated_sec.get_rect(center=center)

    screen.blit(bg, (0, 0))
    screen.blit(rotated_min, rect_min)
    screen.blit(rotated_sec, rect_sec)

    pygame.display.flip()
    clock.tick(60)