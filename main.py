import pygame
import sys
import random
import math
import asyncio
from constants import *
from game_map import GameMap
from tank import PlayerTank, EnemyTank, BossTank
from hud import HUD

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
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
        
        # UI State
        self.menu_selection = 0
        self.menu_options = [
            {"id": 1, "name": "STAGE 1", "desc": "The Frontlines", "color": COLOR_PLAYER},
            {"id": 2, "name": "STAGE 2", "desc": "Industrial Zone", "color": COLOR_ENEMY_ARMOR},
            {"id": 'B', "name": "BOSS FIGHT", "desc": "Ultimate AI Challenge", "color": COLOR_BOSS_P3},
            {"id": 'H', "name": "HOW TO PLAY", "desc": "Controls & Tactics", "color": COLOR_ACCENT}
        ]
        
        # Mobile Controls State
        self.is_mobile = False 
        self.dpad_rects = {
            UP: pygame.Rect(80, SCREEN_HEIGHT - 160, 60, 60),
            DOWN: pygame.Rect(80, SCREEN_HEIGHT - 60, 60, 60),
            LEFT: pygame.Rect(20, SCREEN_HEIGHT - 110, 60, 60),
            RIGHT: pygame.Rect(140, SCREEN_HEIGHT - 110, 60, 60)
        }
        self.fire_rect = pygame.Rect(SCREEN_WIDTH - 120, SCREEN_HEIGHT - 120, 80, 80)

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
        self.frame_count = 0; self.spawn_timer = 0; self.spawn_index = 0; self.enemies_killed = 0; self.boss_log_saved = False
        if self.level == 1: self.enemy_pool = ['basic']*7 + ['fast']*5
        elif self.level == 2: self.enemy_pool = ['fast']*4 + ['armor']*3 + ['power']*2
        elif self.level == 'B': self.enemy_pool = []
        else: self.enemy_pool = ['basic']*10

    def handle_input(self):
        if self.game_state not in ["PLAYING", "BOSS_FIGHT"] or self.player is None: return
        keys = pygame.key.get_pressed()
        moved = False
        if self.player.active:
            if keys[pygame.K_UP] or keys[pygame.K_w]: self.player.move(UP, self.game_map, self.enemies + [self.player]); moved = True
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]: self.player.move(DOWN, self.game_map, self.enemies + [self.player]); moved = True
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]: self.player.move(LEFT, self.game_map, self.enemies + [self.player]); moved = True
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.player.move(RIGHT, self.game_map, self.enemies + [self.player]); moved = True
            if keys[pygame.K_SPACE]: self.player.shoot(self.bullets)
            if not moved and pygame.mouse.get_pressed()[0]:
                mx, my = pygame.mouse.get_pos()
                for direction, rect in self.dpad_rects.items():
                    if rect.collidepoint(mx, my): self.is_mobile = True; self.player.move(direction, self.game_map, self.enemies + [self.player])
                if self.fire_rect.collidepoint(mx, my): self.is_mobile = True; self.player.shoot(self.bullets)

    def handle_menu_click(self, pos):
        card_w, card_h = 400, 70; start_y = 220
        for i, opt in enumerate(self.menu_options):
            y_pos = start_y + i * (card_h + 15)
            rect = pygame.Rect(SCREEN_WIDTH // 2 - card_w // 2, y_pos, card_w, card_h)
            if rect.collidepoint(pos):
                if self.menu_selection == i: self.process_selection(opt['id'])
                else: self.menu_selection = i
                return True
        return False

    def process_selection(self, selection_id):
        if selection_id == 'H': self.game_state = "HOW_TO"
        else: self.start_splash(selection_id)

    def update(self):
        if self.game_state == "SPLASH":
            self.splash_timer -= 1
            if self.splash_timer <= 0: self.reset_level()
            return
        if self.game_state not in ["PLAYING", "BOSS_FIGHT"]: return
        if not self.player.active and self.player.lives > 0:
            self.player.respawn_timer -= 1
            if self.player.respawn_timer <= 0:
                self.player.respawn()
                if self.level == 'B': self.player.x, self.player.y = BOSS_PLAYER_SPAWN
        self.player.update()
        for enemy in self.enemies:
            if enemy.active: enemy.update_ai(self.game_map, self.enemies + [self.player], self.bullets, self.player)
        for bullet in self.bullets[:]:
            if bullet.active: bullet.update(self.game_map, self.enemies + [self.player], self.bullets, self.frame_count)
            else: self.bullets.remove(bullet)
        for enemy in self.enemies[:]:
            if not enemy.active: self.enemies.remove(enemy); self.enemies_killed += 1
        if not self.debug_mode:
            if len(self.enemies) < MAX_ACTIVE_ENEMIES and len(self.enemy_pool) > 0:
                self.spawn_timer += 1
                if self.spawn_timer >= FPS * 2:
                    spawn_pos = ENEMY_SPAWNS[self.spawn_index]
                    if abs(spawn_pos[0] - self.player.x) + abs(spawn_pos[1] - self.player.y) > 10:
                        type = self.enemy_pool.pop(0)
                        self.enemies.append(EnemyTank(spawn_pos[0], spawn_pos[1], type))
                        self.spawn_index = (self.spawn_index + 1) % len(ENEMY_SPAWNS); self.spawn_timer = 0
        if self.level != 'B':
            if self.game_map.get_tile(EAGLE_POS[0], EAGLE_POS[1]) != EAGLE: self.game_state = "GAME_OVER"
            elif self.player.lives <= 0 and not self.player.active: self.game_state = "GAME_OVER"
            elif len(self.enemy_pool) == 0 and len(self.enemies) == 0: self.game_state = "STAGE_CLEAR"
        else:
            if self.player.lives <= 0 and not self.player.active: self.game_state = "GAME_OVER"
            elif len(self.enemies) == 0:
                self.game_state = "VICTORY"
                if not self.boss_log_saved: self.save_boss_stats()

    def save_boss_stats(self):
        try:
            with open("boss_stats.txt", "w") as f:
                f.write("BATTLE CITY - BOSS FIGHT LOG\n")
                for i, stats in enumerate(self.total_stats): f.write(f"Tick {i}: {stats[0]}/{stats[1]}\n")
            self.boss_log_saved = True
        except: pass

    def start_splash(self, level):
        self.level = level; self.game_state = "SPLASH"; self.splash_timer = STAGE_SPLASH_TIME

    async def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_state == "MENU": self.handle_menu_click(event.pos)
                    elif self.game_state in ["STAGE_CLEAR", "GAME_OVER", "VICTORY", "HOW_TO"]: self.game_state = "MENU"
                if event.type == pygame.KEYDOWN:
                    if self.game_state == "MENU":
                        if event.key in [pygame.K_UP, pygame.K_w]: self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
                        elif event.key in [pygame.K_DOWN, pygame.K_s]: self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
                        elif event.key == pygame.K_RETURN: self.process_selection(self.menu_options[self.menu_selection]['id'])
                    elif self.game_state in ["STAGE_CLEAR", "GAME_OVER", "VICTORY", "HOW_TO"]: self.game_state = "MENU"

            self.handle_input(); self.update()
            self.screen.fill(COLOR_BG)
            if self.game_state == "MENU": self.draw_modern_menu()
            elif self.game_state == "HOW_TO": self.draw_how_to()
            elif self.game_state == "SPLASH": self.draw_splash()
            else:
                self.game_map.draw(self.screen, self.frame_count)
                if self.player.active: self.player.draw(self.screen)
                boss_stats = (0,0)
                for enemy in self.enemies:
                    enemy.draw(self.screen)
                    if enemy.tank_type == 'boss':
                        boss_stats = enemy.last_stats
                        if self.game_state == "BOSS_FIGHT": self.total_stats.append(boss_stats)
                for bullet in self.bullets: bullet.draw(self.screen)
                for y in range(GRID_SIZE):
                    for x in range(GRID_SIZE):
                        if self.game_map.grid[y][x] == FOREST: pygame.draw.rect(self.screen, COLOR_FOREST, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                self.hud.draw(self.screen, self.player.lives, len(self.enemy_pool) + len(self.enemies), self.level, self.game_state, boss_stats)
                if self.is_mobile: self.draw_mobile_controls()
            
            pygame.display.flip()
            self.clock.tick(FPS)
            self.frame_count += 1
            await asyncio.sleep(0)

    def draw_how_to(self):
        font_m = pygame.font.SysFont('Arial', 24, bold=True)
        font_s = pygame.font.SysFont('Arial', 18)
        self.screen.fill((10, 10, 20))
        y = 100
        controls = [("MOVE", "WASD / ARROWS"), ("FIRE", "SPACEBAR"), ("MOBILE", "VIRTUAL D-PAD")]
        for t, d in controls:
            self.screen.blit(font_m.render(t, True, COLOR_ACCENT), (200, y))
            self.screen.blit(font_s.render(d, True, (200, 200, 220)), (200, y+30))
            y += 80

    def draw_mobile_controls(self):
        for direction, rect in self.dpad_rects.items():
            pygame.draw.rect(self.screen, (0, 255, 200, 100), rect, 2, border_radius=15)
        pygame.draw.circle(self.screen, (255, 60, 80, 130), (self.fire_rect.center), 40)

    def draw_modern_menu(self):
        font_l = pygame.font.SysFont('Arial', 72, bold=True)
        font_s = pygame.font.SysFont('Arial', 18, bold=True)
        self.screen.blit(font_l.render("BATTLE CITY", True, (255,255,255)), (SCREEN_WIDTH//2-200, 50))
        y = 200
        for i, opt in enumerate(self.menu_options):
            sel = (i == self.menu_selection)
            rect = pygame.Rect(SCREEN_WIDTH//2-200, y, 400, 70)
            pygame.draw.rect(self.screen, (40, 40, 60) if sel else (20, 20, 30), rect, border_radius=10)
            if sel: pygame.draw.rect(self.screen, COLOR_ACCENT, rect, 2, border_radius=10)
            self.screen.blit(font_s.render(opt['name'], True, (255,255,255)), (rect.x+20, rect.y+20))
            y += 85

    def draw_splash(self):
        font = pygame.font.SysFont('Arial', 64, bold=True)
        txt = font.render(f"STAGE {self.level}", True, (255,255,255))
        self.screen.blit(txt, txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))

async def main():
    game = Game()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())
