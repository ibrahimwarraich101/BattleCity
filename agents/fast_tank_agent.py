import random

def decide(tank, game_state):
    grid = game_state['grid']
    eagle_pos = game_state['eagle_pos']
    GRID_SIZE = len(grid)
    
    def h(pos):
        return abs(pos[0] - eagle_pos[0]) + abs(pos[1] - eagle_pos[1])

    def is_tank_at(pos):
        for other in game_state['tanks']:
            if other != tank and other.active and (other.x, other.y) == pos:
                return True
        return False

    neighbors = [
        ('up', (tank.x, tank.y - 1)),
        ('down', (tank.x, tank.y + 1)),
        ('left', (tank.x - 1, tank.y)),
        ('right', (tank.x + 1, tank.y))
    ]

    valid_neighbors = [(d, pos) for d, pos in neighbors if 0 <= pos[0] < GRID_SIZE and 0 <= pos[1] < GRID_SIZE]

    # Fast tanks prioritize movement over shooting but will shoot bricks
    passable = []
    for d, pos in valid_neighbors:
        tile = grid[pos[1]][pos[0]]
        if tile not in [2, 3] and not is_tank_at(pos):
            passable.append((d, pos))

    if passable:
        # Find best direction based on heuristic
        best_d, best_pos = min(passable, key=lambda x: h(x[1]))
        
        # If brick is in the way, shoot it
        if grid[best_pos[1]][best_pos[0]] == 1:
            return ('shoot', best_d)
        return ('move', best_d)

    # If stuck, try to shoot bricks or move randomly
    possible_bricks = [d for d, pos in valid_neighbors if grid[pos[1]][pos[0]] == 1]
    if possible_bricks:
        return ('shoot', random.choice(possible_bricks))
    
    return ('move', random.choice(['up', 'down', 'left', 'right']))
