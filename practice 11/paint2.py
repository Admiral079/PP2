import pygame
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")

clock = pygame.time.Clock()

canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill((255, 255, 255))

drawing = False
start_pos = None
last_pos = None

color = (0, 0, 0)
radius = 5

mode = "brush"

colors = [
    (0,0,0), (255,0,0), (0,255,0), (0,0,255),
    (255,255,0), (255,165,0)
]

def draw_triangle(surface, p1, p2, color):
    x1, y1 = p1
    x2, y2 = p2
    p3 = (x1, y2)
    pygame.draw.polygon(surface, color, [p1, p2, p3], 2)

def draw_equilateral(surface, p1, p2, color):
    x1, y1 = p1
    x2, y2 = p2
    dx = x2 - x1
    h = int(abs(dx) * (3 ** 0.5) / 2)
    p3 = (x1 + dx // 2, y1 - h)
    pygame.draw.polygon(surface, color, [p1, p2, p3], 2)

def draw_rhombus(surface, p1, p2, color):
    x1, y1 = p1
    x2, y2 = p2
    mx = (x1 + x2) // 2
    my = (y1 + y2) // 2
    p3 = (mx, y1 - (y2 - y1))
    p4 = (mx, y2 + (y2 - y1))
    pygame.draw.polygon(surface, color, [p1, p3, p2, p4], 2)

font = pygame.font.SysFont(None, 22)

running = True

while running:
    screen.fill((220, 220, 220))
    screen.blit(canvas, (0, 0))

    for i, c in enumerate(colors):
        pygame.draw.rect(screen, c, (10 + i*40, 10, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            for i, c in enumerate(colors):
                if pygame.Rect(10 + i*40, 10, 30, 30).collidepoint(x, y):
                    color = c

            drawing = True
            start_pos = event.pos
            last_pos = event.pos

        if event.type == pygame.MOUSEBUTTONUP:
            drawing = False
            end_pos = event.pos

            if mode == "rect":
                pygame.draw.rect(canvas, color, (*start_pos, end_pos[0]-start_pos[0], end_pos[1]-start_pos[1]), 2)

            if mode == "circle":
                r = int(math.dist(start_pos, end_pos))
                pygame.draw.circle(canvas, color, start_pos, r, 2)

            if mode == "square":
                s = min(abs(end_pos[0]-start_pos[0]), abs(end_pos[1]-start_pos[1]))
                pygame.draw.rect(canvas, color, (start_pos[0], start_pos[1], s, s), 2)

            if mode == "tri_right":
                draw_triangle(canvas, start_pos, end_pos, color)

            if mode == "tri_eq":
                draw_equilateral(canvas, start_pos, end_pos, color)

            if mode == "rhombus":
                draw_rhombus(canvas, start_pos, end_pos, color)

        if event.type == pygame.MOUSEMOTION and drawing:
            if mode == "brush":
                pygame.draw.line(canvas, color, last_pos, event.pos, radius)
                last_pos = event.pos

    keys = pygame.key.get_pressed()

    if keys[pygame.K_b]:
        mode = "brush"
    if keys[pygame.K_r]:
        mode = "rect"
    if keys[pygame.K_c]:
        mode = "circle"
    if keys[pygame.K_s]:
        mode = "square"
    if keys[pygame.K_t]:
        mode = "tri_right"
    if keys[pygame.K_e]:
        mode = "tri_eq"
    if keys[pygame.K_h]:
        mode = "rhombus"

    help_lines = [
        "B - Brush",
        "R - Rectangle",
        "C - Circle",
        "S - Square",
        "T - Right triangle",
        "E - Equilateral triangle",
        "H - Rhombus"
    ]

    for i, line in enumerate(help_lines):
        img = font.render(line, True, (0, 0, 0))
        screen.blit(img, (600, 10 + i * 20))

    mode_text = font.render(f"Mode: {mode}", True, (0, 0, 0))
    screen.blit(mode_text, (10, 50))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()