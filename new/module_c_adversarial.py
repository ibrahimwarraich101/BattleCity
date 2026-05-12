from constants import *
import copy

nodes_evaluated_alpha_beta = 0

def evaluate_state(boss_x, boss_y, boss_hp, player_x, player_y, player_hp, grid, dist_map):
    score = 0
    
    # Use real pathfinding distance to avoid getting stuck in U-shapes
    dist = dist_map[boss_y][boss_x]
    score -= dist * 2
    
    # Player within 3 tiles (Manhattan is fine for the flat bonus here)
    manhattan = abs(boss_x - player_x) + abs(boss_y - player_y)
    if manhattan <= 3:
        score += 60
        
    # Player in line of sight (same row or col and no walls between)
    if boss_x == player_x:
        min_y, max_y = min(boss_y, player_y), max(boss_y, player_y)
        clear = True
        for y in range(min_y + 1, max_y):
            if grid[y][boss_x] in [BRICK, STEEL]:
                clear = False
                break
        if clear: score += 50
    elif boss_y == player_y:
        min_x, max_x = min(boss_x, player_x), max(boss_x, player_x)
        clear = True
        for x in range(min_x + 1, max_x):
            if grid[boss_y][x] in [BRICK, STEEL]:
                clear = False
                break
        if clear: score += 50
        
    # Boss adjacent to steel
    adj_steel = False
    for dx, dy in [UP, DOWN, LEFT, RIGHT]:
        nx, ny = boss_x + dx, boss_y + dy
        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
            if grid[ny][nx] == STEEL:
                adj_steel = True
                break
    if adj_steel: score += 30
    
    # HP
    player_missing = 1 - player_hp
    score += player_missing * 20
    
    boss_missing = 10 - boss_hp
    score -= boss_missing * 40
    
    # Player in forest
    if 0 <= player_x < GRID_SIZE and 0 <= player_y < GRID_SIZE:
        if grid[player_y][player_x] == FOREST:
            score -= 20
            
    return score

def get_possible_moves(x, y, grid, can_shoot):
    moves = [None] # Stand still
    for dx, dy in [UP, DOWN, LEFT, RIGHT]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
            if grid[ny][nx] not in [BRICK, STEEL, WATER, EAGLE]:
                moves.append((dx, dy))
    if can_shoot:
        moves.append("SHOOT")
    return moves

def minimax_alpha_beta(boss_x, boss_y, boss_hp, player_x, player_y, player_hp, grid, depth, alpha, beta, is_max, dist_map, boss_can_shoot):
    global nodes_evaluated_alpha_beta
    nodes_evaluated_alpha_beta += 1
    
    if depth == 0 or boss_hp <= 0 or player_hp <= 0:
        return evaluate_state(boss_x, boss_y, boss_hp, player_x, player_y, player_hp, grid, dist_map), None
        
    if is_max:
        max_eval = -float('inf')
        best_move = None
        for move in get_possible_moves(boss_x, boss_y, grid, boss_can_shoot):
            nbx, nby = boss_x, boss_y
            if move == "SHOOT":
                pass
            elif move is not None:
                nbx += move[0]
                nby += move[1]
                
            eval_val, _ = minimax_alpha_beta(nbx, nby, boss_hp, player_x, player_y, player_hp, grid, depth - 1, alpha, beta, False, dist_map, boss_can_shoot)
            if eval_val > max_eval:
                max_eval = eval_val
                best_move = move
            alpha = max(alpha, eval_val)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        best_move = None
        for move in get_possible_moves(player_x, player_y, grid, True): # Assume player can always shoot
            npx, npy = player_x, player_y
            if move == "SHOOT":
                pass
            elif move is not None:
                npx += move[0]
                npy += move[1]
                
            eval_val, _ = minimax_alpha_beta(boss_x, boss_y, boss_hp, npx, npy, player_hp, grid, depth - 1, alpha, beta, True, dist_map, boss_can_shoot)
            if eval_val < min_eval:
                min_eval = eval_val
                best_move = move
            beta = min(beta, eval_val)
            if beta <= alpha:
                break
        return min_eval, best_move
