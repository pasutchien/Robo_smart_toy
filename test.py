import pygame
import sys
import os

# Initialize Pygame
pygame.init()

# Set the dimensions of the window
width, height = 480, 320
screen = pygame.display.set_mode((width, height))

# Set the window title
pygame.display.set_caption("Image at Bottom Example")

current_minigame = 1

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the screen with black
    screen.fill((0, 0, 0))
    
    text_color = (255,255,255)
    font = pygame.font.Font(None, 40)
    count_text = f"{000} / {000}"
    count_surface = font.render(count_text, True, text_color)
    count_rect = count_surface.get_rect()
    count_rect.center = (width // 2, (height // 2) +75)
    screen.blit(count_surface, count_rect)
 
    
    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
