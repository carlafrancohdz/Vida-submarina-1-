import pygame
import random
import sys

#Arrancamos pygame
pygame.init()

#Cargamos los sonidos
bite_sound=pygame.mixer.Sound("Bite.mp3")
error_sound = pygame.mixer.Sound("Error.mp3")

#Definimos el tamaño de la ventana
WIDTH, HEIGHT= 800, 600
screen=pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vida Submarina")

# Fuente y reloj
font=pygame.font.Font(None, 36)
clock=pygame.time.Clock()

#Cargar imágenes
fondo=pygame.image.load("Fondo.png")
pez_img=pygame.image.load("Pez.png")
pez_img=pygame.transform.scale(pez_img, (50, 50))
alga_img=pygame.image.load("Alga.png")
alga_img=pygame.transform.scale(alga_img, (40, 40))
lata_img=pygame.image.load("lata.png")
lata_img=pygame.transform.scale(lata_img, (30, 30))
llanta_img=pygame.image.load("llanta.png")
llanta_img=pygame.transform.scale(llanta_img, (30, 30))
papel_img=pygame.image.load("papel.png")
papel_img=pygame.transform.scale(papel_img, (30, 30))

# Variables del juego
points = 0
lives = 10
game_over = False

# pez
fish = pez_img.get_rect(topleft=(WIDTH // 2, HEIGHT - 60))
# velocidad del pez (pixeles por frame)
fish_speed = 5

# Algas (objetos a recoger)
algas = []
for i in range(3):
    alga = alga_img.get_rect(topleft=(random.randint(0, WIDTH - 40), random.randint(0, HEIGHT - 40)))
    # velocidades razonables (pix/frame)
    algas.append({"img": alga_img, "rect": alga, "speed": random.randint(1, 3)})

# Enemigos (basura)
basura_imgs = [lata_img, llanta_img, papel_img]
enemigos = []
for _ in range(3):
    img = random.choice(basura_imgs)
    rect = img.get_rect(topleft=(random.randint(0, WIDTH - 30), random.randint(50, 500)))
    # velocidades razonables (antes había un 400 que provocaba movimiento instantáneo)
    enemigos.append({"img": img, "rect": rect, "speed": random.randint(2, 6)})
   
#Función para texto
def draw_text(text, x, y, color=(255, 255, 255)):
    img=font.render(text, True,color)
    screen.blit(img, (x,y))

#Bucle principal    
while True:
    screen.blit(fondo,(0, 0))
   
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            pygame.quit()
            sys.exit()
           
    if not game_over:
        # Movimiento del pez
        Keys = pygame.key.get_pressed()
        if Keys[pygame.K_LEFT]:
            fish.x -= fish_speed
        if Keys[pygame.K_RIGHT]:
            fish.x += fish_speed
        if Keys[pygame.K_UP]:
            fish.y -= fish_speed
        if Keys[pygame.K_DOWN]:
            fish.y += fish_speed
        fish.clamp_ip(screen.get_rect())
        screen.blit(pez_img, fish.topleft)

        # Algas: mover, dibujar y gestionar colisiones por cada alga
        for alga in algas:
            alga["rect"].y += alga["speed"]
            screen.blit(alga["img"], alga["rect"].topleft)

            # si sale por abajo, reubicarla arriba
            if alga["rect"].top > HEIGHT:
                alga["rect"].topleft = (random.randint(0, WIDTH - 40), random.randint(50, 300))

            # colisión con el pez
            if fish.colliderect(alga["rect"]):
                points += 1
                bite_sound.play()
                alga["rect"].topleft = (random.randint(0, WIDTH - 40), random.randint(50, 300))

        # Basura (enemigos): mover, dibujar y colisiones
        for enemigo in enemigos:
            enemigo["rect"].y += enemigo["speed"]
            screen.blit(enemigo["img"], enemigo["rect"].topleft)

            if enemigo["rect"].top > HEIGHT:
                enemigo["rect"].topleft = (random.randint(0, WIDTH - 30), random.randint(50, 400))

            if fish.colliderect(enemigo["rect"]):
                lives -= 1
                error_sound.play()
                enemigo["rect"].topleft = (random.randint(0, WIDTH - 30), random.randint(50, 400))

        # comprobar fin de juego
        if lives <= 0:
            game_over = True

    else:
        # pantalla de fin de juego
        draw_text("Perdiste, presiona ESC para salir", WIDTH // 2 - 170, HEIGHT // 2 - 20, (255, 0, 0))
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()
           
    # Marcadores          
    draw_text(f"Puntos: {points}", 10, 10)
    draw_text(f"Vidas: {lives}", 10, 50)
       
    pygame.display.flip()
    clock.tick(60)
