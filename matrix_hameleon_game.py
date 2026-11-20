import pygame
import sys
import random

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Матрица: Хамелеон ⏳🦎")
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 64)
clock = pygame.time.Clock()

# Цвета: Красный, Зеленый, Синий
COLORS = [(255, 50, 50), (50, 255, 50), (50, 150, 255)]
COLOR_NAMES = ["КРАСНЫЙ", "ЗЕЛЕНЫЙ", "СИНИЙ"]

# --- КЛАСС ИГРОКА ---
class Player:
    def __init__(self):
        self.x = 100
        self.y = 500
        self.width = 40
        self.height = 40
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        self.color_index = 0 # Начинаем с красного
        self.vy = 0
        self.gravity = 0.6
        self.speed = 5
        
        self.hp = 3
        self.invincible_timer = 0

    def update(self, keys, current_time):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
            
        if self.x < 0: self.x = 0
        if self.x > 800 - self.width: self.x = 800 - self.width

        self.vy += self.gravity
        self.y += self.vy

        if self.y >= 560: 
            self.y = 560
            self.vy = 0
        elif self.y <= 0: 
            self.y = 0
            self.vy = 0
            
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def flip_gravity(self):
        self.gravity *= -1
        self.vy = 0

    def draw(self, surface, current_time):
        # --- ИСПРАВЛЕНИЕ БАГА С МИГАНИЕМ ---
        # Теперь игрок мигает ТОЛЬКО если таймер неуязвимости больше текущего времени
        if current_time < self.invincible_timer and (current_time // 100) % 2 == 0:
            return 

        pygame.draw.rect(surface, COLORS[self.color_index], self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 3) 

# --- КЛАСС ВРАГА ---
class Enemy:
    def __init__(self):
        self.width = 30
        self.height = 30
        self.x = 800
        self.y = random.randint(50, 500)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.color_index = random.randint(0, 2)
        self.speed = random.randint(4, 8)

    def update(self, time_is_moving):
        if time_is_moving:
            self.x -= self.speed
            self.rect.x = int(self.x)

    def draw(self, surface):
        pygame.draw.rect(surface, COLORS[self.color_index], self.rect)
        pygame.draw.circle(surface, (0, 0, 0), (self.rect.x + 15, self.rect.y + 15), 5)

# --- ИНИЦИАЛИЗАЦИЯ ---
player = Player()
enemies = []
last_spawn_time = 0
score = 0
game_over = False

def reset_game():
    global player, enemies, score, game_over, last_spawn_time
    player = Player()
    enemies.clear()
    score = 0
    game_over = False
    last_spawn_time = pygame.time.get_ticks()

while True:
    clock.tick(60)
    current_time = pygame.time.get_ticks()
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
                
            if game_over and event.key == pygame.K_SPACE:
                reset_game()

            if not game_over:
                # --- ИСПРАВЛЕНИЕ КЛАВИШ ---
                # Теперь ловим и обычные цифры, и цифры на NumPad
                if event.key in [pygame.K_1, pygame.K_KP1]: 
                    player.color_index = 0
                    print("Цвет изменен на: КРАСНЫЙ")
                if event.key in [pygame.K_2, pygame.K_KP2]: 
                    player.color_index = 1
                    print("Цвет изменен на: ЗЕЛЕНЫЙ")
                if event.key in [pygame.K_3, pygame.K_KP3]: 
                    player.color_index = 2
                    print("Цвет изменен на: СИНИЙ")
                
                if event.key == pygame.K_SPACE:
                    player.flip_gravity()

    if not game_over:
        is_moving = keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_a] or keys[pygame.K_d]
        
        player.update(keys, current_time)

        if current_time - last_spawn_time > 1000: 
            enemies.append(Enemy())
            last_spawn_time = current_time

        for enemy in enemies[:]:
            enemy.update(is_moving)

            if enemy.x < -50:
                enemies.remove(enemy)

            if enemy.rect.colliderect(player.rect) and current_time > player.invincible_timer:
                if enemy.color_index == player.color_index:
                    enemies.remove(enemy)
                    score += 10
                else:
                    enemies.remove(enemy)
                    player.hp -= 1
                    player.invincible_timer = current_time + 1000 
                    print("Ты получил урон! Осталось HP:", player.hp)
                    
                    if player.hp <= 0:
                        game_over = True

    # --- РИСОВАНИЕ ---
    screen.fill((20, 20, 30))

    pygame.draw.rect(screen, (50, 50, 70), (0, 560, 800, 40))
    pygame.draw.rect(screen, (50, 50, 70), (0, 0, 800, 10))

    for enemy in enemies:
        enemy.draw(screen)

    player.draw(screen, current_time)

    for i in range(player.hp):
        pygame.draw.circle(screen, (255, 0, 0), (20 + i*30, 30), 10)

    score_text = font.render(f"Очки: {score}", True, (255, 255, 255))
    screen.blit(score_text, (650, 20))

    color_text = font.render(f"Твой цвет: {COLOR_NAMES[player.color_index]} (1,2,3)", True, COLORS[player.color_index])
    screen.blit(color_text, (10, 70))

    if is_moving and not game_over:
        time_text = font.render("ВРЕМЯ ИДЕТ!", True, (255, 50, 50))
    else:
        time_text = font.render("ВРЕМЯ СТОП", True, (50, 255, 50))
    screen.blit(time_text, (10, 110))

    if game_over:
        overlay = pygame.Surface((800, 600))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        end_text = big_font.render("СИСТЕМА ВЗЛОМАНА", True, (255, 0, 0))
        restart_text = font.render("Нажми ПРОБЕЛ, чтобы перезапустить", True, (255, 255, 255))
        
        screen.blit(end_text, (150, 200))
        screen.blit(restart_text, (200, 300))

    pygame.display.update()