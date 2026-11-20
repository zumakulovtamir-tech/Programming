import pygame
import sys
import random
import os # Нужно для сохранения рекорда

pygame.init()
screen = pygame.display.set_mode((400, 600)) 
pygame.display.set_caption("Flappy Bird (Красивая версия) 🐦✨")
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 64)
clock = pygame.time.Clock()

# --- РЕКОРД ---
if os.path.exists("flappy_highscore.txt"):
    with open("flappy_highscore.txt", "r") as f:
        high_score = int(f.read())
else:
    high_score = 0

# --- КЛАСС ОБЛАКА (ДЛЯ ФОНА) ---
class Cloud:
    def __init__(self):
        self.x = random.randint(0, 400)
        self.y = random.randint(50, 300)
        self.speed = random.uniform(0.5, 1.5)
        self.width = random.randint(60, 100)
        self.height = random.randint(30, 50)

    def update(self):
        self.x -= self.speed # Облака летят медленно
        if self.x < -self.width:
            self.x = 400 + self.width
            self.y = random.randint(50, 300)

    def draw(self, surface):
        pygame.draw.ellipse(surface, (255, 255, 255), (self.x, self.y, self.width, self.height))

# --- КЛАСС ПТИЦЫ ---
class Bird:
    def __init__(self):
        self.x = 100
        self.y = 300
        self.rect = pygame.Rect(self.x, self.y, 40, 30)
        self.velocity = 0 
        self.gravity = 0.5 
        self.jump_strength = -8 
        
        # Для анимации крыльев
        self.wing_timer = 0
        self.wing_up = True

    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity
        self.rect.y = int(self.y)
        
        # Анимация взмаха крыльев
        self.wing_timer += 1
        if self.wing_timer > 10: # Меняем положение крыла каждые 10 кадров
            self.wing_up = not self.wing_up
            self.wing_timer = 0

    def jump(self):
        self.velocity = self.jump_strength

    def draw(self, surface):
        # Тело птички
        pygame.draw.ellipse(surface, (255, 255, 0), self.rect)
        # Клюв
        pygame.draw.polygon(surface, (255, 150, 0), [(self.x + 40, self.y + 15), (self.x + 50, self.y + 20), (self.x + 40, self.y + 25)])
        # Глаз
        pygame.draw.circle(surface, (0, 0, 0), (self.x + 30, self.y + 10), 4)
        
        # Крылышко (анимация)
        if self.wing_up:
            pygame.draw.ellipse(surface, (255, 200, 0), (self.x + 5, self.y + 10, 20, 15))
        else:
            pygame.draw.ellipse(surface, (255, 200, 0), (self.x + 5, self.y + 5, 20, 15))

# --- КЛАСС ТРУБЫ ---
class Pipe:
    def __init__(self, x, gap_y):
        self.x = x
        self.gap_y = gap_y 
        self.gap_size = 150 
        self.speed = 3 
        
        self.top_rect = pygame.Rect(self.x, 0, 60, self.gap_y)
        self.bottom_rect = pygame.Rect(self.x, self.gap_y + self.gap_size, 60, 600 - (self.gap_y + self.gap_size))

    def update(self):
        self.x -= self.speed
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def draw(self, surface):
        # Верхняя труба
        pygame.draw.rect(surface, (0, 200, 0), self.top_rect)
        # Блик на верхней трубе (объем)
        pygame.draw.rect(surface, (0, 255, 0), (self.top_rect.x + 5, self.top_rect.y, 20, self.top_rect.height))
        # Обводка
        pygame.draw.rect(surface, (0, 100, 0), self.top_rect, 3)

        # Нижняя труба
        pygame.draw.rect(surface, (0, 200, 0), self.bottom_rect)
        pygame.draw.rect(surface, (0, 255, 0), (self.bottom_rect.x + 5, self.bottom_rect.y, 20, self.bottom_rect.height))
        pygame.draw.rect(surface, (0, 100, 0), self.bottom_rect, 3)

# --- ИНИЦИАЛИЗАЦИЯ ---
bird = Bird()
pipes = []
clouds = [Cloud() for _ in range(4)] # Создаем 4 облака
last_pipe_time = 0
score = 0
game_over = False
ground_x = 0 # Для движения земли

def reset_game():
    global bird, pipes, score, game_over, last_pipe_time, ground_x
    bird = Bird()
    pipes.clear()
    score = 0
    game_over = False
    ground_x = 0
    last_pipe_time = pygame.time.get_ticks()

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
                
            if event.key == pygame.K_SPACE:
                if game_over:
                    reset_game()
                else:
                    bird.jump()

    if not game_over:
        bird.update()
        
        # Движение земли (визуальный эффект)
        ground_x -= 3
        if ground_x <= -40:
            ground_x = 0

        # Обновление облаков
        for cloud in clouds:
            cloud.update()

        # Появление труб
        if current_time - last_pipe_time > 1500:
            gap_y = random.randint(100, 400)
            pipes.append(Pipe(400, gap_y))
            last_pipe_time = current_time

        # Логика труб
        for pipe in pipes[:]:
            pipe.update()
            if pipe.x < -60:
                pipes.remove(pipe)
                score += 1

            if bird.rect.colliderect(pipe.top_rect) or bird.rect.colliderect(pipe.bottom_rect):
                game_over = True
                # --- СОХРАНЕНИЕ РЕКОРДА ---
                if score > high_score:
                    high_score = score
                    with open("flappy_highscore.txt", "w") as f:
                        f.write(str(high_score))

        # Столкновение с землей
        if bird.rect.y > 570 or bird.rect.y < 0:
            game_over = True
            # --- СОХРАНЕНИЕ РЕКОРДА ---
            if score > high_score:
                high_score = score
                with open("flappy_highscore.txt", "w") as f:
                    f.write(str(high_score))

    # --- РИСОВАНИЕ ---
    # Небо
    screen.fill((135, 206, 235)) 

    # Облака (рисуются на фоне)
    for cloud in clouds:
        cloud.draw(screen)

    # Трубы
    for pipe in pipes:
        pipe.draw(screen)

    # Птичка
    bird.draw(screen)

    # Земля с текстурой
    pygame.draw.rect(screen, (100, 150, 50), (0, 570, 400, 30)) # Основной цвет
    for i in range(-40, 400, 40): # Рисуем полоски травы, которые двигаются
        pygame.draw.rect(screen, (80, 120, 40), (ground_x + i, 570, 20, 30))

    # Счет и Рекорд
    score_text = big_font.render(str(score), True, (255, 255, 255))
    high_score_text = font.render(f"Рекорд: {high_score}", True, (255, 255, 255))
    
    screen.blit(score_text, (200 - score_text.get_width() // 2, 50))
    screen.blit(high_score_text, (10, 10))

    # Экран проигрыша
    if game_over:
        # Затемняем экран
        overlay = pygame.Surface((400, 600))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        end_text = big_font.render("ИГРА ОКОНЧЕНА", True, (255, 50, 50))
        restart_text = font.render("Нажми ПРОБЕЛ, чтобы играть снова", True, (255, 255, 255))
        final_score = font.render(f"Твой счет: {score}", True, (255, 255, 0))
        
        screen.blit(end_text, (200 - end_text.get_width() // 2, 200))
        screen.blit(final_score, (200 - final_score.get_width() // 2, 270))
        screen.blit(restart_text, (200 - restart_text.get_width() // 2, 330))

    pygame.display.update()