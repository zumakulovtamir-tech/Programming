import pygame
import sys
import random
import math
import os

pygame.init()
pygame.mixer.init() 

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Гонки по серпантину 🏎️〰️")
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

# --- НОВОЕ: Машина теперь может двигаться по Y ---
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

ai_cars = [] 
last_enemy_spawn = 0

police_cars = [] 
last_police_spawn = 0
police_spawn_delay = 8000 

health = 100
score = 0
damage_timer = 0
invincibility_timer = 0 

def reset_game():
    global player_x, player_y, player_speed, ai_cars, police_cars, health, score, last_enemy_spawn, last_police_spawn, game_state, damage_timer, invincibility_timer, road_offset, nitro, is_boosting, particles, paused, bonuses, oil_timer, health_packs, last_health_spawn
    global phase1, phase2, phase3
    
    player_x = 375
    player_y = 450 # Возвращаем машину вниз при старте
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
        
        # --- НОВОЕ: УПРАВЛЕНИЕ ДВИЖЕНИЕМ МАШИНЫ (ВВЕРХ/ВНИЗ) ---
        if keys[pygame.K_UP]:
            player_y -= 6 # Машина едет вверх по экрану
        if keys[pygame.K_DOWN]:
            player_y += 6 # Машина едет вниз по экрану
            
        # Не даем машине улететь за экран
        if player_y < 100:
            player_y = 100
        if player_y > 500:
            player_y = 500
            
        player_rect.y = player_y

        # --- НОВОЕ: СКОРОСТЬ ЗАВИСИТ ОТ ПОЛОЖЕНИЯ НА ЭКРАНЕ ---
        # Чем выше машина (меньше Y), тем она быстрее
        base_speed = 15 - ((player_y - 100) / 400) * 12 
        
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and nitro > 0:
            is_boosting = True
            player_speed = base_speed + 10 # Огромный буст от нитро
            nitro -= 1.5 
        else:
            is_boosting = False
            player_speed = base_speed # Обычная скорость
            if nitro < 100:
                nitro += 0.2 
        
        # Дорога крутится со скоростью машины
        road_offset += player_speed

        # Границы дороги для машины
        center_at_player = get_road_center(player_y)
        left_border = center_at_player - (ROAD_WIDTH // 2)
        right_border = center_at_player + (ROAD_WIDTH // 2)

        if keys[pygame.K_LEFT] and player_x > left_border:
            player_x -= 7
        if keys[pygame.K_RIGHT] and player_x < right_border - player_rect.width: 
            player_x += 7

        if oil_timer > current_time:
            player_x += random.randint(-5, 5)

        player_rect.x = player_x

        # Частицы
        if is_boosting or player_speed > 10:
            for _ in range(2):
                particles.append({
                    "x": player_x + random.randint(10, 40), 
                    "y": player_y + 80, 
                    "size": random.randint(4, 8), 
                    "speed": player_speed * 0.5 
                })

        for p in particles[:]:
            p["y"] += p["speed"]
            p["size"] -= 0.2 
            if p["size"] <= 0 or p["y"] > 600:
                particles.remove(p)

        # --- АПТЕЧКИ ---
        if current_time - last_health_spawn > 6000 and len(health_packs) == 0:
            lane_offset = random.randint(-100, 100)
            hp_rect = pygame.Rect(0, -100, 40, 40)
            health_packs.append({"rect": hp_rect, "lane": lane_offset})
            last_health_spawn = current_time

        for hp_data in health_packs[:]:
            hp_rect = hp_data["rect"]
            hp_rect.y += player_speed 
            center_at_hp = get_road_center(hp_rect.y)
            hp_rect.x = center_at_hp + hp_data["lane"] - 20

            if hp_rect.y > 600:
                health_packs.remove(hp_data)
            if hp_rect.colliderect(player_rect):
                health = min(100, health + 30) 
                health_packs.remove(hp_data)
                if sounds_loaded: heal_sound.play()

        # --- БОНУСЫ ---
        if current_time - last_bonus_spawn > 3500 and len(bonuses) == 0:
            b_type = random.choice(["shield", "lightning", "oil"])
            lane_offset = random.randint(-100, 100)
            b_rect = pygame.Rect(0, -100, 40, 40)
            bonuses.append({"rect": b_rect, "lane": lane_offset, "type": b_type})
            last_bonus_spawn = current_time

        for b_data in bonuses[:]:
            b_rect = b_data["rect"]
            b_rect.y += player_speed 
            center_at_b = get_road_center(b_rect.y)
            b_rect.x = center_at_b + b_data["lane"] - 20

            if b_rect.y > 600:
                bonuses.remove(b_data)
            if b_rect.colliderect(player_rect):
                if b_data["type"] == "shield":
                    invincibility_timer = current_time + 5000 
                elif b_data["type"] == "lightning":
                    nitro = 100 
                elif b_data["type"] == "oil":
                    oil_timer = current_time + 1500 
                    player_speed = max(2, player_speed - 3) 
                if sounds_loaded: heal_sound.play()
                bonuses.remove(b_data)

        # --- ВРАГИ ---
        spawn_delay = 2500 if difficulty == "easy" else (1800 if difficulty == "normal" else 1000)
        if current_time - last_enemy_spawn > spawn_delay:
            ai_speed = random.uniform(3, 12) 
            lane_offset = random.randint(-100, 100) 
            car_rect = pygame.Rect(0, -100, 50, 80) 
            ai_cars.append({"rect": car_rect, "speed": ai_speed, "lane": lane_offset})
            last_enemy_spawn = current_time

        for car_data in ai_cars[:]:
            car = car_data["rect"]
            ai_speed = car_data["speed"]
            relative_speed = player_speed - ai_speed
            car.y += relative_speed

            center_at_car = get_road_center(car.y)
            car.x = center_at_car + car_data["lane"] - 25 

            if car.y < -100:
                ai_cars.remove(car_data)
                score += 10
                if sounds_loaded: score_sound.play()
            elif car.y > 600:
                ai_cars.remove(car_data)

            if invincibility_timer < current_time:
                if car.colliderect(player_rect):
                    health -= 25 
                    ai_cars.remove(car_data)
                    damage_timer = current_time
                    invincibility_timer = current_time + 1000 
                    if sounds_loaded: crash_sound.play()
                    
                    if health <= 0:
                        game_state = "game_over"
                        if sounds_loaded: pygame.mixer.music.stop()
                        if score > high_score:
                            high_score = score
                            with open("highscore.txt", "w") as f:
                                f.write(str(high_score))

        # --- ПОЛИЦИЯ ---
        if current_time - last_police_spawn > police_spawn_delay:
            p_rect = pygame.Rect(random.randint(200, 500), -150, 50, 80) 
            police_cars.append({"rect": p_rect, "speed": random.uniform(8, 14)})
            last_police_spawn = current_time

        for p_data in police_cars[:]:
            p_car = p_data["rect"]
            p_speed = p_data["speed"]
            relative_speed = player_speed - p_speed
            p_car.y += relative_speed

            if p_car.y < player_y - 50: 
                if p_car.x < player_x: p_car.x += 2.5 
                elif p_car.x > player_x: p_car.x -= 2.5 

            if p_car.y < -150:
                police_cars.remove(p_data)
                score += 20 
                if sounds_loaded: score_sound.play()
            elif p_car.y > 600:
                police_cars.remove(p_data)

            if invincibility_timer < current_time:
                if p_car.colliderect(player_rect):
                    health -= 40 
                    police_cars.remove(p_data)
                    damage_timer = current_time
                    invincibility_timer = current_time + 1500 
                    if sounds_loaded: crash_sound.play()
                    
                    if health <= 0:
                        game_state = "game_over"
                        if sounds_loaded: pygame.mixer.music.stop()
                        if score > high_score:
                            high_score = score
                            with open("highscore.txt", "w") as f:
                                f.write(str(high_score))

    # --- РИСОВАНИЕ ---
    screen.fill((34, 139, 34)) 

    if game_state == "menu":
        title = big_font.render("ВЫБЕРИ СЛОЖНОСТЬ", True, (255, 255, 255))
        screen.blit(title, (150, 150))
        mouse_pos = pygame.mouse.get_pos()
        
        color_easy = (0, 200, 0) if btn_easy.collidepoint(mouse_pos) else (0, 100, 0)
        pygame.draw.rect(screen, color_easy, btn_easy, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), btn_easy, 2, border_radius=10)
        screen.blit(font.render("ЛЕГКО", True, (255, 255, 255)), (btn_easy.x + 60, btn_easy.y + 12))

        color_normal = (200, 200, 0) if btn_normal.collidepoint(mouse_pos) else (100, 100, 0)
        pygame.draw.rect(screen, color_normal, btn_normal, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), btn_normal, 2, border_radius=10)
        screen.blit(font.render("НОРМАЛЬНО", True, (255, 255, 255)), (btn_normal.x + 35, btn_normal.y + 12))

        color_hard = (200, 0, 0) if btn_hard.collidepoint(mouse_pos) else (100, 0, 0)
        pygame.draw.rect(screen, color_hard, btn_hard, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), btn_hard, 2, border_radius=10)
        screen.blit(font.render("СЛОЖНО", True, (255, 255, 255)), (btn_hard.x + 50, btn_hard.y + 12))

        screen.blit(font.render(f"ТВОЙ РЕКОРД: {high_score}", True, (255, 255, 255)), (280, 480))

    elif game_state in ["playing", "game_over"]:
        for y in range(0, 600, 10):
            center = get_road_center(y)
            pygame.draw.rect(screen, (100, 100, 100), (center - ROAD_WIDTH//2, y, ROAD_WIDTH, 10))
            if y % 40 == 0:
                pygame.draw.rect(screen, (255, 255, 255), (center - 5, y, 10, 20))

        for p in particles:
            pygame.draw.circle(screen, (255, 150, 0), (int(p["x"]), int(p["y"])), int(p["size"]))

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

        for car_data in ai_cars:
            pygame.draw.rect(screen, (255, 0, 0), car_data["rect"])

        for p_data in police_cars:
            p_car = p_data["rect"]
            pygame.draw.rect(screen, (0, 0, 150), p_car) 
            if (current_time // 200) % 2 == 0:
                pygame.draw.circle(screen, (255, 0, 0), (p_car.x + 10, p_car.y + 10), 6)
                pygame.draw.circle(screen, (0, 0, 255), (p_car.x + 40, p_car.y + 10), 6) 
            else:
                pygame.draw.circle(screen, (0, 0, 255), (p_car.x + 10, p_car.y + 10), 6)
                pygame.draw.circle(screen, (255, 0, 0), (p_car.x + 40, p_car.y + 10), 6) 

        if current_time - damage_timer < 100 or invincibility_timer < current_time:
            pygame.draw.rect(screen, (0, 0, 255), player_rect)
        
        if invincibility_timer > current_time:
            pygame.draw.circle(screen, (0, 255, 255), (player_rect.x + 25, player_rect.y + 40), 40, 3) 

        # Интерфейс
        pygame.draw.rect(screen, (255, 0, 0), (10, 10, 200, 30))
        pygame.draw.rect(screen, (0, 255, 0), (10, 10, 2 * health, 30))
        screen.blit(font.render(f"HP", True, (0, 0, 0)), (15, 15))

        pygame.draw.rect(screen, (50, 50, 50), (10, 50, 200, 20)) 
        nitro_color = (255, 0, 0) if is_boosting else (0, 150, 255)
        pygame.draw.rect(screen, nitro_color, (10, 50, 2 * nitro, 20))
        screen.blit(font.render(f"NITRO", True, (255, 255, 255)), (15, 52))

        score_text = font.render(f"Очки: {score}", True, (255, 255, 255))
        record_text = font.render(f"Рекорд: {high_score}", True, (200, 200, 200))
        speed_text = font.render(f"Скорость: {int(player_speed * 20)} км/ч", True, (255, 255, 255))
        
        screen.blit(score_text, (10, 80))
        screen.blit(speed_text, (10, 120))
        screen.blit(record_text, (10, 160))

        if oil_timer > current_time:
            oil_warning = font.render("МАСЛО! МАШИНУ ЗАНОСИТ!", True, (255, 100, 0))
            screen.blit(oil_warning, (250, 200))

        if game_state == "game_over":
            end_text = big_font.render("МАШИНА РАЗБИТА 💥", True, (255, 0, 0))
            restart_text = font.render("Нажми ПРОБЕЛ, чтобы выйти в меню", True, (255, 255, 0))
            screen.blit(end_text, (180, 200))
            screen.blit(restart_text, (200, 280))

        if paused:
            pause_surface = pygame.Surface((800, 600))
            pause_surface.set_alpha(150) 
            pause_surface.fill((0, 0, 0))
            screen.blit(pause_surface, (0, 0))
            
            pause_text = big_font.render("ПАУЗА", True, (255, 255, 255))
            resume_text = font.render("Нажми P, чтобы продолжить", True, (255, 255, 0))
            screen.blit(pause_text, (330, 250))
            screen.blit(resume_text, (260, 330))

    pygame.display.update()