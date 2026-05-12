import pygame
import sys
from constants import *
from game_state import GameState
from entities import *

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Battle City AI - Tank 1990")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 20)

def draw_grid(screen, state):
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            tile = state.grid[y][x]
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            
            if tile == BRICK:
                pygame.draw.rect(screen, COLOR_BRICK, rect)
                pygame.draw.rect(screen, (0,0,0), rect, 1) # border
            elif tile == STEEL:
                pygame.draw.rect(screen, COLOR_STEEL, rect)
                pygame.draw.rect(screen, (0,0,0), rect, 1)
            elif tile == WATER:
                pygame.draw.rect(screen, COLOR_WATER, rect)
            elif tile == FOREST:
                pygame.draw.rect(screen, COLOR_FOREST, rect)
            elif tile == EAGLE:
                color = COLOR_EAGLE if state.eagle_alive else COLOR_EAGLE_DEAD
                pygame.draw.rect(screen, color, rect)

def draw_entities(screen, state):
    # Draw Player
    if state.player.hp > 0:
        rect = pygame.Rect(state.player.x * TILE_SIZE, state.player.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, state.player.color, rect)
        # Draw direction indicator
        dir_x = state.player.x * TILE_SIZE + TILE_SIZE//2 + state.player.direction[0] * TILE_SIZE//2
        dir_y = state.player.y * TILE_SIZE + TILE_SIZE//2 + state.player.direction[1] * TILE_SIZE//2
        pygame.draw.line(screen, (255,255,255), rect.center, (dir_x, dir_y), 3)

    # Draw Enemies
    for e in state.enemies:
        rect = pygame.Rect(e.x * TILE_SIZE, e.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, e.color, rect)
        if isinstance(e, ArmorTank) and e.hp < e.max_hp:
            # Flash if damaged
            pygame.draw.rect(screen, (255,255,0), rect, 2)
            
        dir_x = e.x * TILE_SIZE + TILE_SIZE//2 + e.direction[0] * TILE_SIZE//2
        dir_y = e.y * TILE_SIZE + TILE_SIZE//2 + e.direction[1] * TILE_SIZE//2
        pygame.draw.line(screen, (0,0,0), rect.center, (dir_x, dir_y), 3)

    # Draw Bullets
    for b in state.bullets:
        center = (int((b.x + 0.5) * TILE_SIZE), int((b.y + 0.5) * TILE_SIZE))
        pygame.draw.circle(screen, COLOR_BULLET, center, TILE_SIZE // 4)

def draw_ui(screen, state):
    ui_rect = pygame.Rect(GRID_SIZE * TILE_SIZE, 0, 200, SCREEN_HEIGHT)
    pygame.draw.rect(screen, (50, 50, 50), ui_rect)
    
    texts = [
        f"Level: {state.level}",
        f"Lives: {state.player.lives}",
        f"Kills: {state.kills}",
        f"Enemies Left: {len(state.enemy_pool) + len(state.enemies)}",
        "",
        "Controls:",
        "Arrows: Move",
        "Space: Shoot"
    ]
    
    if state.game_over:
        texts.extend(["", "GAME OVER!"])
    elif state.win:
        texts.extend(["", "LEVEL CLEAR!"])
        
    for i, t in enumerate(texts):
        surface = font.render(t, True, COLOR_UI_TEXT)
        screen.blit(surface, (GRID_SIZE * TILE_SIZE + 10, 10 + i * 30))

def select_level_menu(screen, font):
    font_large = pygame.font.SysFont('Arial', 40)
    while True:
        screen.fill(COLOR_BG)
        title = font_large.render("BATTLE CITY AI", True, (255, 255, 0))
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 200))
        
        prompt = font.render("Press 1, 2, or 3 to select Level", True, (255, 255, 255))
        screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, 300))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1 or event.key == pygame.K_KP1: return 1
                if event.key == pygame.K_2 or event.key == pygame.K_KP2: return 2
                if event.key == pygame.K_3 or event.key == pygame.K_KP3: return 3

def main():
    level = select_level_menu(screen, font)
    state = GameState()
    state.load_enemy_pool(level)
    
    last_tick_time = pygame.time.get_ticks()

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    state.shoot_bullet(state.player, 'player')

        # Handle continuous key presses for movement
        keys = pygame.key.get_pressed()
        move_dir = None
        if keys[pygame.K_UP]: move_dir = UP
        elif keys[pygame.K_DOWN]: move_dir = DOWN
        elif keys[pygame.K_LEFT]: move_dir = LEFT
        elif keys[pygame.K_RIGHT]: move_dir = RIGHT
        
        if move_dir and not state.game_over and not state.win:
            state.move_tank(state.player, move_dir)

        # Game Tick Logic
        if current_time - last_tick_time >= TICK_RATE_MS:
            state.update_ai_decisions()
            state.update_tick()
            last_tick_time = current_time

        # Rendering
        screen.fill(COLOR_BG)
        draw_grid(screen, state)
        draw_entities(screen, state)
        draw_ui(screen, state)
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
