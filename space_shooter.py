import pygame
import sys
import random

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Космический Шутер 🚀")
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 64)
clock = pygame.time.Clock()

# Начальные настройки игрока
player_x = 375
player_y = 500
speed = 6
player_rect = pygame.Rect(player_x, player_y, 50, 50)

bullets = [] 
enemies = []

last_shot_time = 0
shoot_delay = 300 

last_enemy_spawn = 0
enemy_spawn_delay = 800

score = 0
game_over = False

while True:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
                
            # --- НОВОЕ 1: Логика перезапуска игры ---
            if game_over and event.key == pygame.K_SPACE:
                # Возвращаем игрока на исходную позицию
                player_x = 375
                player_y = 500
                player_rect.x = player_x
                player_rect.y = player_y
                
                # Очищаем списки (удаляем все пули и врагов с экрана)
                bullets.clear()
                enemies.clear()
                
                # Обнуляем счет и снимаем статус проигрыша
                score = 0
                game_over = False
                
                # Сбрасываем таймеры, чтобы враги не напали мгновенно
                last_shot_time = pygame.time.get_ticks()
                last_enemy_spawn = pygame.time.get_ticks()

    if not game_over:
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= speed
        if keys[pygame.K_RIGHT] and player_x < 750:
            player_x += speed
            
        current_time = pygame.time.get_ticks()
        
        if keys[pygame.K_SPACE] and current_time - last_shot_time > shoot_delay:
            bullet = pygame.Rect(player_x + 22, player_y, 6, 15)
            bullets.append(bullet)
            last_shot_time = current_time

        for bullet in bullets[:]:
            bullet.y -= 10
            if bullet.y < 0:
                bullets.remove(bullet)

        if current_time - last_enemy_spawn > enemy_spawn_delay:
            enemy_x = random.randint(0, 750)
            enemy = pygame.Rect(enemy_x, -50, 40, 40) 
            enemies.append(enemy)
            last_enemy_spawn = current_time
            
        for enemy in enemies[:]:
            enemy.y += 3 
            
            if enemy.y > 600:
                game_over = True
                
            if enemy.colliderect(player_rect):
                game_over = True

            for bullet in bullets[:]:
                if enemy.colliderect(bullet):
                    score += 1
                    if enemy in enemies:
                        enemies.remove(enemy)
                    if bullet in bullets:
                        bullets.remove(bullet)
                    break 

    # --- РИСОВАНИЕ ---
    screen.fill((10, 10, 30)) 
    
    pygame.draw.rect(screen, (0, 255, 0), player_rect)
    
    for bullet in bullets:
        pygame.draw.rect(screen, (255, 255, 255), bullet)
        
    for enemy in enemies:
        pygame.draw.rect(screen, (255, 0, 0), enemy)

    score_text = font.render(f"Сбито врагов: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    # --- НОВОЕ 2: Обновленный экран проигрыша с подсказками ---
    if game_over:
        end_text = big_font.render("КОРАБЛЬ УНИЧТОЖЕН 💀", True, (255, 0, 0))
        
        # Подсказка для перезапуска
        restart_text = font.render("Нажми ПРОБЕЛ, чтобы начать заново", True, (255, 255, 0))
        # Подсказка для выхода
        exit_text = font.render("Нажми ESC, чтобы выйти", True, (200, 200, 200))
        
        screen.blit(end_text, (150, 250))
        screen.blit(restart_text, (230, 330))
        screen.blit(exit_text, (290, 380))

    pygame.display.update()