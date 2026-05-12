import collections
import random

def decide(tank, game_state):
    grid = game_state['grid']
    player_pos = game_state['player_pos']
    eagle_pos = game_state['eagle_pos']
    current_pos = (tank.x, tank.y)
    
    # 1. SHOOT: Check if player or eagle is in line of sight
    action = check_targets_in_line(tank, player_pos, eagle_pos, grid)
    if action:
        return action

    # 2. PATHFINDING: Move towards Eagle
    path_blocked = False
    if tank.path:
        next_step = tank.path[0]
        if grid[next_step[1]][next_step[0]] not in [0, 4, 5]:
            path_blocked = True
        else:
            for other in game_state['tanks']:
                if other != tank and other.active and (other.x, other.y) == next_step:
                    path_blocked = True
                    break

    if not tank.path or path_blocked or tank.ticks_since_path > 100:
        tank.path = run_bfs(current_pos, eagle_pos, grid)
        tank.ticks_since_path = 0

    if tank.path:
        next_step = tank.path[0]
        direction = (next_step[0] - tank.x, next_step[1] - tank.y)
        return ('move', get_dir_name(direction))

    # 3. FALLBACK: Random move or wait
    return ('move', random.choice(['up', 'down', 'left', 'right']))

def run_bfs(start, goal, grid):
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
                # Basic tanks only pass through EMPTY, FOREST, EAGLE
                if grid[ny][nx] in [0, 4, 5] and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)]))
    return None

def check_targets_in_line(tank, player_pos, eagle_pos, grid):
    targets = []
    if player_pos: targets.append(player_pos)
    targets.append(eagle_pos)
    
    tx, ty = tank.x, tank.y
    for px, py in targets:
        if tx == px:
            step = 1 if py > ty else -1
            clear = True
            for y in range(ty + step, py, step):
                if grid[y][tx] in [1, 2, 3]:
                    clear = False
                    break
            if clear: return ('shoot', 'down' if py > ty else 'up')
        
        if ty == py:
            step = 1 if px > tx else -1
            clear = True
            for x in range(tx + step, px, step):
                if grid[ty][x] in [1, 2, 3]:
                    clear = False
                    break
            if clear: return ('shoot', 'right' if px > tx else 'left')
    return None

def get_dir_name(d):
    return {(0, -1): 'up', (0, 1): 'down', (-1, 0): 'left', (1, 0): 'right'}.get(d, 'down')
