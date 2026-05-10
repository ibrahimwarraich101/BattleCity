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
        self.hp_lost = 0 # To track damage for agents
        self.active = True
        self.move_cooldown = 0
        self.shoot_cooldown = 0
        self.bullet = None
        self.respawn_timer = 0
        
        # Stats (Default: Player)
        self.speed_stat = PLAYER_SPEED
        self.fire_rate_stat = 60 # Player fires every 2s now
        
        # Agent state
        self.path = []
        self.ticks_since_path = 0
        self.flash_timer = 0
    
    def update(self):
        if self.move_cooldown > 0: self.move_cooldown -= 1
        if self.shoot_cooldown > 0: self.shoot_cooldown -= 1
        if self.flash_timer > 0: self.flash_timer -= 1

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
        return True

    def shoot(self, bullets, direction=None):
        if direction:
            mapping = {'up': UP, 'down': DOWN, 'left': LEFT, 'right': RIGHT}
            self.direction = mapping.get(direction, self.direction)

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
        self.flash_timer = 10
        if self.hp <= 0:
            self.active = False

    def draw(self, screen):
        if not self.active: return
        
        color = self.color
        if self.flash_timer > 0:
            if self.flash_timer % 2 == 0:
                color = (255, 255, 255) # White flash

        rect = pygame.Rect(self.x * TILE_SIZE, self.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, color, rect)
        
        center = (self.x * TILE_SIZE + TILE_SIZE // 2, self.y * TILE_SIZE + TILE_SIZE // 2)
        size = 8
        if self.direction == UP:
            pts = [(center[0], center[1]-size), (center[0]-size, center[1]), (center[0]+size, center[1])]
        elif self.direction == DOWN:
            pts = [(center[0], center[1]+size), (center[0]-size, center[1]), (center[0]+size, center[1])]
        elif self.direction == LEFT:
            pts = [(center[0]-size, center[1]), (center[0], center[1]-size), (center[0], center[1]+size)]
        elif self.direction == RIGHT:
            pts = [(center[0]+size, center[1]), (center[0], center[1]-size), (center[0], center[1]+size)]
        
        pygame.draw.polygon(screen, (0, 0, 0), pts)

class PlayerTank(Tank):
    def __init__(self, x, y):
        super().__init__(x, y, UP, COLOR_PLAYER)
        self.lives = PLAYER_LIVES

    def take_damage(self):
        super().take_damage()
        if not self.active:
            self.lives -= 1
            if self.lives > 0:
                self.respawn_timer = int(1.5 * FPS)

    def respawn(self):
        self.x, self.y = PLAYER_SPAWN
        self.direction = UP
        self.hp = 1
        self.hp_lost = 0
        self.active = True
        self.respawn_timer = 0

class EnemyTank(Tank):
    def __init__(self, x, y, tank_type='basic'):
        if tank_type == 'basic':
            super().__init__(x, y, DOWN, COLOR_ENEMY_BASIC)
            self.agent = basic_agent
            self.hp = 1
            self.speed_stat = 8 # Very slow movement
            self.fire_rate_stat = 180 # 6 seconds
        elif tank_type == 'fast':
            super().__init__(x, y, DOWN, COLOR_ENEMY_FAST)
            self.agent = fast_agent
            self.hp = 1
            self.speed_stat = 4
            self.fire_rate_stat = 120 # 4 seconds
        elif tank_type == 'armor':
            super().__init__(x, y, DOWN, COLOR_ENEMY_ARMOR)
            self.agent = armor_agent
            self.hp = 4 # Needs 3 hits to retreat (4 total to die)
            self.speed_stat = 6
            self.fire_rate_stat = 150 # 5 seconds
        elif tank_type == 'power':
            super().__init__(x, y, DOWN, (200, 100, 0))
            self.agent = armor_agent # Uses Armor AI
            self.hp = 4
            self.speed_stat = 4 # Reduced speed
            self.fire_rate_stat = 120 # Reduced fire rate
        elif tank_type == 'boss':
            super().__init__(x, y, DOWN, COLOR_BOSS_P1)
            # HP and Agent handled in BossTank subclass
        
        self.tank_type = tank_type

    def update_ai(self, game_map, tanks, bullets, player):
        self.ticks_since_path += 1
        self.update() # Handle cooldowns
        
        # Prepare game state for agent
        game_state = {
            'grid': game_map.grid,
            'player_pos': (player.x, player.y) if player.active else None,
            'eagle_pos': EAGLE_POS,
            'tanks': tanks,
            'bullets': bullets,
            'player': player,
            'boss': self
        }
        
        if self.tank_type == 'boss':
            action, n_raw, n_pruned = self.agent.decide(self, game_state)
            self.last_stats = (n_raw, n_pruned)
            action_type, action_value = action
        else:
            action_type, action_value = self.agent.decide(self, game_state)
        
        if action_type == 'move':
            self.move(action_value, game_map, tanks)
        elif action_type == 'shoot':
            self.shoot(bullets, action_value)
        
        # Handle Power Tank speed
        if self.tank_type == 'power' and self.move_cooldown > 0:
            self.move_cooldown = 1

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
        # HP-based Phase System
        for p, data in BOSS_PHASES.items():
            if data['hp'][0] <= self.hp <= data['hp'][1]:
                self.phase = p
                break
        
        # Update Stats/Visuals based on Phase
        phase_data = BOSS_PHASES[self.phase]
        self.speed_stat = phase_data['speed']
        self.fire_rate_stat = phase_data['fire_rate']
        
        if self.phase == 1: self.color = COLOR_BOSS_P1
        elif self.phase == 2: self.color = COLOR_BOSS_P2
        elif self.phase == 3: self.color = COLOR_BOSS_P3
        
        # Decision and movement
        super().update_ai(game_map, tanks, bullets, player)

    def draw(self, screen):
        if not self.active: return
        
        # Phase Visual Effects
        offset_x, offset_y = 0, 0
        draw_color = self.color
        
        if self.phase == 2:
            # Pulsing glow
            pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) / 2
            draw_color = (
                int(self.color[0] * (0.7 + 0.3 * pulse)),
                int(self.color[1] * (0.7 + 0.3 * pulse)),
                int(self.color[2] * (0.7 + 0.3 * pulse))
            )
        elif self.phase == 3:
            # Screen shake / offset
            if pygame.time.get_ticks() % 5 == 0:
                offset_x = random.randint(-2, 2)
                offset_y = random.randint(-2, 2)
        
        # HP Bar
        bar_width = TILE_SIZE
        bar_height = 4
        pygame.draw.rect(screen, (0,0,0), (self.x*TILE_SIZE + offset_x, self.y*TILE_SIZE - 6 + offset_y, bar_width, bar_height))
        fill_width = int(bar_width * (self.hp / BOSS_HP_MAX))
        pygame.draw.rect(screen, COLOR_HP_BAR, (self.x*TILE_SIZE + offset_x, self.y*TILE_SIZE - 6 + offset_y, fill_width, bar_height))

        # Flash effect
        if self.flash_timer > 0:
            if self.flash_timer % 2 == 0:
                draw_color = (255, 255, 255)

        rect = pygame.Rect(self.x * TILE_SIZE + offset_x, self.y * TILE_SIZE + offset_y, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, draw_color, rect)
        
        # Direction indicator
        center = (self.x * TILE_SIZE + TILE_SIZE // 2 + offset_x, self.y * TILE_SIZE + TILE_SIZE // 2 + offset_y)
        size = 8
        if self.direction == UP: pts = [(center[0], center[1]-size), (center[0]-size, center[1]), (center[0]+size, center[1])]
        elif self.direction == DOWN: pts = [(center[0], center[1]+size), (center[0]-size, center[1]), (center[0]+size, center[1])]
        elif self.direction == LEFT: pts = [(center[0]-size, center[1]), (center[0], center[1]-size), (center[0], center[1]+size)]
        elif self.direction == RIGHT: pts = [(center[0]+size, center[1]), (center[0], center[1]-size), (center[0], center[1]+size)]
        pygame.draw.polygon(screen, (0, 0, 0), pts)
