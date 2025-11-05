import pygame
import sys

pygame.init()

#Pantalla
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vida Submarina")

# Fuente y reloj
font = pygame.font.SysFont(None, 36)
clock = pygame.time.Clock()

# Cargar imágenes
fondo = pygame.image.load("Fondo.png")
pez_img = pygame.image.load("Pez.png")
pez_img = pygame.transform.scale(pez_img, (50, 50))

# Pez 
fish = pez_img.get_rect(topleft=(WIDTH//2, HEIGHT - 60))
fish_speed = 7

def draw_text(text, x, y, color=(255, 255, 255)):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))
    
while True:
    screen.blit(fondo, (0, 0))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: fish.x -= fish_speed
    if keys[pygame.K_RIGHT]: fish.x += fish_speed
    if keys[pygame.K_UP]: fish.y -= fish_speed
    if keys[pygame.K_DOWN]: fish.y += fish_speed
    
    fish.clamp_ip(screen.get_rect())
    screen.blit(pez_img, fish.topleft)
    
    
    
    pygame.display.flip()
    clock.tick(60)
    
    
    
    
    