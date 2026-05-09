import random

# TANK TYPE 2: Fast Tank
# AI Model: Goal-Based Agent (Ignores player)
# Search Algorithm: Greedy Best-First (1-step)

def decide(tank, game_state):
    grid = game_state['grid']
    eagle_pos = game_state['eagle_pos']
    GRID_SIZE = len(grid)
    
    # h(n) = Manhattan distance to Eagle
    def h(pos):
        return abs(pos[0] - eagle_pos[0]) + abs(pos[1] - eagle_pos[1])

    neighbors = [
        ('up', (tank.x, tank.y - 1)),
        ('down', (tank.x, tank.y + 1)),
        ('left', (tank.x - 1, tank.y)),
        ('right', (tank.x + 1, tank.y))
    ]

    # Filter valid neighbors (within grid)
    valid_neighbors = []
    for d, pos in neighbors:
        if 0 <= pos[0] < GRID_SIZE and 0 <= pos[1] < GRID_SIZE:
            valid_neighbors.append((d, pos))

    # 1. WALL AHEAD RULE: If greedy-best neighbor is Brick, shoot it
    # Find the neighbor with the lowest h(n) regardless of block (except Steel/Water)
    greedy_choice = None
    min_dist = float('inf')
    for d, pos in valid_neighbors:
        tile = grid[pos[1]][pos[0]]
        if tile not in [2, 3]: # Steel and Water are impassable
            dist = h(pos)
            if dist < min_dist:
                min_dist = dist
                greedy_choice = (d, pos)

    if greedy_choice:
        d, pos = greedy_choice
        if grid[pos[1]][pos[0]] == 1: # Brick
            return ('shoot', d)
        
        # 2. MOVE RULE: If passable, move there
        # Check if tile is occupied by another tank
        tank_blocking = False
        for other in game_state['tanks']:
            if other != tank and other.active and (other.x, other.y) == pos:
                tank_blocking = True
                break
        
        if not tank_blocking:
            return ('move', d)

    # 3. LOCAL MINIMA: If all 4 neighbors are blocked
    # Pick a random non-Steel, non-Water direction and shoot
    possible_shoot = [d for d, pos in valid_neighbors if grid[pos[1]][pos[0]] not in [2, 3]]
    if possible_shoot:
        return ('shoot', random.choice(possible_shoot))
    
    return ('stay', None)
