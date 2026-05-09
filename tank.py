import pygame
import random
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
        self.bullet = None
        self.respawn_timer = 0
        
        # Agent state
        self.path = []
        self.ticks_since_path = 0
        self.flash_timer = 0

    def move(self, direction, game_map, other_tanks):
        if isinstance(direction, str):
            mapping = {'up': UP, 'down': DOWN, 'left': LEFT, 'right': RIGHT}
            direction = mapping.get(direction, self.direction)

        self.direction = direction
        
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
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
        self.move_cooldown = 2
        return True

    def shoot(self, bullets, direction=None):
        if direction:
            mapping = {'up': UP, 'down': DOWN, 'left': LEFT, 'right': RIGHT}
            self.direction = mapping.get(direction, self.direction)

        if self.bullet is None or not self.bullet.active:
            bx, by = self.x + self.direction[0], self.y + self.direction[1]
            if 0 <= bx < GRID_SIZE and 0 <= by < GRID_SIZE:
                self.bullet = Bullet(bx, by, self.direction, self)
                bullets.append(self.bullet)
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
            self.flash_timer -= 1
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
        elif tank_type == 'fast':
            super().__init__(x, y, DOWN, COLOR_ENEMY_FAST)
            self.agent = fast_agent
            self.hp = 1
        elif tank_type == 'armor':
            super().__init__(x, y, DOWN, COLOR_ENEMY_ARMOR)
            self.agent = armor_agent
            self.hp = 4 # Needs 3 hits to retreat (4 total to die)
        elif tank_type == 'power':
            super().__init__(x, y, DOWN, (200, 100, 0))
            self.agent = armor_agent # Uses Armor AI
            self.hp = 4
            self.move_speed = 1 # We'll handle speed by cooldown
        
        self.tank_type = tank_type

    def update_ai(self, game_map, tanks, bullets, player):
        self.ticks_since_path += 1
        
        # Prepare game state for agent
        game_state = {
            'grid': game_map.grid,
            'player_pos': (player.x, player.y) if player.active else None,
            'eagle_pos': EAGLE_POS,
            'tanks': tanks,
            'bullets': bullets
        }
        
        action_type, action_value = self.agent.decide(self, game_state)
        
        if action_type == 'move':
            self.move(action_value, game_map, tanks)
        elif action_type == 'shoot':
            self.shoot(bullets, action_value)
        
        # Handle Power Tank speed (+1 speed = less cooldown)
        if self.tank_type == 'power' and self.move_cooldown > 0:
            self.move_cooldown = 1 # Default is 2, power is 1
