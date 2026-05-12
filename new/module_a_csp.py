from constants import *
from collections import deque
import random

def get_neighbors(x, y):
    return [(x+dx, y+dy) for dx, dy in [UP, DOWN, LEFT, RIGHT] 
            if 0 <= x+dx < GRID_SIZE and 0 <= y+dy < GRID_SIZE]

def is_reachable(grid, start_points, target):
    # BFS to ensure all start_points can reach target
    for sx, sy in start_points:
        visited = set()
        queue = deque([(sx, sy)])
        visited.add((sx, sy))
        found = False
        
        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) == target:
                found = True
                break
                
            for nx, ny in get_neighbors(cx, cy):
                if (nx, ny) not in visited:
                    tile = grid[ny][nx]
                    # Can pass through EMPTY, FOREST. Water blocks tanks. 
                    # Brick/Steel block BFS unless we consider destroying walls. 
                    # Constraint 2 says "Valid BFS path... must exist". 
                    # We assume it means empty/forest path, OR perhaps a path breaking bricks is allowed?
                    # Let's assume a strict empty/forest path for guaranteed reachability without shooting.
                    if tile in [EMPTY, FOREST, EAGLE]:
                        visited.add((nx, ny))
                        queue.append((nx, ny))
                        
        if not found:
            return False
            
    return True

def generate_map(level):
    # Initialize empty grid
    grid = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    
    # Fixed positions
    spawns = [(0, 0), (12, 0), (24, 0)]
    player_start = (4, 24)
    eagle_pos = (12, 24)
    
    grid[eagle_pos[1]][eagle_pos[0]] = EAGLE
    
    # Base Safety Constraint
    # Surround Eagle with Brick (level 1) or mix of Brick/Steel (level 2)
    base_ring = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0)]
    for dx, dy in base_ring:
        rx, ry = eagle_pos[0] + dx, eagle_pos[1] + dy
        if level == 1:
            grid[ry][rx] = BRICK
        else:
            grid[ry][rx] = random.choice([BRICK, BRICK, STEEL])
            
    # Protect spawns and player start from being walled in immediately
    protected_tiles = set(spawns)
    protected_tiles.add(player_start)
    protected_tiles.add(eagle_pos)
    for dx, dy in base_ring:
        protected_tiles.add((eagle_pos[0]+dx, eagle_pos[1]+dy))
        
    for sx, sy in spawns:
        for nx, ny in get_neighbors(sx, sy): protected_tiles.add((nx, ny))
    for nx, ny in get_neighbors(player_start[0], player_start[1]): protected_tiles.add((nx, ny))

    # CSP variables: The remaining empty tiles
    # Domains: EMPTY, BRICK, STEEL, WATER, FOREST
    
    num_walls = 0
    max_walls = int(GRID_SIZE * GRID_SIZE * 0.3) # Max 30% to be safe (<40%)
    
    # Number of elements based on level
    if level == 1:
        target_bricks = 150
        target_steel = 10
        target_water = 10
        target_forest = 30
    elif level == 2:
        target_bricks = 100
        target_steel = 40
        target_water = 20
        target_forest = 40
    else: # Boss
        target_bricks = 30
        target_steel = 20
        target_water = 5
        target_forest = 10

    elements_to_place = (
        [BRICK] * target_bricks + 
        [STEEL] * target_steel + 
        [WATER] * target_water + 
        [FOREST] * target_forest
    )
    
    random.shuffle(elements_to_place)
    
    all_coords = [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE)]
    random.shuffle(all_coords)

    # Simplified Backtracking/Iterative Placement
    for tile_type in elements_to_place:
        placed = False
        for i in range(len(all_coords)):
            x, y = all_coords[i]
            if grid[y][x] == EMPTY and (x, y) not in protected_tiles:
                # Try placing
                grid[y][x] = tile_type
                
                # Check reachability constraint (Forward Checking)
                # We only need to check if the path is still reachable.
                # Since BFS reachability is strict (no walls), placing a wall/water might block it.
                if tile_type in [BRICK, STEEL, WATER]:
                    if is_reachable(grid, spawns, eagle_pos):
                        placed = True
                        all_coords.pop(i)
                        break
                    else:
                        # Backtrack
                        grid[y][x] = EMPTY
                else:
                    # Forest doesn't block
                    placed = True
                    all_coords.pop(i)
                    break
        
        if not placed:
            # Could not place without violating constraints, skip
            pass

    return grid
