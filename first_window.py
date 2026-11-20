import pygame
import sys
import random
import math
import os

pygame.init()
pygame.mixer.init() 

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Гонки по серпантину (ООП) 🏎️〰️")
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 64)
clock = pygame.time.Clock()

# --- ЗВУКИ ---
try:
    crash_sound = pygame.mixer.Sound("crash.wav")
    score_sound = pygame.mixer.Sound("score.wav")
    heal_sound = pygame.mixer.Sound("score.wav") 
    pygame.mixer.music.load("bg_music.ogg")
    sounds_loaded = True
except:
    sounds_loaded = False

# --- РЕКОРД ---
if os.path.exists("highscore.txt"):
    with open("highscore.txt", "r") as f:
        high_score = int(f.read())
else:
    high_score = 0

# --- НАСТРОЙКИ ---
game_state = "menu" 
difficulty = "normal" 
ROAD_WIDTH = 300
road_offset = 0 
paused = False 

phase1 = random.uniform(0, math.pi * 2)
phase2 = random.uniform(0, math.pi * 2)
phase3 = random.uniform(0, math.pi * 2)

btn_easy = pygame.Rect(300, 250, 200, 50)
btn_normal = pygame.Rect(300, 320, 200, 50)
btn_hard = pygame.Rect(300, 390, 200, 50)

def get_road_center(y):
    t = y - road_offset
    wave1 = math.sin(0.002 * t + phase1) * 100
    wave2 = math.sin(0.005 * t + phase2) * 50
    wave3 = math.sin(0.011 * t + phase3) * 20
    return 400 + wave1 + wave2 + wave3

# ==========================================
# --- НОВОЕ: КЛАССЫ МАШИН (ООП) ---
# ==========================================
class Car:
    def __init__(self, lane, speed):
        self.rect = pygame.Rect(0, -100, 50, 80) # Создаем рамку машины
        self.lane = lane                         # Смещение от центра дороги
        self.speed = speed                       # Скорость машины
        
    def update(self, player_speed):
        # Вычисляем, как быстро машина едет по экрану
        relative_speed = player_speed - self.speed
        self.rect.y += relative_speed
        
        # Машина едет по извилистой дороге
        center_at_car = get_road_center(self.rect.y)
        self.rect.x = center_at_car + self.lane - 25

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 0, 0), self.rect) # Красная машина

class PoliceCar(Car): # Наследуем всёViewController все свойства от Car
    def __init__(self, lane, speed):
        super().__init__(lane, speed) # Вызываем конструктор родителя
        self.rect = pygame.Rect(random.randint(200, 500), -150, 50, 80)
        
    def update(self, player_speed, player_x, player_y):
        relative_speed = player_speed - self.speed
        self.rect.y += relative_speed
        
        # Полиция преследует игрока по X
        if self.rect.y < player_y - 50:
            if self.rect.x < player_x: self.rect.x += 2.5
            elif self.rect.x > player_x: self.rect.x -= 2.5
            
    def draw(self, surface):
        pygame.draw.rect(surface, (0, 0, 150), self.rect) # Синяя машина
        # Рисуем мигалки
        current_time = pygame.time.get_ticks()
        if (current_time // 200) % 2 == 0:
            pygame.draw.circle(surface, (255, 0, 0), (self.rect.x + 10, self.rect.y + 10), 6)
            pygame.draw.circle(surface, (0, 0, 255), (self.rect.x + 40, self.rect.y + 10), 6) 
        else:
            pygame.draw.circle(surface, (0, 0, 255), (self.rect.x + 10, self.rect.y + 10), 6)
            pygame.draw.circle(surface, (255, 0, 0), (self.rect.x + 40, self.rect.y + 10), 6) 
# ==========================================

# --- ИГРОК ---
player_x = 375
player_y = 450 
player_speed = 5 
player_rect = pygame.Rect(player_x, player_y, 50, 80)

nitro = 100 
is_boosting = False
particles = [] 

bonuses = []
last_bonus_spawn = 0
health_packs = [] 
last_health_spawn = 0
oil_timer = 0 

# Теперь это списки объектов, а не словарей!
ai_cars = [] 
police_cars = []
last_enemy_spawn = 0
last_police_spawn = 0

health = 100
score = 0
damage_timer = 0
invincibility_timer = 0 

def reset_game():
    global player_x, player_y, player_speed, ai_cars, police_cars, health, score, last_enemy_spawn, last_police_spawn, game_state, damage_timer, invincibility_timer, road_offset, nitro, is_boosting, particles, paused, bonuses, oil_timer, health_packs, last_health_spawn
    global phase1, phase2, phase3
    
    player_x = 375
    player_y = 450
    player_speed = 5
    player_rect.x = player_x
    player_rect.y = player_y
    ai_cars.clear()
    police_cars.clear()
    particles.clear()
    bonuses.clear()
    health_packs.clear()
    health = 100
    score = 0
    nitro = 100
    is_boosting = False
    paused = False
    oil_timer = 0
    road_offset = 0
    last_enemy_spawn = pygame.time.get_ticks()
    last_police_spawn = pygame.time.get_ticks()
    last_bonus_spawn = pygame.time.get_ticks()
    last_health_spawn = pygame.time.get_ticks()
    damage_timer = 0
    invincibility_timer = 0
    
    phase1 = random.uniform(0, math.pi * 2)
    phase2 = random.uniform(0, math.pi * 2)
    phase3 = random.uniform(0, math.pi * 2)
    
    game_state = "playing"
    if sounds_loaded: pygame.mixer.music.play(-1)

while True:
    clock.tick(60)
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if game_state == "playing" and event.key == pygame.K_p:
                paused = not paused

            if game_state == "game_over" and event.key == pygame.K_SPACE:
                if sounds_loaded: pygame.mixer.music.stop()
                game_state = "menu"

        if game_state == "menu" and event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: 
                mouse_pos = pygame.mouse.get_pos()
                if btn_easy.collidepoint(mouse_pos):
                    difficulty = "easy"
                    reset_game()
                elif btn_normal.collidepoint(mouse_pos):
                    difficulty = "normal"
                    reset_game()
                elif btn_hard.collidepoint(mouse_pos):
                    difficulty = "hard"
                    reset_game()

    if game_state == "playing" and not paused:
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_UP]: player_y -= 6 
        if keys[pygame.K_DOWN]: player_y += 6 
            
        if player_y < 100: player_y = 100
        if player_y > 500: player_y = 500
        player_rect.y = player_y

        base_speed = 15 - ((player_y - 100) / 400) * 12 
        
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and nitro > 0:
            is_boosting = True
            player_speed = base_speed + 10 
            nitro -= 1.5 
        else:
            is_boosting = False
            player_speed = base_speed 
            if nitro < 100: nitro += 0.2 
        
        road_offset += player_speed

        center_at_player = get_road_center(player_y)
        left_border = center_at_player - (ROAD_WIDTH // 2)
        right_border = center_at_player + (ROAD_WIDTH // 2)

        if keys[pygame.K_LEFT] and player_x > left_border: player_x -= 7
        if keys[pygame.K_RIGHT] and player_x < right_border - player_rect.width: player_x += 7

        if oil_timer > current_time: player_x += random.randint(-5, 5)
        player_rect.x = player_x

        if is_boosting or player_speed > 10:
            for _ in range(2):
                particles.append({"x": player_x + random.randint(10, 40), "y": player_y + 80, "size": random.randint(4, 8), "speed": player_speed * 0.5})

        for p in particles[:]:
            p["y"] += p["speed"]
            p["size"] -= 0.2 
            if p["size"] <= 0 or p["y"] > 600: particles.remove(p)

        # --- АПТЕЧКИ ---
        if current_time - last_health_spawn > 6000 and len(health_packs) == 0:
            health_packs.append({"rect": pygame.Rect(0, -100, 40, 40), "lane": random.randint(-100, 100)})
            last_health_spawn = current_time

        for hp_data in health_packs[:]:
            hp_rect = hp_data["rect"]
            hp_rect.y += player_speed 
            hp_rect.x = get_road_center(hp_rect.y) + hp_data["lane"] - 20

            if hp_rect.y > 600: health_packs.remove(hp_data)
            if hp_rect.colliderect(player_rect):
                health = min(100, health + 30) 
                health_packs.remove(hp_data)
                if sounds_loaded: heal_sound.play()

        # --- БОНУСЫ ---
        if current_time - last_bonus_spawn > 3500 and len(bonuses) == 0:
            bonuses.append({"rect": pygame.Rect(0, -100, 40, 40), "lane": random.randint(-100, 100), "type": random.choice(["shield", "lightning", "oil"])})
            last_bonus_spawn = current_time

        for b_data in bonuses[:]:
            b_rect = b_data["rect"]
            b_rect.y += player_speed 
            b_rect.x = get_road_center(b_rect.y) + b_data["lane"] - 20

            if b_rect.y > 600: bonuses.remove(b_data)
            if b_rect.colliderect(player_rect):
                if b_data["type"] == "shield": invincibility_timer = current_time + 5000 
                elif b_data["type"] == "lightning": nitro = 100 
                elif b_data["type"] == "oil": 
                    oil_timer = current_time + 1500 
                    player_speed = max(2, player_speed - 3) 
                if sounds_loaded: heal_sound.play()
                bonuses.remove(b_data)

        # --- ОБЫЧНЫЕ ВРАГИ (Используем класс!) ---
        spawn_delay = 2500 if difficulty == "easy" else (1800 if difficulty == "normal" else 1000)
        if current_time - last_enemy_spawn > spawn_delay:
            # Создаем ОБЪЕКТ машины!
            new_car = Car(lane=random.randint(-100, 100), speed=random.uniform(3, 12))
            ai_cars.append(new_car)
            last_enemy_spawn = current_time

        for car in ai_cars[:]:
            car.update(player_speed) # Вызываем метод update у объекта
            if car.rect.y < -100:
                ai_cars.remove(car)
                score += 10
                if sounds_loaded: score_sound.play()
            elif car.rect.y > 600:
                ai_cars.remove(car)

            if invincibility_timer < current_time and car.rect.colliderect(player_rect):
                health -= 25 
                ai_cars.remove(car)
                damage_timer = current_time
                invincibility_timer = current_time + 1000 
                if sounds_loaded: crash_sound.play()
                if health <= 0:
                    game_state = "game_over"
                    if sounds_loaded: pygame.mixer.music.stop()
                    if score > high_score:
                        high_score = score
                        with open("highscore.txt", "w") as f: f.write(str(high_score))

        # --- ПОЛИЦИЯ (Используем класс PoliceCar!) ---
        if current_time - last_police_spawn > 8000:
            new_police = PoliceCar(lane=0, speed=random.uniform(8, 14))
            police_cars.append(new_police)
            last_police_spawn = current_time

        for p_car in police_cars[:]:
            p_car.update(player_speed, player_x, player_y) # У полиции свой update
            if p_car.rect.y < -150:
                police_cars.remove(p_car)
                score += 20 
                if sounds_loaded: score_sound.play()
            elif p_car.rect.y > 600:
                police_cars.remove(p_car)

            if invincibility_timer < current_time and p_car.rect.colliderect(player_rect):
                health -= 40 
                police_cars.remove(p_car)
                damage_timer = current_time
                invincibility_timer = current_time + 1500 
                if sounds_loaded: crash_sound.play()
                if health <= 0:
                    game_state = "game_over"
                    if sounds_loaded: pygame.mixer.music.stop()
                    if score > high_score:
                        high_score = score
                        with open("highscore.txt", "w") as f: f.write(str(high_score))

    # --- РИСОВАНИЕ ---
    screen.fill((34, 139, 34)) 

    if game_state == "menu":
        screen.blit(big_font.render("ВЫБЕРИ СЛОЖНОСТЬ", True, (255, 255, 255)), (150, 150))
        mouse_pos = pygame.mouse.get_pos()
        
        c_easy = (0, 200, 0) if btn_easy.collidepoint(mouse_pos) else (0, 100, 0)
        pygame.draw.rect(screen, c_easy, btn_easy, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), btn_easy, 2, border_radius=10)
        screen.blit(font.render("ЛЕГКО", True, (255, 255, 255)), (btn_easy.x + 60, btn_easy.y + 12))

        c_normal = (200, 200, 0) if btn_normal.collidepoint(mouse_pos) else (100, 100, 0)
        pygame.draw.rect(screen, c_normal, btn_normal, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), btn_normal, 2, border_radius=10)
        screen.blit(font.render("НОРМАЛЬНО", True, (255, 255, 255)), (btn_normal.x + 35, btn_normal.y + 12))

        c_hard = (200, 0, 0) if btn_hard.collidepoint(mouse_pos) else (100, 0, 0)
        pygame.draw.rect(screen, c_hard, btn_hard, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), btn_hard, 2, border_radius=10)
        screen.blit(font.render("СЛОЖНО", True, (255, 255, 255)), (btn_hard.x + 50, btn_hard.y + 12))

        screen.blit(font.render(f"ТВОЙ РЕКОРД: {high_score}", True, (255, 255, 255)), (280, 480))

    elif game_state in ["playing", "game_over"]:
        for y in range(0, 600, 10):
            center = get_road_center(y)
            pygame.draw.rect(screen, (100, 100, 100), (center - ROAD_WIDTH//2, y, ROAD_WIDTH, 10))
            if y % 40 == 0: pygame.draw.rect(screen, (255, 255, 255), (center - 5, y, 10, 20))

        for p in particles: pygame.draw.circle(screen, (255, 150, 0), (int(p["x"]), int(p["y"])), int(p["size"]))

        for hp_data in health_packs:
            hp_rect = hp_data["rect"]
            pygame.draw.rect(screen, (0, 255, 0), hp_rect)
            pygame.draw.line(screen, (255, 255, 255), (hp_rect.x + 20, hp_rect.y + 10), (hp_rect.x + 20, hp_rect.y + 30), 4)
            pygame.draw.line(screen, (255, 255, 255), (hp_rect.x + 10, hp_rect.y + 20), (hp_rect.x + 30, hp_rect.y + 20), 4)

        for b_data in bonuses:
            b_rect = b_data["rect"]
            if b_data["type"] == "shield": pygame.draw.circle(screen, (0, 150, 255), (b_rect.x + 20, b_rect.y + 20), 20) 
            elif b_data["type"] == "lightning": pygame.draw.circle(screen, (255, 255, 0), (b_rect.x + 20, b_rect.y + 20), 20) 
            elif b_data["type"] == "oil": pygame.draw.ellipse(screen, (0, 0, 0), b_rect) 

        # --- РИСОВАНИЕ МАШИН ИЗ КЛАССОВ ---
        for car in ai_cars:
            car.draw(screen) # Вызываем метод draw!
            
        for p_car in police_cars:
            p_car.draw(screen) # Полиция сама знает, как себя рисовать

        if current_time - damage_timer < 100 or invincibility_timer < current_time:
            pygame.draw.rect(screen, (0, 0, 255), player_rect)
        if invincibility_timer > current_time:
            pygame.draw.circle(screen, (0, 255, 255), (player_rect.x + 25, player_rect.y + 40), 40, 3) 

        # Интерфейс (без изменений)
        pygame.draw.rect(screen, (255, 0, 0), (10, 10, 200, 30))
        pygame.draw.rect(screen, (0, 255, 0), (10, 10, 2 * health, 30))
        screen.blit(font.render(f"HP", True, (0, 0, 0)), (15, 15))

        pygame.draw.rect(screen, (50, 50, 50), (10, 50, 200, 20)) 
        nitro_color = (255, 0, 0) if is_boosting else (0, 150, 255)
        pygame.draw.rect(screen, nitro_color, (10, 50, 2 * nitro, 20))
        screen.blit(font.render(f"NITRO", True, (255, 255, 255)), (15, 52))

        screen.blit(font.render(f"Очки: {score}", True, (255, 255, 255)), (10, 80))
        screen.blit(font.render(f"Скорость: {int(player_speed * 20)} км/ч", True, (255, 255, 255)), (10, 120))
        screen.blit(font.render(f"Рекорд: {high_score}", True, (200, 200, 200)), (10, 160))

        if oil_timer > current_time:
            screen.blit(font.render("МАСЛО! МАШИНУ ЗАНОСИТ!", True, (255, 100, 0)), (250, 200))

        if game_state == "game_over":
            screen.blit(big_font.render("МАШИНА РАЗБИТА 💥", True, (255, 0, 0)), (180, 200))
            screen.blit(font.render("Нажми ПРОБЕЛ, чтобы выйти в меню", True, (255, 255, 0)), (200, 280))

        if paused:
            pause_surface = pygame.Surface((800, 600))
            pause_surface.set_alpha(150) 
            pause_surface.fill((0, 0, 0))
            screen.blit(pause_surface, (0, 0))
            screen.blit(big_font.render("ПАУЗА", True, (255, 255, 255)), (330, 250))
            screen.blit(font.render("Нажми P, чтобы продолжить", True, (255, 255, 0)), (260, 330))

    pygame.display.update()
