import heapq
import collections
import random

def decide(tank, game_state):
    grid = game_state['grid']
    player_pos = game_state['player_pos']
    eagle_pos = game_state['eagle_pos']
    
    # State-based decision: Retreat if HP is low (hp_lost >= 3)
    if tank.hp_lost >= 3:
        return handle_retreat(tank, game_state)
    
    return handle_attack(tank, game_state)

def handle_attack(tank, game_state):
    grid = game_state['grid']
    player_pos = game_state['player_pos']
    eagle_pos = game_state['eagle_pos']
    
    # 1. SHOOT: Check line of sight to player or eagle
    from agents.basic_tank_agent import check_targets_in_line
    action = check_targets_in_line(tank, player_pos, eagle_pos, grid)
    if action:
        return action

    # 2. PATHFINDING: Move towards Eagle using A*
    current_pos = (tank.x, tank.y)
    path_blocked = False
    if tank.path:
        next_step = tank.path[0]
        if grid[next_step[1]][next_step[0]] not in [0, 1, 4, 5]: # Blocks except brick
            path_blocked = True
        else:
            for other in game_state['tanks']:
                if other != tank and other.active and (other.x, other.y) == next_step:
                    path_blocked = True
                    break

    if not tank.path or path_blocked or tank.ticks_since_path > 100:
        tank.path = run_astar(current_pos, eagle_pos, grid)
        tank.ticks_since_path = 0

    if tank.path:
        next_step = tank.path[0]
        direction = (next_step[0] - tank.x, next_step[1] - tank.y)
        dir_name = get_dir_name(direction)
        # Shoot brick if in the way
        if grid[next_step[1]][next_step[0]] == 1:
            return ('shoot', dir_name)
        return ('move', dir_name)

    return ('move', random.choice(['up', 'down', 'left', 'right']))

def handle_retreat(tank, game_state):
    grid = game_state['grid']
    
    if not hasattr(tank, 'retreat_target') or tank.retreat_target is None:
        tank.retreat_target = find_nearest_cover((tank.x, tank.y), grid)
        tank.retreat_path = []
        tank.retreat_wait = 0

    if tank.retreat_wait > 0:
        tank.retreat_wait -= 1
        if tank.retreat_wait == 0:
            tank.hp_lost = 0 # Healed
            tank.hp = 4
            tank.retreat_target = None
        return ('stay', None)

    if tank.retreat_target:
        if (tank.x, tank.y) == tank.retreat_target:
            tank.retreat_wait = 180 # 3 seconds to heal
            return ('stay', None)

        if not tank.retreat_path:
            tank.retreat_path = run_astar((tank.x, tank.y), tank.retreat_target, grid)

        if tank.retreat_path:
            next_step = tank.retreat_path[0]
            direction = (next_step[0] - tank.x, next_step[1] - tank.y)
            return ('move', get_dir_name(direction))

    return ('move', random.choice(['up', 'down', 'left', 'right']))

def run_astar(start, goal, grid):
    def h(pos):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    pq = [(h(start), 0, start, [])]
    visited = {}
    GRID_SIZE = len(grid)

    while pq:
        f, g, (cx, cy), path = heapq.heappop(pq)
        if (cx, cy) == goal: return path
        if (cx, cy) in visited and visited[(cx, cy)] <= g: continue
        visited[(cx, cy)] = g

        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                tile = grid[ny][nx]
                if tile in [2, 3]: continue # Steel/Water impassable
                cost = 1 if tile in [0, 4, 5] else 5 # High cost for bricks
                new_g = g + cost
                heapq.heappush(pq, (new_g + h((nx, ny)), new_g, (nx, ny), path + [(nx, ny)]))
    return []

def find_nearest_cover(start, grid):
    queue = collections.deque([start])
    visited = {start}
    GRID_SIZE = len(grid)
    while queue:
        cx, cy = queue.popleft()
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                if grid[ny][nx] == 2: return (cx, cy) # Adjacent to steel
                if grid[ny][nx] in [0, 4] and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
    return start

def get_dir_name(d):
    return {(0, -1): 'up', (0, 1): 'down', (-1, 0): 'left', (1, 0): 'right'}.get(d, 'down')
