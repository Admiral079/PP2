import pygame
import math
from collections import deque
from datetime import datetime

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS Paint")

clock = pygame.time.Clock()

canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill((255, 255, 255))

drawing = False
start_pos = None
last_pos = None

color = (0, 0, 0)
BG_COLOR = (255, 255, 255)
brush_size = 5
mode = "pencil"

text_mode = False
text_input = ""
text_pos = (0, 0)
font = pygame.font.SysFont(None, 24)

colors = [
    (0,0,0), (255,0,0), (0,255,0), (0,0,255),
    (255,255,0), (255,165,0), (255,255,255)
]

palette_rects = [pygame.Rect(10 + i*40, 10, 30, 30) for i in range(len(colors))]

def flood_fill(surface, x, y, new_color):
    if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
        return
    target_color = surface.get_at((x, y))
    if target_color == new_color:
        return
    q = deque([(x, y)])
    while q:
        px, py = q.popleft()
        if not (0 <= px < WIDTH and 0 <= py < HEIGHT):
            continue
        if surface.get_at((px, py)) != target_color:
            continue
        surface.set_at((px, py), new_color)
        q.extend([(px+1, py), (px-1, py), (px, py+1), (px, py-1)])

def draw_triangle(surface, p1, p2, draw_color):
    x1, y1 = p1
    x2, y2 = p2
    pygame.draw.polygon(surface, draw_color, [p1, p2, (x1, y2)], brush_size)

def draw_equilateral(surface, p1, p2, draw_color):
    x1, y1 = p1
    x2, y2 = p2
    left, right = sorted((x1, x2))
    top, bottom = sorted((y1, y2))
    width = right - left
    height = bottom - top

    if width == 0 or height == 0:
        return

    side = min(width, (2 * height) / math.sqrt(3))
    tri_height = side * math.sqrt(3) / 2
    center_x = (left + right) / 2

    if y2 >= y1:
        points = [
            (round(center_x), top),
            (round(center_x - side / 2), round(top + tri_height)),
            (round(center_x + side / 2), round(top + tri_height))
        ]
    else:
        points = [
            (round(center_x), bottom),
            (round(center_x - side / 2), round(bottom - tri_height)),
            (round(center_x + side / 2), round(bottom - tri_height))
        ]

    pygame.draw.polygon(surface, draw_color, points, brush_size)

def draw_rhombus(surface, p1, p2, draw_color):
    x1, y1 = p1
    x2, y2 = p2
    mx = (x1 + x2)//2
    pygame.draw.polygon(surface, draw_color, [
        (x1, y1), (mx, y1 - (y2-y1)), (x2, y2), (mx, y2 + (y2-y1))
    ], brush_size)

running = True
while running:
    current_color = BG_COLOR if mode == "eraser" else color
    screen.fill((200, 200, 200))
    preview = canvas.copy()
    screen.blit(canvas, (0, 0))

    for i, rect in enumerate(palette_rects):
        pygame.draw.rect(screen, colors[i], rect)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            clicked_ui = False
            for i, rect in enumerate(palette_rects):
                if rect.collidepoint(x, y):
                    color = colors[i]
                    if mode == "eraser": mode = "pencil"
                    clicked_ui = True
                    break
            if clicked_ui: continue 

            if mode == "fill":
                flood_fill(canvas, x, y, current_color)
            elif mode == "text":
                text_mode = True
                text_input = ""
                text_pos = (x, y)
            else:
                drawing = True
                start_pos = (x, y)
                last_pos = (x, y)

        if event.type == pygame.MOUSEBUTTONUP:
            if not drawing: continue
            drawing = False
            end_pos = event.pos

            if mode == "line":
                pygame.draw.line(canvas, current_color, start_pos, end_pos, brush_size)
            elif mode == "rect":
                rect = pygame.Rect(start_pos, (end_pos[0]-start_pos[0], end_pos[1]-start_pos[1]))
                rect.normalize()
                pygame.draw.rect(canvas, current_color, rect)
            elif mode == "circle":
                r = int(math.dist(start_pos, end_pos))
                pygame.draw.circle(canvas, current_color, start_pos, r, brush_size)
            elif mode == "square":
                dx = end_pos[0] - start_pos[0]
                dy = end_pos[1] - start_pos[1]
                s = min(abs(dx), abs(dy))
                left = start_pos[0] if dx >= 0 else start_pos[0] - s
                top = start_pos[1] if dy >= 0 else start_pos[1] - s
                pygame.draw.rect(canvas, current_color, (left, top, s, s))
            elif mode == "tri_right":
                draw_triangle(canvas, start_pos, end_pos, current_color)
            elif mode == "tri_eq":
                draw_equilateral(canvas, start_pos, end_pos, current_color)
            elif mode == "rhombus":
                draw_rhombus(canvas, start_pos, end_pos, current_color)

        if event.type == pygame.MOUSEMOTION and drawing:
            if mode == "pencil" or mode == "eraser":
                pygame.draw.line(canvas, current_color, last_pos, event.pos, brush_size)
                pygame.draw.circle(canvas, current_color, event.pos, brush_size // 2)
                last_pos = event.pos

        if event.type == pygame.KEYDOWN and text_mode:
            if event.key == pygame.K_RETURN:
                img = font.render(text_input, True, current_color)
                canvas.blit(img, text_pos)
                text_mode = False
            elif event.key == pygame.K_ESCAPE:
                text_mode = False
            elif event.key == pygame.K_BACKSPACE:
                text_input = text_input[:-1]
            else:
                text_input += event.unicode

    if drawing and mode != "pencil" and mode != "eraser":
        if mode == "line":
            pygame.draw.line(preview, current_color, start_pos, pygame.mouse.get_pos(), brush_size)
        screen.blit(preview, (0, 0))

    if text_mode:
        img = font.render(text_input, True, current_color)
        screen.blit(img, text_pos)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_p]: mode = "pencil"
    if keys[pygame.K_l]: mode = "line"
    if keys[pygame.K_r]: mode = "rect"
    if keys[pygame.K_c]: mode = "circle"
    if keys[pygame.K_s]: mode = "square"
    if keys[pygame.K_t]: mode = "tri_right"
    if keys[pygame.K_g]: mode = "tri_eq"
    if keys[pygame.K_h]: mode = "rhombus"
    if keys[pygame.K_f]: mode = "fill"
    if keys[pygame.K_x]: mode = "text"
    if keys[pygame.K_e]: mode = "eraser"

    if keys[pygame.K_1]: brush_size = 2
    if keys[pygame.K_2]: brush_size = 10
    if keys[pygame.K_3]: brush_size = 30

    if keys[pygame.K_LCTRL] and keys[pygame.K_s]:
        filename = datetime.now().strftime("paint_%Y%m%d_%H%M%S.png")
        pygame.image.save(canvas, filename)

    help_lines = [
        f"MODE: {mode.upper()}",
        "P Pencil | E Eraser | L Line",
        "R Rect | C Circle | S Square",
        "T Tri | G EqTri | H Rhombus",
        "F Fill | X Text",
        "1/2/3 Size | Ctrl+S Save"
    ]
    for i, line in enumerate(help_lines):
        screen.blit(font.render(line, True, (0,0,0)), (540, 10 + i*20))

    pygame.display.flip()
    clock.tick(60)
pygame.quit()
