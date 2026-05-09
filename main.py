import pygame
import sys
import random
from constants import *
from game_map import GameMap
from tank import PlayerTank, EnemyTank
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

        # Update Enemy AI
        for enemy in self.enemies:
            if enemy.active:
                enemy.update_ai(self.game_map, self.enemies + [self.player], self.bullets, self.player)

        # Update Bullets
        for bullet in self.bullets[:]:
            if bullet.active:
                bullet.update(self.game_map, self.enemies + [self.player], self.bullets)
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
                f.write(f"Tick {i}: Raw={stats[0]}, Pruned={stats[1]}, Speedup={stats[0]/stats[1]:.2f}x\n")
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
                        if event.key == pygame.K_RETURN: self.start_splash(1)
                        elif event.key == pygame.K_1: self.start_splash(1)
                        elif event.key == pygame.K_2: self.start_splash(2)
                        elif event.key == pygame.K_b: self.start_splash('B')
                    elif event.key == pygame.K_d:
                        self.toggle_debug()
                    elif self.game_state == "STAGE_CLEAR":
                        if self.level == 1: self.start_splash(2)
                        elif self.level == 2: self.start_splash('B')
                    elif self.game_state in ["GAME_OVER", "VICTORY"]:
                        self.game_state = "MENU"

            self.handle_input()
            self.update()
            
            self.screen.fill((0, 0, 0))
            
            if self.game_state == "MENU":
                self.draw_menu()
            elif self.game_state == "SPLASH":
                self.draw_splash()
            else:
                self.game_map.draw(self.screen, self.frame_count)
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
        font = pygame.font.SysFont('Arial', 64, bold=True)
        title = font.render("BATTLE CITY", True, (255, 255, 255))
        rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(title, rect)
        
        font = pygame.font.SysFont('Arial', 24)
        prompt = font.render("Press ENTER to Start", True, (200, 200, 200))
        rect = prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(prompt, rect)
        
        hint = font.render("Press 1, 2, or B to select level", True, (150, 150, 150))
        rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(hint, rect)

    def draw_splash(self):
        font = pygame.font.SysFont('Arial', 48, bold=True)
        text = f"STAGE {self.level}" if self.level != 'B' else "BOSS LEVEL"
        surf = font.render(text, True, (255, 255, 255))
        rect = surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(surf, rect)

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
