import heapq
import collections
import random

# TANK TYPE 3: Armor Tank
# AI Model: Model-Based Reflex Agent (States based on hitCount)
# Search Algorithm: A* to Eagle

def decide(tank, game_state):
    grid = game_state['grid']
    player_pos = game_state['player_pos']
    eagle_pos = game_state['eagle_pos']
    GRID_SIZE = len(grid)

    # Maintain hitCount (passed from tank object)
    hit_count = tank.hp_lost

    # STATE MACHINE
    if hit_count >= 3: # CRITICALLY DAMAGED - RETREAT
        return handle_retreat(tank, game_state)
    
    # HEALTHY/DAMAGED - ATTACK
    return handle_attack(tank, game_state)

def handle_attack(tank, game_state):
    grid = game_state['grid']
    player_pos = game_state['player_pos']
    eagle_pos = game_state['eagle_pos']
    
    # Rule 1: Shoot player if in line
    from agents.basic_tank_agent import check_player_in_line
    action = check_player_in_line(tank, player_pos, grid)
    if action:
        return action

    # A* Pathfinding Logic
    current_pos = (tank.x, tank.y)
    path_blocked = False
    if tank.path:
        next_step = tank.path[0]
        for other in game_state['tanks']:
            if other != tank and other.active and (other.x, other.y) == next_step:
                path_blocked = True
                break
    
    # Re-trigger A*
    if not tank.path or path_blocked or tank.ticks_since_path > 150:
        tank.path = run_astar(current_pos, eagle_pos, grid)
        tank.ticks_since_path = 0

    # Rule 2: Follow A* path
    if tank.path:
        next_step = tank.path.pop(0)
        direction = (next_step[0] - tank.x, next_step[1] - tank.y)
        dir_name = get_dir_name(direction)
        if grid[next_step[1]][next_step[0]] == 1: # Brick
            return ('shoot', dir_name)
        return ('move', dir_name)

    return ('move', random.choice(['up', 'down', 'left', 'right']))

def handle_retreat(tank, game_state):
    # Model-Based: maintains internal state (retreating)
    if not hasattr(tank, 'retreat_target') or tank.retreat_target is None:
        tank.retreat_target = find_nearest_steel_cover((tank.x, tank.y), game_state['grid'])
        tank.retreat_path = None
        tank.retreat_wait = 0

    if tank.retreat_wait > 0:
        tank.retreat_wait -= 1
        if tank.retreat_wait == 0:
            # Healing complete (Model state update)
            tank.hp_lost = 2
            tank.retreat_target = None
        return ('stay', None)

    # Move to retreat target
    if tank.retreat_target:
        if (tank.x, tank.y) == tank.retreat_target:
            tank.retreat_wait = 60 # 2 seconds
            return ('stay', None)
        
        if not tank.retreat_path:
            tank.retreat_path = run_astar((tank.x, tank.y), tank.retreat_target, game_state['grid'])
        
        if tank.retreat_path:
            next_step = tank.retreat_path.pop(0)
            direction = (next_step[0] - tank.x, next_step[1] - tank.y)
            return ('move', get_dir_name(direction))

    return ('move', random.choice(['up', 'down', 'left', 'right']))

def run_astar(start, goal, grid):
    # A* Algorithm
    # g(n): 0,4 = 1; 1 = 3; 2,3 = inf
    # h(n): Manhattan distance
    GRID_SIZE = len(grid)
    pq = [(0, start, [])]
    visited = {}

    while pq:
        (f, (cx, cy), path) = heapq.heappop(pq)
        
        if (cx, cy) == goal:
            return path
        
        if (cx, cy) in visited and visited[(cx, cy)] <= f:
            continue
        visited[(cx, cy)] = f

        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                tile = grid[ny][nx]
                if tile in [2, 3]: continue # Impassable
                
                cost = 1 if tile in [0, 4, 5] else 3
                g = f - (abs(cx - goal[0]) + abs(cy - goal[1])) + cost
                h = abs(nx - goal[0]) + abs(ny - goal[1])
                heapq.heappush(pq, (g + h, (nx, ny), path + [(nx, ny)]))
    return None

def find_nearest_steel_cover(start, grid):
    # BFS to find nearest empty tile adjacent to a Steel Wall (2)
    queue = collections.deque([start])
    visited = {start}
    GRID_SIZE = len(grid)
    
    while queue:
        cx, cy = queue.popleft()
        # Check neighbors for steel
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                if grid[ny][nx] == 2: # Adjacent to steel
                    return (cx, cy)
                if grid[ny][nx] in [0, 4] and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
    return None

def get_dir_name(d):
    mapping = {(0, -1): 'up', (0, 1): 'down', (-1, 0): 'left', (1, 0): 'right'}
    return mapping.get(d, 'up')
