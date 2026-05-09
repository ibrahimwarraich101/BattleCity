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
            pygame.event.pump() # Keep window responsive
            self.grid = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
            
            # Place Eagle
            ex, ey = EAGLE_POS
            self.grid[ey][ex] = EAGLE

            # Constraint 1: Base Safety
            # Eagle tile (12,24) must be surrounded by at least 1 full ring of Brick (1) or Steel (2)
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if dx == 0 and dy == 0: continue
                    nx, ny = ex + dx, ey + dy
                    if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                        # Base ring is brick by default
                        self.grid[ny][nx] = BRICK
            
            # Level specific adjustments for Base Safety
            if level == 1:
                # 2 rings of brick
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        if abs(dx) <= 1 and abs(dy) <= 1: continue
                        nx, ny = ex + dx, ey + dy
                        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                            self.grid[ny][nx] = BRICK

            # Boss Level special layout
            if level == 'B':
                self._generate_boss_level()
                break

            # Fill the rest using CSP-like approach (Randomized with constraints)
            if self._fill_map_csp(level):
                if self.is_valid_map():
                    break

    def _fill_map_csp(self, level):
        # We'll use a simplified CSP: iterate through tiles and pick from domain
        # with density and fairness constraints.
        
        # Determine weights based on level
        if level == 1:
            weights = {BRICK: 0.15, STEEL: 0.02, WATER: 0.03, FOREST: 0.05}
        elif level == 2:
            weights = {BRICK: 0.12, STEEL: 0.08, WATER: 0.05, FOREST: 0.05}
        else:
            weights = {BRICK: 0.10, STEEL: 0.10, WATER: 0.05, FOREST: 0.05}

        tiles_to_fill = []
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                # Skip eagle and its protection ring
                if self.grid[y][x] != EMPTY: continue
                # Skip spawn zones (top row)
                if y == 0 and (x == 0 or x == 12 or x == 24): continue
                
                # Proximity to spawns/eagle for Steel/Water prevention
                is_near_critical = False
                for sx, sy in ENEMY_SPAWNS + [EAGLE_POS]:
                    if abs(x - sx) + abs(y - sy) <= 2:
                        is_near_critical = True
                        break
                
                # Fairness: No block within distance of player start (4,24)
                if abs(x - PLAYER_SPAWN[0]) + abs(y - PLAYER_SPAWN[1]) < 8: continue
                
                tiles_to_fill.append((x, y, is_near_critical))

        random.shuffle(tiles_to_fill)
        
        wall_count = sum(row.count(BRICK) + row.count(STEEL) + row.count(WATER) for row in self.grid)
        max_walls = int(TOTAL_TILES * MAX_WALL_DENSITY)

        for info in tiles_to_fill:
            x, y = info[0], info[1]
            if wall_count >= max_walls:
                break
            
            # Pick a tile type based on weights
            r = random.random()
            cumulative = 0
            chosen = EMPTY
            for t, w in weights.items():
                cumulative += w
                if r < cumulative:
                    # If near spawn/eagle, don't place Steel(2) or Water(3)
                    if info[2] and t in [STEEL, WATER]:
                        chosen = BRICK # Downgrade to brick if near critical
                    else:
                        chosen = t
                    break
            
            if chosen != EMPTY:
                self.grid[y][x] = chosen
                wall_count += 1
        
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
        for _ in range(20):
            rx, ry = random.randint(8, 17), random.randint(8, 17)
            if (rx, ry) != BOSS_SPAWN and (rx, ry) != BOSS_PLAYER_SPAWN:
                self.grid[ry][rx] = BRICK
        
        # Steel pillar clusters (2x2)
        pillars = [(9,9), (15,15)]
        for px, py in pillars:
            for dx in range(2):
                for dy in range(2):
                    self.grid[py+dy][px+dx] = STEEL
        
        # Water patch (2x3) bottom-left of arena
        for dx in range(3):
            for dy in range(2):
                self.grid[16+dy][8+dx] = WATER

    def is_valid_map(self):
        # BFS Reachability check from all spawns to Eagle
        for sx, sy in ENEMY_SPAWNS:
            if not self._can_reach(sx, sy, EAGLE_POS[0], EAGLE_POS[1]):
                return False
        return True

    def _can_reach(self, sx, sy, tx, ty):
        queue = collections.deque([(sx, sy)])
        visited = set([(sx, sy)])
        while queue:
            cx, cy = queue.popleft()
            if cx == tx and cy == ty:
                return True
            for dx, dy in [UP, DOWN, LEFT, RIGHT]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    # Passable: Empty, Forest, Brick (since tanks can destroy brick to reach)
                    if self.grid[ny][nx] in [EMPTY, FOREST, BRICK] and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append((nx, ny))
        return False

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
