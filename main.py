import pygame
import random
import math
from collections import deque

# ---------------------------------------
# Configuración base
# ---------------------------------------
WIDTH, HEIGHT = 960, 540
FPS = 60
BG_COLOR = (20, 22, 30)

E_AGUA = 1
E_FUEGO = 2
E_RAYO = 3
E_HUMO = 4
E_LINTERNA = 5

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Efectos: Agua(1) Fuego(2) Rayo(3) Humo(4) Linterna(5)")
clock = pygame.time.Clock()

# ---------------------------------------
# Utilidades
# ---------------------------------------
def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def lerp(a, b, t):
    return a + (b - a) * t

# ---------------------------------------
# Sistema de partículas genérico
# ---------------------------------------
class Particle:
    __slots__ = ("x", "y", "vx", "vy", "r", "life", "max_life", "color")
    def __init__(self, x, y, vx, vy, r, life, color):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.r = r
        self.life = life
        self.max_life = life
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        return self.life > 0

    def draw(self, surf):
        if self.life <= 0:
            return
        alpha = int(255 * (self.life / self.max_life))
        alpha = clamp(alpha, 0, 255)
        c = (*self.color[:3], alpha)
        # Dibujar como círculo en una superficie temporal con alpha
        r = max(1, int(self.r * (0.5 + 0.5 * self.life / self.max_life)))
        temp = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
        pygame.draw.circle(temp, c, (r+1, r+1), r)
        surf.blit(temp, (int(self.x - r), int(self.y - r)))

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, p: Particle):
        self.particles.append(p)

    def update(self):
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, surf):
        for p in self.particles:
            p.draw(surf)

# ---------------------------------------
# Efecto: FUEGO (partículas ascendentes + glow)
# ---------------------------------------
class FireEffect:
    def __init__(self, x, y, spread=60):
        self.ps = ParticleSystem()
        self.x, self.y = x, y
        self.spread = spread
        self.timer = 0

    def update(self):
        self.timer += 1
        # Emitir varias partículas por frame
        for _ in range(10):
            ang = random.uniform(-math.pi/8, math.pi/8)
            speed = random.uniform(1.0, 3.0)
            vx = math.cos(ang) * 0.3
            vy = -speed
            r = random.randint(3, 6)
            life = random.randint(20, 40)
            # Paleta cálida aleatoria
            color = (
                random.randint(220, 255),  # R
                random.randint(120, 180),  # G
                random.randint(20, 60)     # B
            )
            ox = self.x + random.uniform(-self.spread, self.spread)
            oy = self.y + random.uniform(-10, 10)
            self.ps.emit(Particle(ox, oy, vx, vy, r, life, color))

        self.ps.update()

    def draw(self, surf):
        self.ps.draw(surf)
        # Glow base (mancha rojiza)
        glow = pygame.Surface((200, 200), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 100, 30, 60), (100, 100), 90)
        surf.blit(glow, (self.x - 100, self.y - 100), special_flags=pygame.BLEND_PREMULTIPLIED)

# ---------------------------------------
# Efecto: AGUA (ondas sinusoidales + burbujas)
# ---------------------------------------
class WaterEffect:
    def __init__(self):
        self.t = 0
        self.ps = ParticleSystem()

    def update(self):
        self.t += 1
        # Burbujas ascendentes desde la parte baja
        for _ in range(3):
            x = random.randint(0, WIDTH)
            y = random.randint(HEIGHT - 60, HEIGHT - 10)
            vx = random.uniform(-0.2, 0.2)
            vy = random.uniform(-0.8, -0.3)
            r = random.randint(2, 5)
            life = random.randint(60, 120)
            color = (160, 200, 255)
            self.ps.emit(Particle(x, y, vx, vy, r, life, color))
        self.ps.update()

    def draw(self, surf):
        # Fondo azul agua
        surf.fill((12, 30, 60))
        # Ondas horizontales (desplazamiento sinusoidal de líneas)
        rows = 30
        for i in range(rows):
            y = int(HEIGHT * (i / rows))
            amp = 8 + 6 * math.sin(self.t * 0.02 + i * 0.4)
            x_offset = int(amp * math.sin(self.t * 0.05 + i))
            color = (20, 60 + i*3, 110 + i*4)
            pygame.draw.rect(surf, color, (x_offset, y, WIDTH, 4))
        # Burbujas
        self.ps.draw(surf)

# ---------------------------------------
# Efecto: RAYO (zigzag entre puntos con glow)
# ---------------------------------------
class LightningEffect:
    def __init__(self):
        self.start = (WIDTH//4, HEIGHT//4)
        self.end = (WIDTH*3//4, HEIGHT*3//4)
        self.segments = []
        self.rebuild()

    def rebuild(self):
        # Generar puntos intermedios con desviación aleatoria
        points = [self.start]
        segments = 20
        for i in range(1, segments):
            t = i / segments
            x = lerp(self.start[0], self.end[0], t) + random.randint(-12, 12)
            y = lerp(self.start[1], self.end[1], t) + random.randint(-12, 12)
            points.append((x, y))
        points.append(self.end)
        self.segments = points

    def set_endpoints(self, start, end):
        self.start = start
        self.end = end
        self.rebuild()

    def update(self):
        # Pequeño “flicker”: ajustar algunos puntos
        for i in range(1, len(self.segments)-1):
            x, y = self.segments[i]
            self.segments[i] = (x + random.randint(-1, 1), y + random.randint(-1, 1))

    def draw(self, surf):
        # Glow: varias pasadas de líneas más gruesas y translúcidas
        glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for w, a in [(8, 40), (5, 80), (3, 130)]:
            pygame.draw.lines(glow_surf, (100, 180, 255, a), False, self.segments, w)
        surf.blit(glow_surf, (0, 0))
        # Núcleo del rayo (blanco)
        pygame.draw.lines(surf, (255, 255, 255), False, self.segments, 2)

# ---------------------------------------
# Efecto: HUMO/NIEBLA (partículas + manto)
# ---------------------------------------
class SmokeEffect:
    def __init__(self, x, y):
        self.ps = ParticleSystem()
        self.x, self.y = x, y
        self.cloud = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.t = 0

    def update(self):
        self.t += 1
        # Emitir humo
        for _ in range(6):
            ang = random.uniform(-math.pi, -math.pi/6)
            speed = random.uniform(0.3, 1.0)
            vx = math.cos(ang) * speed * 0.4
            vy = math.sin(ang) * speed * 0.4
            r = random.randint(6, 12)
            life = random.randint(90, 150)
            gray = random.randint(120, 200)
            self.ps.emit(Particle(self.x, self.y, vx, vy, r, life, (gray, gray, gray)))

        self.ps.update()

    def draw(self, surf):
        # Niebla suave desplazándose
        fog = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        alpha = 40 + int(20 * math.sin(self.t * 0.01))
        fog.fill((200, 200, 200, alpha))
        surf.blit(fog, (int(10 * math.sin(self.t * 0.003)), 0))
        # Humo ascendente
        self.ps.draw(surf)

# ---------------------------------------
# Efecto: LINTERNA (máscara de luz)
# ---------------------------------------
class FlashlightEffect:
    def __init__(self):
        self.radius = 120

    def update(self):
        pass

    def draw(self, surf, mouse_pos):
        # Capa oscura
        darkness = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        darkness.fill((0, 0, 0, 210))
        # “Recortar” un círculo de luz en la posición del mouse
        pygame.draw.circle(darkness, (0, 0, 0, 0), mouse_pos, self.radius)
        surf.blit(darkness, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        # Aureola sutil
        halo = pygame.Surface((self.radius*2+2, self.radius*2+2), pygame.SRCALPHA)
        for i in range(self.radius, 0, -8):
            a = int(80 * (1 - i/self.radius))
            pygame.draw.circle(halo, (255, 255, 200, a), (self.radius, self.radius), i)
        surf.blit(halo, (mouse_pos[0]-self.radius, mouse_pos[1]-self.radius), special_flags=pygame.BLEND_PREMULTIPLIED)

# ---------------------------------------
# Escena / manejador de efectos
# ---------------------------------------
class EffectsDemo:
    def __init__(self):
        self.mode = E_FUEGO
        self.fire = FireEffect(WIDTH//2, HEIGHT-80)
        self.water = WaterEffect()
        self.lightning = LightningEffect()
        self.smoke = SmokeEffect(WIDTH//2, HEIGHT-60)
        self.flashlight = FlashlightEffect()
        self.bg_stars = self._make_starry_bg()

    def _make_starry_bg(self):
        # Fondo con estrellas para que luz/niebla se noten
        surf = pygame.Surface((WIDTH, HEIGHT))
        surf.fill(BG_COLOR)
        for _ in range(180):
            x = random.randint(0, WIDTH-1)
            y = random.randint(0, HEIGHT-1)
            c = random.randint(180, 255)
            surf.set_at((x, y), (c, c, c))
        return surf

    def set_mode(self, m):
        self.mode = m
        if m == E_RAYO:
            self.lightning.rebuild()

    def update(self, mouse_pos):
        if self.mode == E_AGUA:
            self.water.update()
        elif self.mode == E_FUEGO:
            self.fire.update()
        elif self.mode == E_RAYO:
            self.lightning.update()
        elif self.mode == E_HUMO:
            self.smoke.update()
        elif self.mode == E_LINTERNA:
            self.flashlight.update()

    def draw(self, surf, mouse_pos):
        surf.blit(self.bg_stars, (0, 0))

        if self.mode == E_AGUA:
            self.water.draw(surf)
        elif self.mode == E_FUEGO:
            self.fire.draw(surf)
        elif self.mode == E_RAYO:
            self.lightning.draw(surf)
        elif self.mode == E_HUMO:
            self.smoke.draw(surf)
        elif self.mode == E_LINTERNA:
            # fondo simple para resaltar la luz
            pygame.draw.rect(surf, (40, 60, 80), (0, 0, WIDTH, HEIGHT))
            self.flashlight.draw(surf, mouse_pos)

        # Texto HUD
        self._draw_hud(surf)

    def _draw_hud(self, surf):
        font = pygame.font.SysFont("consolas", 18)
        mode_text = {
            E_AGUA: "AGUA (1)  |  Ondas + Burbujas",
            E_FUEGO: "FUEGO (2) | Partículas ascendentes",
            E_RAYO: "RAYO (3)  | Espacio: regenerar | Arrastra con mouse",
            E_HUMO: "HUMO (4)  | Niebla + humo",
            E_LINTERNA: "LINTERNA (5) | Luz recorta oscuridad con mouse"
        }[self.mode]
        info = "1:Agua  2:Fuego  3:Rayo  4:Humo  5:Linterna  |  ESC: salir"
        t1 = font.render(mode_text, True, (230, 230, 230))
        t2 = font.render(info, True, (190, 200, 210))
        surf.blit(t1, (14, 12))
        surf.blit(t2, (14, 34))

# ---------------------------------------
# Bucle principal
# ---------------------------------------
def main():
    demo = EffectsDemo()
    dragging = False  # para mover el rayo

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    demo.set_mode(E_AGUA)
                elif event.key == pygame.K_2:
                    demo.set_mode(E_FUEGO)
                elif event.key == pygame.K_3:
                    demo.set_mode(E_RAYO)
                elif event.key == pygame.K_4:
                    demo.set_mode(E_HUMO)
                elif event.key == pygame.K_5:
                    demo.set_mode(E_LINTERNA)
                elif event.key == pygame.K_SPACE and demo.mode == E_RAYO:
                    demo.lightning.rebuild()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if demo.mode == E_RAYO:
                    dragging = True
                    demo.lightning.set_endpoints(demo.lightning.start, mouse_pos)

            elif event.type == pygame.MOUSEBUTTONUP:
                if demo.mode == E_RAYO:
                    dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if demo.mode == E_RAYO and dragging:
                    demo.lightning.set_endpoints(demo.lightning.start, mouse_pos)

        # Actualizar origen de efectos vinculados a mouse
        if demo.mode == E_FUEGO:
            demo.fire.x, demo.fire.y = mouse_pos[0], HEIGHT - 60
        if demo.mode == E_HUMO:
            demo.smoke.x, demo.smoke.y = mouse_pos[0], HEIGHT - 60

        demo.update(mouse_pos)

        # Render
        screen.fill(BG_COLOR)
        demo.draw(screen, mouse_pos)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
