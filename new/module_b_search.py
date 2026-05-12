import heapq
from collections import deque
from constants import *
import random
import itertools

def manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def get_neighbors(x, y):
    neighbors = []
    for dx, dy in [UP, DOWN, LEFT, RIGHT]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
            neighbors.append((nx, ny, (dx, dy)))
    return neighbors

def bfs_distance_map(start_x, start_y, grid):
    # Generates a map of shortest path distances from start
    distances = [[float('inf')] * GRID_SIZE for _ in range(GRID_SIZE)]
    distances[start_y][start_x] = 0
    queue = deque([(start_x, start_y)])
    
    while queue:
        cx, cy = queue.popleft()
        dist = distances[cy][cx]
        
        for nx, ny, _ in get_neighbors(cx, cy):
            if grid[ny][nx] not in [BRICK, STEEL, WATER]:
                if distances[ny][nx] == float('inf'):
                    distances[ny][nx] = dist + 1
                    queue.append((nx, ny))
    return distances

def bfs_pathfinding(start, target, grid, obstacles=None):
    if obstacles is None: obstacles = set()
    queue = deque([(start, [])])
    visited = set([start])
    
    while queue:
        (cx, cy), path = queue.popleft()
        
        if (cx, cy) == target:
            if len(path) > 0:
                return path[0]
            return None
            
        for nx, ny, direction in get_neighbors(cx, cy):
            if (nx, ny) not in visited and (nx, ny) not in obstacles:
                tile = grid[ny][nx]
                if tile in [EMPTY, FOREST, EAGLE]:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [direction]))
    
    free_dirs = []
    for nx, ny, direction in get_neighbors(start[0], start[1]):
        if grid[ny][nx] in [EMPTY, FOREST] and (nx, ny) not in obstacles:
            free_dirs.append(direction)
    if free_dirs:
        return random.choice(free_dirs)
        
    return None

def greedy_pathfinding(start, target, grid, obstacles=None):
    if obstacles is None: obstacles = set()
    best_dist = float('inf')
    best_dir = None
    
    for nx, ny, direction in get_neighbors(start[0], start[1]):
        if (nx, ny) in obstacles: continue
        dist = manhattan_distance((nx, ny), target)
        if dist < best_dist:
            tile = grid[ny][nx]
            if tile not in [STEEL, WATER]:
                best_dist = dist
                best_dir = direction
            
    return best_dir

def astar_pathfinding(start, target, grid, obstacles=None):
    if obstacles is None: obstacles = set()
    open_set = []
    counter = itertools.count()
    heapq.heappush(open_set, (0, next(counter), start, []))
    
    g_score = {start: 0}
    
    while open_set:
        current_f, _, (cx, cy), path = heapq.heappop(open_set)
        
        if (cx, cy) == target:
            if len(path) > 0:
                return path[0]
            return None
            
        for nx, ny, direction in get_neighbors(cx, cy):
            if (nx, ny) in obstacles: continue
            tile = grid[ny][nx]
            
            if tile in [STEEL, WATER]:
                continue
                
            cost = 1
            if tile == BRICK:
                cost = 3
                
            tentative_g = g_score[(cx, cy)] + cost
            
            if (nx, ny) not in g_score or tentative_g < g_score[(nx, ny)]:
                g_score[(nx, ny)] = tentative_g
                f_score = tentative_g + manhattan_distance((nx, ny), target)
                heapq.heappush(open_set, (f_score, next(counter), (nx, ny), path + [direction]))
                
    free_dirs = []
    for nx, ny, direction in get_neighbors(start[0], start[1]):
        if grid[ny][nx] not in [STEEL, WATER, BRICK] and (nx, ny) not in obstacles:
            free_dirs.append(direction)
    if free_dirs:
        return random.choice(free_dirs)
        
    return None

def bfs_find_nearest_cover(start, grid, obstacles=None):
    if obstacles is None: obstacles = set()
    queue = deque([(start, [])])
    visited = set([start])
    
    while queue:
        (cx, cy), path = queue.popleft()
        
        for nx, ny, _ in get_neighbors(cx, cy):
            if grid[ny][nx] == STEEL:
                if len(path) > 0:
                    return path[0]
                return None
                
        for nx, ny, direction in get_neighbors(cx, cy):
            if (nx, ny) not in visited and (nx, ny) not in obstacles:
                tile = grid[ny][nx]
                if tile in [EMPTY, FOREST]:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [direction]))
                    
    return None
