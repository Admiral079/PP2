import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")

clock = pygame.time.Clock()

drawing = False
last_pos = None

color = (0, 0, 0)
radius = 5
eraser_radius = 10

mode = "brush"

start_pos = None

colors = [
    (0,0,0), (255,0,0), (0,255,0), (0,0,255),
    (255,255,0), (255,165,0), (255,255,255)
]

canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill((255,255,255))

running = True

while running:
    screen.fill((200,200,200))
    screen.blit(canvas, (0,0))

    for i, c in enumerate(colors):
        pygame.draw.rect(screen, c, (10 + i*40, 10, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            for i, c in enumerate(colors):
                if pygame.Rect(10 + i*40, 10, 30, 30).collidepoint(x,y):
                    color = c

            drawing = True
            last_pos = event.pos
            start_pos = event.pos

        if event.type == pygame.MOUSEBUTTONUP:
            drawing = False

            if mode == "rect":
                end_pos = event.pos
                pygame.draw.rect(canvas, color, (*start_pos, end_pos[0]-start_pos[0], end_pos[1]-start_pos[1]), 2)

            if mode == "circle":
                end_pos = event.pos
                radius_c = int(((end_pos[0]-start_pos[0])**2 + (end_pos[1]-start_pos[1])**2)**0.5)
                pygame.draw.circle(canvas, color, start_pos, radius_c, 2)

        if event.type == pygame.MOUSEMOTION and drawing:
            if mode == "brush":
                pygame.draw.line(canvas, color, last_pos, event.pos, radius)
                last_pos = event.pos

            if mode == "eraser":
                pygame.draw.line(canvas, (255,255,255), last_pos, event.pos, eraser_radius)
                last_pos = event.pos

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                radius += 1
                eraser_radius += 1

            if event.key == pygame.K_DOWN:
                if radius > 1:
                    radius -= 1
                if eraser_radius > 2:
                    eraser_radius -= 1

    keys = pygame.key.get_pressed()

    if keys[pygame.K_b]:
        mode = "brush"
    if keys[pygame.K_r]:
        mode = "rect"
    if keys[pygame.K_c]:
        mode = "circle"
    if keys[pygame.K_e]:
        mode = "eraser"

    font = pygame.font.SysFont(None, 28)
    text = font.render(f"Mode: {mode}  Size: {radius}", True, (0,0,0))
    screen.blit(text, (10, 50))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()