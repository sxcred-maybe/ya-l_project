import pygame
from random import randint
import os
import sys

pygame.init()
WIDTH, HEIGHT = 800, 600
FPS, TILE = 60, 32
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


def load_image(name):
    fullname = os.path.join(name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


bullets, objects = [], []
imgBrick = pygame.image.load('images/block_brick.png')
imgTanks = [pygame.image.load('images/tank2.png'),
            pygame.image.load('images/tank1.png')]
imgBang = pygame.image.load('images/bang3.png')
settings = [[0, -1], [1, 0], [0, 1], [-1, 0]]


class Interface:
    def __init__(self):
        pass

    def update(self):
        pass

    def draw(self):
        i = 0
        for obj in objects:
            if obj.type == 'tank':
                pygame.draw.rect(window, obj.color, (5 + i * 70, 5, 22, 22))
                text = pygame.font.Font(None, 30).render(str(obj.hp), 1, obj.color)
                rect = text.get_rect(center=(5 + i * 70 + 32, 5 + 11))
                window.blit(text, rect)
                i += 1


class Tank:
    def __init__(self, color, px, py, direct, keyList):
        objects.append(self)
        self.type = 'tank'
        self.color = color
        self.rect = pygame.Rect(px, py, TILE, TILE)
        self.direct = direct
        self.moveSpeed = 2
        self.hp = 3
        self.shotTime = 0
        self.bulletSpeed = 5
        self.bulletDamage = 1

        self.keyLEFT, self.keyRIGHT = keyList[0], keyList[1]
        self.keyUP, self.keyDOWN = keyList[2], keyList[3]
        self.keySHOT = keyList[4]

        if color == 'blue':
            self.rank = 0
        else:
            self.rank = 1
        self.image = pygame.transform.rotate(imgTanks[self.rank], -self.direct * 90)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        self.image = pygame.transform.rotate(imgTanks[self.rank], -self.direct * 90)
        self.image = pygame.transform.scale(self.image, (self.image.get_width() - 5, self.image.get_height() - 5))
        self.rect = self.image.get_rect(center=self.rect.center)

        old_x, old_y = self.rect.topleft

        if keys[self.keyLEFT]:
            self.rect.x -= self.moveSpeed
            self.direct = 3
        elif keys[self.keyRIGHT]:
            self.rect.x += self.moveSpeed
            self.direct = 1
        elif keys[self.keyUP]:
            self.rect.y -= self.moveSpeed
            self.direct = 0
        elif keys[self.keyDOWN]:
            self.rect.y += self.moveSpeed
            self.direct = 2

        for obj in objects:
            if obj != self and obj.type == 'block' and self.rect.colliderect(obj.rect):
                self.rect.topleft = old_x, old_y

        if keys[self.keySHOT] and self.shotTime == 0:
            dx = settings[self.direct][0] * self.bulletSpeed
            dy = settings[self.direct][1] * self.bulletSpeed
            Bullet(self, self.rect.centerx, self.rect.centery, dx, dy, self.bulletDamage)
            self.shotTime = 60

        if self.shotTime > 0:
            self.shotTime -= 1

    def draw(self):
        window.blit(self.image, self.rect)

    def damage(self, value):
        self.hp -= value
        if self.hp <= 0:
            objects.remove(self)
            print(self.color, 'dead')


class Bullet:
    def __init__(self, parent, px, py, dx, dy, damage):
        bullets.append(self)
        self.parent = parent
        self.px, self.py = px, py
        self.dx, self.dy = dx, dy
        self.damage = damage

    def update(self):
        self.px += self.dx
        self.py += self.dy

        if self.px < 0 or self.px > WIDTH or self.py < 0 or self.py > HEIGHT:
            bullets.remove(self)
        else:
            for obj in objects:
                if obj != self.parent and obj.type != 'bang' and obj.rect.collidepoint(self.px, self.py):
                    obj.damage(self.damage)
                    bullets.remove(self)
                    Bang(self.px, self.py)
                    break

    def draw(self):
        pygame.draw.circle(window, 'yellow', (self.px, self.py), 2)


class Bang:
    def __init__(self, px, py):
        objects.append(self)
        self.type = 'bang'

        self.px, self.py = px, py
        self.frame = 0

    def update(self):
        self.frame += 0.2
        if self.frame >= 3:
            objects.remove(self)

    def draw(self):
        image = imgBang
        rect = image.get_rect(center=(self.px, self.py))
        window.blit(image, rect)


class Block:
    def __init__(self, px, py, size):
        objects.append(self)
        self.type = 'block'

        self.rect = pygame.Rect(px, py, size, size)
        self.hp = 1

    def update(self):
        pass

    def draw(self):
        window.blit(imgBrick, self.rect)

    def damage(self, value):
        self.hp -= value
        if self.hp <= 0:
            objects.remove(self)


Tank('blue', 100, 275, 0,
     (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE))
Tank('red', 650, 275, 0,
     (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_KP_ENTER))
interface = Interface()


def load_level(self, filename='map_lvl.txt'):
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def start_screen():
    intro_text = ["TANKS DUEL"]
    fon = pygame.transform.scale(load_image('images/fon.jpg'), (WIDTH, HEIGHT))
    window.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        window.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


for i in range(50):
    while True:
        x = randint(0, WIDTH // TILE - 1) * TILE
        y = randint(1, HEIGHT // TILE - 1) * TILE
        rect = pygame.Rect(x, y, TILE, TILE)
        fined = False
        for obj in objects:
            if rect.colliderect(obj.rect):
                fined = True
        if not fined:
            break

    Block(x, y, TILE)

start_screen()
play = True
while play:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            play = False

    keys = pygame.key.get_pressed()

    for bullet in bullets:
        bullet.update()
    for obj in objects:
        obj.update()
    interface.update()

    window.fill('black')
    for bullet in bullets:
        bullet.draw()
    for obj in objects:
        obj.draw()
    interface.draw()

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
