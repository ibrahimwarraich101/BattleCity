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
        self.reset_level()

    def reset_level(self):
        self.game_map = GameMap(self.level)
        self.player = PlayerTank(PLAYER_SPAWN[0], PLAYER_SPAWN[1])
        self.enemies = []
        self.bullets = []
        self.frame_count = 0
        self.game_state = "PLAYING"
        self.spawn_timer = 0
        self.spawn_index = 0
        self.enemies_killed = 0
        
        # Level Configs
        if self.level == 1:
            self.enemy_pool = ['basic']*7 + ['fast']*5
        elif self.level == 2:
            self.enemy_pool = ['fast']*4 + ['armor']*3 + ['power']*2
        else:
            self.enemy_pool = ['basic']*10 # Fallback

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
        if self.game_state != "PLAYING":
            return

        if not self.player.active and self.player.lives > 0:
            self.player.respawn_timer -= 1
            if self.player.respawn_timer <= 0:
                self.player.respawn()

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
        if self.game_map.get_tile(EAGLE_POS[0], EAGLE_POS[1]) != EAGLE:
            self.game_state = "GAME_OVER"
        elif self.player.lives <= 0 and not self.player.active:
            self.game_state = "GAME_OVER"
        elif len(self.enemy_pool) == 0 and len(self.enemies) == 0:
            self.game_state = "STAGE_CLEAR"

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
                    if event.key == pygame.K_d:
                        self.toggle_debug()
                    if self.game_state == "STAGE_CLEAR":
                        self.level += 1
                        self.reset_level()
                    elif self.game_state == "GAME_OVER":
                        self.level = 1
                        self.reset_level()

            self.handle_input()
            self.update()
            
            self.screen.fill((0, 0, 0))
            self.game_map.draw(self.screen, self.frame_count)
            
            self.player.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)
            
            for bullet in self.bullets:
                bullet.draw(self.screen)

            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    if self.game_map.grid[y][x] == FOREST:
                        rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                        pygame.draw.rect(self.screen, COLOR_FOREST, rect)

            self.hud.draw(self.screen, self.player.lives, len(self.enemy_pool) + len(self.enemies), self.level, self.game_state)
            
            if self.debug_mode:
                font = pygame.font.SysFont('Arial', 24, bold=True)
                txt = font.render("DEBUG MODE: Detour Test", True, (255, 255, 0))
                self.screen.blit(txt, (10, 10))

            pygame.display.flip()
            self.clock.tick(FPS)
            self.frame_count += 1

if __name__ == "__main__":
    game = Game()
    game.run()
