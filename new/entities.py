from constants import *
import pygame

class GameObject:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Bullet(GameObject):
    def __init__(self, x, y, direction, owner_type):
        super().__init__(x, y)
        self.direction = direction
        self.owner_type = owner_type  # 'player' or 'enemy'
        self.active = True

class Tank(GameObject):
    def __init__(self, x, y, hp, move_cooldown_ticks, fire_cooldown_ticks, color):
        super().__init__(x, y)
        self.hp = hp
        self.max_hp = hp
        self.move_cooldown_ticks = move_cooldown_ticks
        self.fire_cooldown_ticks = fire_cooldown_ticks
        self.color = color
        
        self.direction = UP
        self.ticks_since_move = 0
        self.ticks_since_fire = 0
        self.active = True
        self.path = [] # For AI tanks

    def can_move(self):
        return self.ticks_since_move >= self.move_cooldown_ticks

    def can_fire(self):
        return self.ticks_since_fire >= self.fire_cooldown_ticks

    def reset_move_cooldown(self):
        self.ticks_since_move = 0

    def reset_fire_cooldown(self):
        self.ticks_since_fire = 0

    def update_cooldowns(self):
        self.ticks_since_move += 1
        self.ticks_since_fire += 1

class PlayerTank(Tank):
    def __init__(self, x, y):
        # Player moves slightly fast, can fire frequently but one bullet at a time usually
        super().__init__(x, y, hp=1, move_cooldown_ticks=2, fire_cooldown_ticks=5, color=COLOR_PLAYER)
        self.lives = 10

class BasicTank(Tank):
    def __init__(self, x, y):
        # 1 tile per 4 ticks, 1 bullet per 30 ticks (3s if 10 ticks/s)
        super().__init__(x, y, hp=1, move_cooldown_ticks=4, fire_cooldown_ticks=30, color=COLOR_ENEMY_BASIC)
        self.tank_type = "basic"

class FastTank(Tank):
    def __init__(self, x, y):
        # 1 tile per 2 ticks, 1 bullet per 15 ticks (1.5s)
        super().__init__(x, y, hp=1, move_cooldown_ticks=2, fire_cooldown_ticks=15, color=COLOR_ENEMY_FAST)
        self.tank_type = "fast"

class ArmorTank(Tank):
    def __init__(self, x, y):
        # 1 tile per 3 ticks, 1 bullet per 20 ticks (2s), 4 HP
        super().__init__(x, y, hp=4, move_cooldown_ticks=3, fire_cooldown_ticks=20, color=COLOR_ENEMY_ARMOR)
        self.hits_taken = 0
        self.retreating = False
        self.retreat_timer = 0
        self.tank_type = "armor"

class BossTank(Tank):
    def __init__(self, x, y):
        # Phase 1 starting stats
        super().__init__(x, y, hp=10, move_cooldown_ticks=4, fire_cooldown_ticks=20, color=COLOR_BOSS)
        self.phase = 1
        self.tank_type = "boss"
