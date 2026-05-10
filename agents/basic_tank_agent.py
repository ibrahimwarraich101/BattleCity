import collections
import random

# TANK TYPE 1: Basic Tank
# AI Model: Simple Reflex Agent
# Search Algorithm: BFS

def decide(tank, game_state):
    grid = game_state['grid']
    player_pos = game_state['player_pos']
    eagle_pos = game_state['eagle_pos']
    current_pos = (tank.x, tank.y)
    
    # 1. SHOOT RULE: Check if player is in line of sight (same row or col, no walls)
    action = check_player_in_line(tank, player_pos, grid)
    if action:
        return action

    # BFS Pathfinding Logic
    # Re-trigger BFS: at spawn, when path is blocked, or every 150 ticks
    path_blocked = False
    if tank.path and len(tank.path) > 0:
        next_step = tank.path[0]
        # Check if next step is blocked by a wall or another tank
        if grid[next_step[1]][next_step[0]] not in [0, 4]:
            path_blocked = True
        else:
            for other in game_state['tanks']:
                if other != tank and other.active and (other.x, other.y) == next_step:
                    path_blocked = True
                    break

    if not tank.path or path_blocked or tank.ticks_since_path > 150:
        tank.path = run_bfs(current_pos, eagle_pos, grid)
        tank.ticks_since_path = 0

    # 2. MOVE RULE: Follow BFS path
    if tank.path:
        next_step = tank.path.pop(0)
        direction = (next_step[0] - tank.x, next_step[1] - tank.y)
        return ('move', get_dir_name(direction))

    # 4. FALLBACK: Random move
    return ('move', random.choice(['up', 'down', 'left', 'right']))

def run_bfs(start, goal, grid):
    # BFS: Passable tiles are 0 (Empty) and 4 (Forest)
    queue = collections.deque([(start, [])])
    visited = {start}
    GRID_SIZE = len(grid)

    while queue:
        (cx, cy), path = queue.popleft()
        if (cx, cy) == goal:
            return path

        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                # Brick (1) is NOT passable for BFS in Basic Tank
                if grid[ny][nx] in [0, 4, 5] and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)]))
    return None

def check_player_in_line(tank, player_pos, grid):
    if not player_pos: return None
    tx, ty = tank.x, tank.y
    px, py = player_pos
    
    if tx == px: # Same column
        step = 1 if py > ty else -1
        for y in range(ty + step, py, step):
            if grid[y][tx] in [1, 2, 3]: # Blocked by wall
                return None
        return ('shoot', 'down' if py > ty else 'up')
    
    if ty == py: # Same row
        step = 1 if px > tx else -1
        for x in range(tx + step, px, step):
            if grid[ty][x] in [1, 2, 3]: # Blocked by wall
                return None
        return ('shoot', 'right' if px > tx else 'left')
    
    return None

def get_dir_name(d):
    mapping = {(0, -1): 'up', (0, 1): 'down', (-1, 0): 'left', (1, 0): 'right'}
    return mapping.get(d, 'up')
