import pygame
import random
import math
from constants import *
from bullet import Bullet
import agents.basic_tank_agent as basic_agent
import agents.fast_tank_agent as fast_agent
import agents.armor_tank_agent as armor_agent

class Tank:
    def __init__(self, x, y, direction, color):
        self.x = x
        self.y = y
        self.direction = direction
        self.color = color
        self.hp = 1
        self.hp_lost = 0
        self.active = True
        self.move_cooldown = 0
        self.shoot_cooldown = 0
        self.bullet = None
        self.respawn_timer = 0
        
        # Stats (Default: Player)
        self.speed_stat = PLAYER_SPEED
        self.fire_rate_stat = 30 # 0.5s at 60 FPS
        
        self.path = []
        self.ticks_since_path = 0
        self.flash_timer = 0
        self.stuck_timer = 0
    
    def update(self):
        if self.move_cooldown > 0: self.move_cooldown -= 1
        if self.shoot_cooldown > 0: self.shoot_cooldown -= 1
        if self.flash_timer > 0: self.flash_timer -= 1
        self.ticks_since_path += 1

    def move(self, direction, game_map, other_tanks):
        if isinstance(direction, str):
            mapping = {'up': UP, 'down': DOWN, 'left': LEFT, 'right': RIGHT}
            direction = mapping.get(direction, self.direction)

        self.direction = direction
        
        if self.move_cooldown > 0:
            return False

        dx, dy = direction
        nx, ny = self.x + dx, self.y + dy

        if not (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE):
            return False

        tile = game_map.get_tile(nx, ny)
        if tile in [BRICK, STEEL, WATER, EAGLE]:
            return False

        for tank in other_tanks:
            if tank != self and tank.active:
                if tank.x == nx and tank.y == ny:
                    return False

        self.x = nx
        self.y = ny
        self.move_cooldown = self.speed_stat
        self.stuck_timer = 0
        return True

    def shoot(self, bullets, direction=None):
        if direction:
            mapping = {'up': UP, 'down': DOWN, 'left': LEFT, 'right': RIGHT}
            if isinstance(direction, str):
                self.direction = mapping.get(direction, self.direction)
            else:
                self.direction = direction

        if self.shoot_cooldown > 0:
            return False

        if self.bullet is None or not self.bullet.active:
            bx, by = self.x + self.direction[0], self.y + self.direction[1]
            if 0 <= bx < GRID_SIZE and 0 <= by < GRID_SIZE:
                self.bullet = Bullet(bx, by, self.direction, self)
                bullets.append(self.bullet)
                self.shoot_cooldown = self.fire_rate_stat
                return True
        return False

    def take_damage(self):
        self.hp -= 1
        self.hp_lost += 1
        self.flash_timer = 15
        if self.hp <= 0:
            self.active = False

    def draw(self, screen):
        if not self.active: return
        
        color = self.color
        if self.flash_timer > 0:
            if (self.flash_timer // 2) % 2 == 0:
                color = (255, 255, 255)

        rect = pygame.Rect(self.x * TILE_SIZE + 2, self.y * TILE_SIZE + 2, TILE_SIZE - 4, TILE_SIZE - 4)
        # Rounded tank body
        pygame.draw.rect(screen, color, rect, border_radius=4)
        
        # Barrel
        bx = self.x * TILE_SIZE + TILE_SIZE // 2 + self.direction[0] * (TILE_SIZE // 2 - 2)
        by = self.y * TILE_SIZE + TILE_SIZE // 2 + self.direction[1] * (TILE_SIZE // 2 - 2)
        pygame.draw.line(screen, (0, 0, 0), (self.x * TILE_SIZE + TILE_SIZE // 2, self.y * TILE_SIZE + TILE_SIZE // 2), (bx, by), 4)

class PlayerTank(Tank):
    def __init__(self, x, y):
        super().__init__(x, y, UP, COLOR_PLAYER)
        self.lives = PLAYER_LIVES
        self.fire_rate_stat = 20 # Player fires faster

    def take_damage(self):
        super().take_damage()
        if not self.active:
            self.lives -= 1
            if self.lives > 0:
                self.respawn_timer = 90 # 1.5s at 60 FPS

    def respawn(self):
        self.x, self.y = PLAYER_SPAWN
        self.direction = UP
        self.hp = 1
        self.hp_lost = 0
        self.active = True
        self.respawn_timer = 0

class EnemyTank(Tank):
    def __init__(self, x, y, tank_type='basic'):
        self.tank_type = tank_type
        if tank_type == 'basic':
            super().__init__(x, y, DOWN, COLOR_ENEMY_BASIC)
            self.agent = basic_agent
            self.hp = 1
            self.speed_stat = 12
            self.fire_rate_stat = 180
        elif tank_type == 'fast':
            super().__init__(x, y, DOWN, COLOR_ENEMY_FAST)
            self.agent = fast_agent
            self.hp = 1
            self.speed_stat = 6
            self.fire_rate_stat = 120
        elif tank_type == 'armor':
            super().__init__(x, y, DOWN, COLOR_ENEMY_ARMOR)
            self.agent = armor_agent
            self.hp = 4
            self.speed_stat = 10
            self.fire_rate_stat = 150
        elif tank_type == 'power':
            super().__init__(x, y, DOWN, (200, 100, 255))
            self.agent = armor_agent
            self.hp = 4
            self.speed_stat = 8
            self.fire_rate_stat = 90
        elif tank_type == 'boss':
            super().__init__(x, y, DOWN, COLOR_BOSS_P1)
            # HP and Agent are specialized in BossTank subclass

    def update_ai(self, game_map, tanks, bullets, player):
        self.update()
        
        game_state = {
            'grid': game_map.grid,
            'player_pos': (player.x, player.y) if player.active else None,
            'eagle_pos': EAGLE_POS,
            'tanks': tanks,
            'bullets': bullets,
            'player': player,
            'boss': self
        }
        
        # Call agent
        if self.tank_type == 'boss':
            result = self.agent.decide(self, game_state)
            action, n_raw, n_pruned = result
            self.last_stats = (n_raw, n_pruned)
        else:
            action = self.agent.decide(self, game_state)
        
        atype, aval = action
        
        if atype == 'move':
            if self.move_cooldown == 0:
                if not self.move(aval, game_map, tanks):
                    self.stuck_timer += 1
                else:
                    # Successfully moved, update path
                    if self.path:
                        if (self.x, self.y) == self.path[0]:
                            self.path.pop(0)
            else:
                self.stuck_timer += 1
        elif atype == 'shoot':
            self.shoot(bullets, aval)
        elif atype == 'stay':
            pass

        # Stuck detection
        if self.stuck_timer > 60: # 1 second stuck
            dirs = ['up', 'down', 'left', 'right']
            random.shuffle(dirs)
            for d in dirs:
                if self.move(d, game_map, tanks):
                    self.stuck_timer = 0
                    self.path = [] # Force re-path
                    break

class BossTank(EnemyTank):
    def __init__(self, x, y):
        super().__init__(x, y, 'boss')
        from agents.boss_tank_agent import BossAgent
        self.agent = BossAgent()
        self.hp = BOSS_HP_MAX
        self.color = COLOR_BOSS_P1
        self.last_stats = (0, 0)
        self.phase = 1

    def update_ai(self, game_map, tanks, bullets, player):
        # Update Phase
        for p, data in BOSS_PHASES.items():
            if data['hp'][0] <= self.hp <= data['hp'][1]:
                self.phase = p
                break
        
        phase_data = BOSS_PHASES[self.phase]
        self.speed_stat = phase_data['speed']
        self.fire_rate_stat = phase_data['fire_rate']
        
        if self.phase == 1: self.color = COLOR_BOSS_P1
        elif self.phase == 2: self.color = COLOR_BOSS_P2
        elif self.phase == 3: self.color = COLOR_BOSS_P3
        
        super().update_ai(game_map, tanks, bullets, player)

    def draw(self, screen):
        if not self.active: return
        
        offset_x, offset_y = 0, 0
        draw_color = self.color
        
        if self.phase == 2:
            pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) / 2
            draw_color = [int(c * (0.8 + 0.2 * pulse)) for c in self.color]
        elif self.phase == 3:
            if pygame.time.get_ticks() % 4 == 0:
                offset_x = random.randint(-3, 3)
                offset_y = random.randint(-3, 3)
        
        # HP Bar
        pygame.draw.rect(screen, (40, 40, 40), (self.x*TILE_SIZE + offset_x, self.y*TILE_SIZE - 10 + offset_y, TILE_SIZE, 5))
        fill = int(TILE_SIZE * (self.hp / BOSS_HP_MAX))
        pygame.draw.rect(screen, COLOR_HP_BAR, (self.x*TILE_SIZE + offset_x, self.y*TILE_SIZE - 10 + offset_y, fill, 5))

        if self.flash_timer > 0 and (self.flash_timer // 2) % 2 == 0:
            draw_color = (255, 255, 255)

        rect = pygame.Rect(self.x * TILE_SIZE + offset_x, self.y * TILE_SIZE + offset_y, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, draw_color, rect, border_radius=6)
        
        # Boss Details
        pygame.draw.rect(screen, (0,0,0), rect, 2, border_radius=6)
        center = rect.center
        bx = center[0] + self.direction[0] * (TILE_SIZE // 2 - 2)
        by = center[1] + self.direction[1] * (TILE_SIZE // 2 - 2)
        pygame.draw.line(screen, (0,0,0), center, (bx, by), 6)
