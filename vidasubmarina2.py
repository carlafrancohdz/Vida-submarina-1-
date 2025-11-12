import pygame
import random
import sys

#Arrancamos pygame
pygame.init()

#Cargamos los sonidos
bite_sound=pygame.mixer.Sound("Bite.mp3")

#Definimos el tamaño de la ventana
WIDTH, HEIGHT= 800, 600
screen=pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vida Submarina - Parte 2")

# Fuente y reloj
font=pygame.font.Font(None, 36)
clock=pygame.time.Clock()

#Cargar imágenes
fondo=pygame.image.load("Fondo.png")
pez_img=pygame.image.load("Pez.png")
pez_img=pygame.transform.scale(pez_img, (50, 50))
alga_img=pygame.image.load("Alga.png")
alga_img=pygame.transform.scale(alga_img, (40, 40))

algas=[]
for i in range(3):
    alga=alga_img.get_rect(topleft=(random.randint(0,WIDTH-40), random.randint(0, HEIGHT-40)))
    algas.append({"img":alga_img, "rect": alga, "speed": random.randint(3, 6)})
   
points=0


#pez
fish=pez_img.get_rect(topleft=(WIDTH//2, HEIGHT-60))
fish_speed=7

def draw_text(text, x, y, color=(255, 255, 255)):
    img=font.render(text, True,color)
    screen.blit(img, (x,y))
   
while True:
    screen.blit(fondo,(0, 0))
   
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            pygame.quit()
            sys.exit()
           
    Keys=pygame.key.get_pressed()
    if Keys[pygame.K_LEFT]:fish.x-=fish_speed
    if Keys[pygame.K_RIGHT]:fish.x+=fish_speed
    if Keys[pygame.K_UP]:fish.y-=fish_speed
    if Keys[pygame.K_DOWN]:fish.y+=fish_speed
   
    fish.clamp_ip(screen.get_rect())
    screen.blit(pez_img, fish.topleft)
   
    for alga in algas:
        alga["rect"].y+=alga["speed"]
        screen.blit(alga["img"],alga["rect"].topleft)
       
        if alga["rect"].top>HEIGHT:
            alga["rect"].topleft=(random.randint(0, WIDTH-40), random.randint(50,300))
           
        if fish.colliderect(alga["rect"]):
            points+=1
            bite_sound.play()
            alga["rect"].topleft=(random.randint(0,WIDTH-40), random.randint(50,300))
           
    draw_text(f"Puntos: {points}", 10, 10)
   
    pygame.display.flip()
    clock.tick(60)
