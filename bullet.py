import pygame
from constants import *

class Bullet:
    def __init__(self, x, y, direction, owner):
        self.x = x
        self.y = y
        self.direction = direction
        self.owner = owner # Reference to the tank that fired it
        self.active = True

    def update(self, game_map, tanks, bullets):
        # Advance 2 tiles per tick as per requirements
        for _ in range(BULLET_SPEED):
            dx, dy = self.direction
            self.x += dx
            self.y += dy

            # Check screen boundaries
            if not (0 <= self.x < GRID_SIZE and 0 <= self.y < GRID_SIZE):
                self.active = False
                return

            # Check tile collisions
            tile = game_map.get_tile(self.x, self.y)
            if tile == BRICK:
                game_map.set_tile(self.x, self.y, EMPTY)
                self.active = False
                return
            elif tile == STEEL:
                self.active = False
                return
            elif tile == EAGLE:
                game_map.set_tile(self.x, self.y, EMPTY) # Destroy eagle
                self.active = False
                return

            # Check tank collisions
            for tank in tanks:
                if tank.active and tank != self.owner:
                    if tank.x == self.x and tank.y == self.y:
                        tank.take_damage()
                        self.active = False
                        return

            # Check bullet-bullet collisions
            for other in bullets:
                if other != self and other.active:
                    if other.x == self.x and other.y == self.y:
                        self.active = False
                        other.active = False
                        return

    def draw(self, screen):
        rect = pygame.Rect(self.x * TILE_SIZE + 8, self.y * TILE_SIZE + 8, 8, 8)
        pygame.draw.rect(screen, (255, 255, 0), rect)
