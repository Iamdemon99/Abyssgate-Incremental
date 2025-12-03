import pygame
import subprocess

pygame.init()

# --- Window Setup ---
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Abyssgate Incremental")
clock = pygame.time.Clock()

# --- Load Background ---
bg = pygame.image.load("background.jpg").convert()
bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))

# --- Colors ---
RED = (150, 0, 0)
RED_GLOW = (255, 40, 40)
WHITE = (255, 255, 255)

# --- Fonts ---
title_font = pygame.font.Font(None, 150)
button_font = pygame.font.Font(None, 65)

# --- Button Function ---
def draw_button(text, y):
    mouse = pygame.mouse.get_pos()
    text_surf = button_font.render(text, True, WHITE)
    rect = text_surf.get_rect(center=(WIDTH // 2, y))

    # Hover glow
    color = RED_GLOW if rect.collidepoint(mouse) else RED
    pygame.draw.rect(screen, color,
                     (rect.x - 25, rect.y - 15,
                      rect.width + 50, rect.height + 30),
                     border_radius=20)
    screen.blit(text_surf, rect)

    return rect

# --- Main GUI Loop ---
running = True
game_started = False  # Flag to prevent opening multiple game windows

while running:
    screen.blit(bg, (0, 0))  # Draw static background

    # Title
    title = "Abyssgate Incremental"
    title_surf = title_font.render(title, True, RED_GLOW)
    title_rect = title_surf.get_rect(center=(WIDTH // 2, 180))
    screen.blit(title_surf, title_rect)

    # Draw buttons and get their rects
    start_rect = draw_button("Start", 450)
    options_rect = draw_button("Options", 570)
    quit_rect = draw_button("Quit", 690)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Detect single mouse click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if start_rect.collidepoint(event.pos) and not game_started:
                subprocess.Popen(["python", "test.py"])
                game_started = True  # Prevent opening multiple windows
            elif options_rect.collidepoint(event.pos):
                print("Options!")
            elif quit_rect.collidepoint(event.pos):
                running = False

    pygame.display.update()
    clock.tick(60)

pygame.quit()
