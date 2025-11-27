import random

import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Red Ball Movement")

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

radius = 25
x = WIDTH // 2
y = HEIGHT // 2
step = 20
N = 3
speed = 10

clock = pygame.time.Clock()

enemies = []

for i in range(N):
    en = pygame.draw.rect(screen, BLACK, pygame.Rect(WIDTH, random.randint(1, HEIGHT), 50, 40))

    enemies.append(en)

def move_enemies(enemies):
    for enemy in enemies:
        enemy.x -= speed
        pygame.draw.rect(screen, BLACK, pygame.Rect(enemy.x, enemy.y, 50, 40))

    print(enemies)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    #for enemy in enemies:

    keys = pygame.key.get_pressed()

    if keys[pygame.K_UP] and y - radius >= 0:
        if y - radius - step >= 0:
            y -= step
        else:
            y -= y - radius
    if keys[pygame.K_DOWN] and y + radius + step <= HEIGHT:
        if y + radius + step <= HEIGHT:
            y += step
        else:
            y += radius
    if keys[pygame.K_LEFT] and x - radius >= 0:
        if x - radius - step >= 0:
            x -= step
        else:
            x -= x - radius
    if keys[pygame.K_RIGHT] and x + radius <= WIDTH:
        if x + radius + step <= WIDTH:
            x += step
        else:
            x += radius


    move_enemies(enemies)
    screen.fill(WHITE)
    pygame.draw.circle(screen, RED, (x, y), radius)
    pygame.display.flip()

    clock.tick(30)
