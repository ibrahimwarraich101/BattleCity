import pygame
import sys
import random
import math
from constants import *
from game_map import GameMap
from tank import PlayerTank, EnemyTank, BossTank
from hud import HUD

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Battle City Clone - Tank 1990")
        self.clock = pygame.time.Clock()
        self.hud = HUD()
        
        self.level = 1
        self.debug_mode = False
        self.game_state = "MENU"
        self.splash_timer = 0
        self.boss_log_saved = False
        self.total_stats = []
        self.player = None
        self.enemies = []
        self.bullets = []
        self.frame_count = 0
        self.game_map = None
        self.selected_option = 0

    def reset_level(self):
        self.game_map = GameMap(self.level)
        
        if self.level == 'B':
            self.player = PlayerTank(BOSS_PLAYER_SPAWN[0], BOSS_PLAYER_SPAWN[1])
            self.enemies = [BossTank(BOSS_SPAWN[0], BOSS_SPAWN[1])]
            self.enemy_pool = []
            self.game_state = "BOSS_FIGHT"
        else:
            self.player = PlayerTank(PLAYER_SPAWN[0], PLAYER_SPAWN[1])
            self.enemies = []
            self.game_state = "PLAYING"
        
        self.bullets = []
        self.frame_count = 0
        self.spawn_timer = 0
        self.spawn_index = 0
        self.enemies_killed = 0
        self.boss_log_saved = False
        
        # Level Configs
        if self.level == 1:
            self.enemy_pool = ['basic']*7 + ['fast']*5
        elif self.level == 2:
            self.enemy_pool = ['fast']*4 + ['armor']*3 + ['power']*2
        elif self.level == 'B':
            self.enemy_pool = []
        else:
            self.enemy_pool = ['basic']*10

    def handle_input(self):
        if self.game_state not in ["PLAYING", "BOSS_FIGHT"] or self.player is None:
            return

        keys = pygame.key.get_pressed()
        
        if self.player.active:
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.player.move(UP, self.game_map, self.enemies + [self.player])
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.player.move(DOWN, self.game_map, self.enemies + [self.player])
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player.move(LEFT, self.game_map, self.enemies + [self.player])
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player.move(RIGHT, self.game_map, self.enemies + [self.player])
            
            if keys[pygame.K_SPACE]:
                self.player.shoot(self.bullets)

    def update(self):
        if self.game_state == "SPLASH":
            self.splash_timer -= 1
            if self.splash_timer <= 0:
                self.reset_level()
            return

        if self.game_state not in ["PLAYING", "BOSS_FIGHT"]:
            return

        if not self.player.active and self.player.lives > 0:
            self.player.respawn_timer -= 1
            if self.player.respawn_timer <= 0:
                self.player.respawn()
                if self.level == 'B': # In Boss fight, reposition
                    self.player.x, self.player.y = BOSS_PLAYER_SPAWN
        
        self.player.update()

        # Update Enemy AI
        for enemy in self.enemies:
            if enemy.active:
                enemy.update_ai(self.game_map, self.enemies + [self.player], self.bullets, self.player)

        # Update Bullets
        for bullet in self.bullets[:]:
            if bullet.active:
                bullet.update(self.game_map, self.enemies + [self.player], self.bullets, self.frame_count)
            else:
                self.bullets.remove(bullet)

        # Remove dead enemies
        for enemy in self.enemies[:]:
            if not enemy.active:
                self.enemies.remove(enemy)
                self.enemies_killed += 1

        # Spawn Enemies
        if not self.debug_mode:
            if len(self.enemies) < MAX_ACTIVE_ENEMIES and len(self.enemy_pool) > 0:
                self.spawn_timer += 1
                if self.spawn_timer >= FPS * 2:
                    spawn_pos = ENEMY_SPAWNS[self.spawn_index]
                    # Check distance to player
                    if abs(spawn_pos[0] - self.player.x) + abs(spawn_pos[1] - self.player.y) > 10:
                        type = self.enemy_pool.pop(0)
                        self.enemies.append(EnemyTank(spawn_pos[0], spawn_pos[1], type))
                        self.spawn_index = (self.spawn_index + 1) % len(ENEMY_SPAWNS)
                        self.spawn_timer = 0

        # Win/Lose Check
        if self.level != 'B':
            if self.game_map.get_tile(EAGLE_POS[0], EAGLE_POS[1]) != EAGLE:
                self.game_state = "GAME_OVER"
            elif self.player.lives <= 0 and not self.player.active:
                self.game_state = "GAME_OVER"
            elif len(self.enemy_pool) == 0 and len(self.enemies) == 0:
                self.game_state = "STAGE_CLEAR"
        else:
            # Boss Level specific win/lose
            if self.player.lives <= 0 and not self.player.active:
                self.game_state = "GAME_OVER"
            elif len(self.enemies) == 0:
                self.game_state = "VICTORY"
                if not self.boss_log_saved:
                    self.save_boss_stats()

    def save_boss_stats(self):
        with open("boss_stats.txt", "w") as f:
            f.write("BATTLE CITY - BOSS FIGHT LOG\n")
            f.write("----------------------------\n")
            for i, stats in enumerate(self.total_stats):
                speedup = stats[0]/stats[1] if stats[1] > 0 else 1.0
                f.write(f"Tick {i}: Raw={stats[0]}, Pruned={stats[1]}, Speedup={speedup:.2f}x\n")
        self.boss_log_saved = True

    def start_splash(self, level):
        self.level = level
        self.game_state = "SPLASH"
        self.splash_timer = STAGE_SPLASH_TIME

    def toggle_debug(self):
        self.debug_mode = not self.debug_mode
        if self.debug_mode:
            # Setup Debug Scene
            self.level = 1
            self.reset_level()
            # Place a wall across path
            # Direct path from spawn (0,0) to Eagle (12,24)
            for y in range(5, 10):
                self.game_map.set_tile(6, y, BRICK)
            # Add detour obstacles to force path
            # Clear 6-tile detour
            
            # Spawn one of each
            self.enemies = []
            self.enemies.append(EnemyTank(0, 0, 'basic'))
            self.enemies.append(EnemyTank(12, 0, 'fast'))
            self.enemies.append(EnemyTank(24, 0, 'armor'))
            self.enemy_pool = []
        else:
            self.reset_level()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if self.game_state == "MENU":
                        if event.key == pygame.K_UP or event.key == pygame.K_w:
                            self.selected_option = (self.selected_option - 1) % 3
                        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            self.selected_option = (self.selected_option + 1) % 3
                        elif event.key == pygame.K_RETURN:
                            levels = [1, 2, 'B']
                            self.start_splash(levels[self.selected_option])
                        elif event.key == pygame.K_1: self.start_splash(1)
                        elif event.key == pygame.K_2: self.start_splash(2)
                        elif event.key == pygame.K_b: self.start_splash('B')
                    elif event.key == pygame.K_d:
                        self.toggle_debug()
                    elif self.game_state in ["STAGE_CLEAR", "GAME_OVER", "VICTORY"]:
                        if self.game_state == "STAGE_CLEAR":
                            if self.level == 1: self.start_splash(2)
                            elif self.level == 2: self.start_splash('B')
                            else: self.game_state = "MENU"
                        else:
                            self.game_state = "MENU"

            self.handle_input()
            self.update()
            
            self.screen.fill(COLOR_BG)
            
            if self.game_state == "MENU":
                self.draw_menu()
            elif self.game_state == "SPLASH":
                self.draw_splash()
            else:
                self.game_map.draw(self.screen, self.frame_count)
                
                # Draw Player (only if active)
                if self.player.active:
                    self.player.draw(self.screen)
                
                boss_stats = (0, 0)
                for enemy in self.enemies:
                    enemy.draw(self.screen)
                    if enemy.tank_type == 'boss':
                        boss_stats = enemy.last_stats
                        if self.game_state == "BOSS_FIGHT":
                            self.total_stats.append(boss_stats)
                
                for bullet in self.bullets:
                    bullet.draw(self.screen)

                # Forest Layer (Top)
                for y in range(GRID_SIZE):
                    for x in range(GRID_SIZE):
                        if self.game_map.grid[y][x] == FOREST:
                            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                            pygame.draw.rect(self.screen, COLOR_FOREST, rect)

                self.hud.draw(self.screen, self.player.lives, len(self.enemy_pool) + len(self.enemies), self.level, self.game_state, boss_stats)
            
            if self.debug_mode and self.game_state not in ["MENU", "SPLASH"]:
                self.draw_debug()

            pygame.display.flip()
            self.clock.tick(FPS)
            self.frame_count += 1

    def draw_menu(self):
        # Draw dynamic background
        self.draw_menu_background()
        
        # Overlay for better text readability
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 15, 180))
        self.screen.blit(overlay, (0, 0))

        time = pygame.time.get_ticks()
        pulse = (math.sin(time * 0.004) + 1) / 2
        float_y = math.sin(time * 0.002) * 10
        
        # Title with double glow and floating effect
        font_title = pygame.font.SysFont(['Outfit', 'Segoe UI', 'Arial'], 90, bold=True)
        title_text = "BATTLE CITY"
        title_center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + float_y)
        
        # Outer glow
        glow_alpha = int(50 + 50 * pulse)
        glow_surf = font_title.render(title_text, True, (255, 255, 0))
        glow_surf.set_alpha(glow_alpha)
        for dx, dy in [(-4,-4), (4,-4), (-4,4), (4,4), (0,-6), (0,6)]:
            self.screen.blit(glow_surf, glow_surf.get_rect(center=(title_center[0]+dx, title_center[1]+dy)))
            
        # Inner glow
        title_surf = font_title.render(title_text, True, (255, 255, 50))
        self.screen.blit(title_surf, title_surf.get_rect(center=title_center))
        
        # Subtitle
        font_sub = pygame.font.SysFont(['Outfit', 'Segoe UI', 'Arial'], 28)
        subtitle = font_sub.render("AI ADAPTIVE COMBAT", True, (160, 170, 200))
        sub_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, title_center[1] + 80))
        self.screen.blit(subtitle, sub_rect)
        
        # Options with selection cursor
        options = ["STAGE 1 - TRAINING", "STAGE 2 - ADVANCED", "BOSS - ULTIMATE TEST"]
        font_opt = pygame.font.SysFont(['Outfit', 'Segoe UI', 'Arial'], 26)
        
        start_y = SCREEN_HEIGHT // 2 + 60
        for i, opt in enumerate(options):
            is_selected = (i == self.selected_option)
            color = (255, 255, 255) if is_selected else (120, 130, 160)
            
            if is_selected:
                # Selected text with pulse
                s_pulse = (math.sin(time * 0.01) + 1) / 2
                color = (255, 200 + 55 * s_pulse, 100 + 155 * s_pulse)
                
                # Draw cursor (tank)
                self.draw_cursor(SCREEN_WIDTH // 2 - 180, start_y + i * 45)
            
            opt_surf = font_opt.render(opt, True, color)
            self.screen.blit(opt_surf, opt_surf.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * 45)))

        # Footer prompt
        prompt_alpha = int(100 + 155 * pulse)
        font_p = pygame.font.SysFont(['Outfit', 'Segoe UI', 'Arial'], 18)
        prompt = font_p.render("USE ARROW KEYS & ENTER TO START", True, (200, 200, 200))
        prompt.set_alpha(prompt_alpha)
        self.screen.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)))

    def draw_menu_background(self):
        # Draw a moving grid/pattern of tiles
        time = pygame.time.get_ticks() * 0.02
        for y in range(-1, GRID_SIZE + 1):
            for x in range(-1, GRID_SIZE + 1):
                off_x = (time % TILE_SIZE)
                off_y = (time * 0.5 % TILE_SIZE)
                rect = pygame.Rect(x * TILE_SIZE + off_x, y * TILE_SIZE + off_y, TILE_SIZE, TILE_SIZE)
                
                # Alternate pattern
                if (x + y) % 5 == 0:
                    pygame.draw.rect(self.screen, (20, 20, 30), rect)
                    pygame.draw.rect(self.screen, (30, 30, 45), rect, 1)

    def draw_cursor(self, x, y):
        # Draw a small player tank as a cursor
        size = 24
        rect = pygame.Rect(x - size//2, y - size//2, size, size)
        pygame.draw.rect(self.screen, COLOR_PLAYER, rect, border_radius=4)
        pygame.draw.line(self.screen, (0, 0, 0), (x, y), (x + 12, y), 3) # Barrel
        
    def draw_splash(self):
        # Animated splash transition
        self.screen.fill(COLOR_BG)
        self.draw_menu_background()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        font_l = pygame.font.SysFont(['Outfit', 'Segoe UI', 'Arial'], 72, bold=True)
        text = f"STAGE {self.level}" if self.level != 'B' else "ULTIMATE BOSS"
        
        # Text shadow
        shadow = font_l.render(text, True, (20, 20, 20))
        self.screen.blit(shadow, shadow.get_rect(center=(SCREEN_WIDTH // 2 + 4, SCREEN_HEIGHT // 2 + 4)))
        
        surf = font_l.render(text, True, (255, 255, 255))
        self.screen.blit(surf, surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
        
        # Flavor text
        font_s = pygame.font.SysFont(['Outfit', 'Segoe UI', 'Arial'], 20)
        flavors = {
            1: "Initializing Combat Systems...",
            2: "Scanning High-Risk Zones...",
            'B': "Emergency: Alpha-Beta Pruning Engaged!"
        }
        flavor = font_s.render(flavors.get(self.level, "Loading..."), True, (150, 160, 200))
        self.screen.blit(flavor, flavor.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)))

        # Progress Bar
        bar_w = 400
        bar_x = SCREEN_WIDTH // 2 - bar_w // 2
        bar_y = SCREEN_HEIGHT // 2 + 100
        progress = (STAGE_SPLASH_TIME - self.splash_timer) / STAGE_SPLASH_TIME
        
        pygame.draw.rect(self.screen, (30, 30, 50), (bar_x, bar_y, bar_w, 8), border_radius=4)
        pygame.draw.rect(self.screen, COLOR_PLAYER, (bar_x, bar_y, int(bar_w * progress), 8), border_radius=4)
        
        # Add a glow to the progress bar
        if progress > 0:
            glow_rect = pygame.Rect(bar_x, bar_y - 2, int(bar_w * progress), 12)
            glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (50, 200, 255, 60), (0, 0, glow_rect.width, glow_rect.height), border_radius=6)
            self.screen.blit(glow_surf, glow_rect)

    def draw_debug(self):
        font = pygame.font.SysFont('Arial', 14)
        # Mouse coords
        mx, my = pygame.mouse.get_pos()
        tx, ty = mx // TILE_SIZE, my // TILE_SIZE
        if tx < GRID_SIZE and ty < GRID_SIZE:
            txt = font.render(f"Tile: ({tx}, {ty})", True, (255, 255, 0))
            self.screen.blit(txt, (mx + 10, my + 10))
        
        # Enemy paths
        for enemy in self.enemies:
            if hasattr(enemy, 'path') and enemy.path:
                pts = [(enemy.x * TILE_SIZE + 12, enemy.y * TILE_SIZE + 12)]
                for px, py in enemy.path:
                    pts.append((px * TILE_SIZE + 12, py * TILE_SIZE + 12))
                if len(pts) > 1:
                    pygame.draw.lines(self.screen, (255, 0, 255), False, pts, 2)

if __name__ == "__main__":
    game = Game()
    game.run()
