import pygame
import random
import collections
from constants import *

class GameMap:
    def __init__(self, level=1):
        self.level = level
        self.grid = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.generate_map(level)

    def generate_map(self, level):
        while True:
            pygame.event.pump()
            self.grid = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
            
            # Place Eagle
            ex, ey = EAGLE_POS
            self.grid[ey][ex] = EAGLE
            
            # Base Safety: Surround Eagle with Brick
            base_ring = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0)]
            for dx, dy in base_ring:
                rx, ry = ex + dx, ey + dy
                if 0 <= rx < GRID_SIZE and 0 <= ry < GRID_SIZE:
                    if level == 1:
                        self.grid[ry][rx] = BRICK
                    else:
                        self.grid[ry][rx] = random.choice([BRICK, BRICK, STEEL])

            if level == 'B':
                self._generate_boss_level()
                break

            # Fill with CSP logic
            if self._fill_map_csp(level):
                break

    def _fill_map_csp(self, level):
        # Determine targets based on level
        if level == 1:
            targets = {BRICK: 150, STEEL: 20, WATER: 15, FOREST: 40}
        elif level == 2:
            targets = {BRICK: 120, STEEL: 50, WATER: 30, FOREST: 50}
        else:
            targets = {BRICK: 80, STEEL: 30, WATER: 10, FOREST: 20}

        elements = []
        for t, count in targets.items():
            elements.extend([t] * count)
        random.shuffle(elements)

        # Protected zones
        protected = set([EAGLE_POS, PLAYER_SPAWN] + ENEMY_SPAWNS)
        # Base ring
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                protected.add((EAGLE_POS[0]+dx, EAGLE_POS[1]+dy))
        # Immediate spawn neighbors
        for sx, sy in ENEMY_SPAWNS + [PLAYER_SPAWN]:
            for dx, dy in [UP, DOWN, LEFT, RIGHT]:
                protected.add((sx+dx, sy+dy))

        all_coords = [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE)]
        random.shuffle(all_coords)

        for tile_type in elements:
            placed = False
            for i in range(len(all_coords)):
                x, y = all_coords[i]
                if self.grid[y][x] == EMPTY and (x, y) not in protected:
                    # Temporary place
                    self.grid[y][x] = tile_type
                    
                    # Check reachability (Strict BFS: no walls)
                    if tile_type in [BRICK, STEEL, WATER]:
                        if self.is_reachable(ENEMY_SPAWNS, EAGLE_POS):
                            placed = True
                            all_coords.pop(i)
                            break
                        else:
                            # Backtrack
                            self.grid[y][x] = EMPTY
                    else:
                        placed = True
                        all_coords.pop(i)
                        break
        return True

    def is_reachable(self, start_points, target):
        for sx, sy in start_points:
            visited = set([(sx, sy)])
            queue = collections.deque([(sx, sy)])
            found = False
            while queue:
                cx, cy = queue.popleft()
                if (cx, cy) == target:
                    found = True
                    break
                for dx, dy in [UP, DOWN, LEFT, RIGHT]:
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                        # Passable tiles for reachability: EMPTY, FOREST, EAGLE
                        if self.grid[ny][nx] in [EMPTY, FOREST, EAGLE] and (nx, ny) not in visited:
                            visited.add((nx, ny))
                            queue.append((nx, ny))
            if not found:
                return False
        return True
    def _generate_boss_level(self):
        # 12x12 arena in center (7..18)
        # Surround everything else with Steel
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if 7 <= x <= 18 and 7 <= y <= 18:
                    self.grid[y][x] = EMPTY
                else:
                    self.grid[y][x] = STEEL
        
        # Scattered bricks
        for _ in range(30):
            rx, ry = random.randint(8, 17), random.randint(8, 17)
            if (rx, ry) != BOSS_SPAWN and (rx, ry) != BOSS_PLAYER_SPAWN:
                self.grid[ry][rx] = BRICK
        
        # Steel pillar clusters (2x2)
        pillars = [(9,9), (15,15), (9,15), (15,9)]
        for px, py in pillars:
            for dx in range(2):
                for dy in range(2):
                    self.grid[py+dy][px+dx] = STEEL
        
        # Water patch (2x3)
        for dx in range(3):
            for dy in range(2):
                self.grid[16+dy][8+dx] = WATER
                self.grid[9+dy][14+dx] = WATER

    def get_tile(self, x, y):
        if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
            return self.grid[y][x]
        return STEEL # Out of bounds is like steel

    def set_tile(self, x, y, tile_type):
        if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
            self.grid[y][x] = tile_type

    def draw(self, screen, frame_count):
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                tile = self.grid[y][x]
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                
                if tile == EMPTY:
                    pygame.draw.rect(screen, COLOR_EMPTY, rect)
                elif tile == BRICK:
                    pygame.draw.rect(screen, COLOR_BRICK, rect)
                    # Small grid lines for brick
                    pygame.draw.line(screen, (0,0,0), (x*TILE_SIZE, y*TILE_SIZE + TILE_SIZE//2), (x*TILE_SIZE + TILE_SIZE, y*TILE_SIZE + TILE_SIZE//2), 1)
                    pygame.draw.line(screen, (0,0,0), (x*TILE_SIZE + TILE_SIZE//2, y*TILE_SIZE), (x*TILE_SIZE + TILE_SIZE//2, y*TILE_SIZE + TILE_SIZE//2), 1)
                elif tile == STEEL:
                    pygame.draw.rect(screen, COLOR_STEEL, rect)
                    # Shine effect
                    pygame.draw.rect(screen, (200, 200, 200), (x*TILE_SIZE+4, y*TILE_SIZE+4, TILE_SIZE-8, TILE_SIZE-8), 1)
                elif tile == WATER:
                    # Animated water
                    shade_offset = 20 if (frame_count // 15) % 2 == 0 else 0
                    color = (COLOR_WATER[0], COLOR_WATER[1] + shade_offset, COLOR_WATER[2])
                    pygame.draw.rect(screen, color, rect)
                elif tile == FOREST:
                    pygame.draw.rect(screen, COLOR_FOREST, rect)
                elif tile == EAGLE:
                    pygame.draw.rect(screen, COLOR_EMPTY, rect)
                    pygame.draw.polygon(screen, COLOR_EAGLE, [
                        (x*TILE_SIZE + TILE_SIZE//2, y*TILE_SIZE + 4),
                        (x*TILE_SIZE + 4, y*TILE_SIZE + TILE_SIZE - 4),
                        (x*TILE_SIZE + TILE_SIZE - 4, y*TILE_SIZE + TILE_SIZE - 4)
                    ])
