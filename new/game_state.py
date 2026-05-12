from constants import *
from entities import *
import random

class GameState:
    def __init__(self):
        self.grid = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.player = PlayerTank(4, 24)
        self.enemies = []
        self.bullets = []
        self.eagle_alive = True
        self.game_over = False
        self.win = False
        
        self.enemy_pool = []
        self.spawns = [(0, 0), (12, 0), (24, 0)]
        self.spawn_timer = 0
        self.kills = 0
        self.level = 1
        
        pass

    def load_enemy_pool(self, level):
        import module_a_csp
        self.grid = module_a_csp.generate_map(level)
        self.level = level
        self.enemy_pool = []
        if level == 1:
            # 7 Basic + 5 Fast
            for _ in range(7): self.enemy_pool.append("basic")
            for _ in range(5): self.enemy_pool.append("fast")
        elif level == 2:
            # 4 Fast, 3 Armor
            for _ in range(4): self.enemy_pool.append("fast")
            for _ in range(3): self.enemy_pool.append("armor")
        elif level == 3: # Boss level
            self.enemy_pool.append("boss")

    def is_valid_move(self, x, y):
        if x < 0 or x >= GRID_SIZE or y < 0 or y >= GRID_SIZE:
            return False
        tile = self.grid[y][x]
        if tile in [BRICK, STEEL, WATER, EAGLE]:
            return False
        # Tank collision
        if self.player.x == x and self.player.y == y:
            return False
        for e in self.enemies:
            if e.x == x and e.y == y:
                return False
        return True

    def move_tank(self, tank, direction):
        if not tank.can_move():
            return False
        
        tank.direction = direction
        nx, ny = tank.x + direction[0], tank.y + direction[1]
        
        if self.is_valid_move(nx, ny):
            tank.x, tank.y = nx, ny
            tank.reset_move_cooldown()
            return True
        return False

    def shoot_bullet(self, tank, owner_type):
        if tank.can_fire():
            tank.reset_fire_cooldown()
            self.bullets.append(Bullet(tank.x, tank.y, tank.direction, owner_type))

    def update_ai_decisions(self):
        import module_b_search
        import module_c_adversarial
        
        eagle_pos = (12, 24)
        
        # Build set of obstacle positions (all tanks)
        tank_positions = set((e.x, e.y) for e in self.enemies)
        tank_positions.add((self.player.x, self.player.y))
        
        for e in self.enemies:
            # Only decide if it can do something
            if not e.can_move() and not e.can_fire():
                continue
                
            # Treat other tanks as obstacles
            obstacles = tank_positions.copy()
            if (e.x, e.y) in obstacles:
                obstacles.remove((e.x, e.y))
                
            if e.tank_type == "basic":
                if e.can_move():
                    move = module_b_search.bfs_pathfinding((e.x, e.y), eagle_pos, self.grid, obstacles)
                    if move:
                        self.move_tank(e, move)
                if e.can_fire():
                    if e.x == self.player.x:
                        min_y, max_y = min(e.y, self.player.y), max(e.y, self.player.y)
                        clear = True
                        for y in range(min_y + 1, max_y):
                            if self.grid[y][e.x] in [BRICK, STEEL]:
                                clear = False
                                break
                        if clear:
                            e.direction = DOWN if self.player.y > e.y else UP
                            self.shoot_bullet(e, 'enemy')
                    elif e.y == self.player.y:
                        min_x, max_x = min(e.x, self.player.x), max(e.x, self.player.x)
                        clear = True
                        for x in range(min_x + 1, max_x):
                            if self.grid[e.y][x] in [BRICK, STEEL]:
                                clear = False
                                break
                        if clear:
                            e.direction = RIGHT if self.player.x > e.x else LEFT
                            self.shoot_bullet(e, 'enemy')
                        
            elif e.tank_type == "fast":
                if e.can_move():
                    move = module_b_search.greedy_pathfinding((e.x, e.y), eagle_pos, self.grid, obstacles)
                    if move:
                        # Wall Rule: IF next tile is Brick THEN shoot
                        nx, ny = e.x + move[0], e.y + move[1]
                        if self.grid[ny][nx] == BRICK and e.can_fire():
                            e.direction = move
                            self.shoot_bullet(e, 'enemy')
                        else:
                            self.move_tank(e, move)
                            
            elif e.tank_type == "armor":
                if e.can_move():
                    if getattr(e, 'retreat_timer', 0) > 0:
                        e.retreat_timer -= 1
                    elif e.hp <= e.max_hp - 3 and not getattr(e, 'retreating', False):
                        move = module_b_search.bfs_find_nearest_cover((e.x, e.y), self.grid, obstacles)
                        if move: 
                            self.move_tank(e, move)
                        else:
                            # Either reached cover or no cover exists. Wait 2s (20 ticks)
                            e.retreating = True
                            e.retreat_timer = 20
                    else:
                        e.retreating = False
                        move = module_b_search.astar_pathfinding((e.x, e.y), eagle_pos, self.grid, obstacles)
                        if move:
                            nx, ny = e.x + move[0], e.y + move[1]
                            if self.grid[ny][nx] == BRICK and e.can_fire():
                                e.direction = move
                                self.shoot_bullet(e, 'enemy')
                            else:
                                self.move_tank(e, move)
                                
            elif e.tank_type == "boss":
                if e.can_move() or e.can_fire():
                    depth = 2
                    if 3 <= e.hp <= 6: depth = 3
                    elif e.hp <= 2: depth = 4
                    
                    dist_map = module_b_search.bfs_distance_map(self.player.x, self.player.y, self.grid)
                    
                    _, move = module_c_adversarial.minimax_alpha_beta(
                        e.x, e.y, e.hp, self.player.x, self.player.y, self.player.hp, 
                        self.grid, depth, -float('inf'), float('inf'), True,
                        dist_map, e.can_fire()
                    )
                    
                    if move == "SHOOT" and e.can_fire():
                        # Face player before shooting
                        if abs(self.player.x - e.x) >= abs(self.player.y - e.y):
                            e.direction = RIGHT if self.player.x > e.x else LEFT
                        else:
                            e.direction = DOWN if self.player.y > e.y else UP
                        self.shoot_bullet(e, 'enemy')
                    elif move and move != "SHOOT" and e.can_move():
                        self.move_tank(e, move)

    def update_tick(self):
        if self.game_over or self.win:
            return

        # 1. Update cooldowns
        self.player.update_cooldowns()
        for e in self.enemies:
            e.update_cooldowns()

        # 2. Bullet Update & Collisions
        self._update_bullets()

        # 3. State Update (remove dead tanks)
        self.enemies = [e for e in self.enemies if e.hp > 0]
        if self.player.hp <= 0:
            self.player.lives -= 1
            if self.player.lives <= 0:
                self.game_over = True
            else:
                self.player.hp = 1
                self.player.x, self.player.y = 4, 24 # Respawn

        # 4. Spawn Check
        if len(self.enemies) < 3 and len(self.enemy_pool) > 0 and self.spawn_timer >= 20: # 2 seconds between spawns
            spawn_type = self.enemy_pool.pop(0)
            sx, sy = random.choice(self.spawns)
            # Check if spawn is clear
            clear = True
            for e in self.enemies:
                if e.x == sx and e.y == sy: clear = False
            if self.player.x == sx and self.player.y == sy: clear = False
            
            if clear:
                if spawn_type == "basic": self.enemies.append(BasicTank(sx, sy))
                elif spawn_type == "fast": self.enemies.append(FastTank(sx, sy))
                elif spawn_type == "armor": self.enemies.append(ArmorTank(sx, sy))
                elif spawn_type == "boss": self.enemies.append(BossTank(sx, sy))
                self.spawn_timer = 0
            else:
                self.enemy_pool.insert(0, spawn_type) # retry later

        self.spawn_timer += 1

        if len(self.enemy_pool) == 0 and len(self.enemies) == 0:
            self.win = True

    def _update_bullets(self):
        active_bullets = []
        for b in self.bullets:
            b.x += b.direction[0]
            b.y += b.direction[1]
            
            # Boundary check
            if b.x < 0 or b.x >= GRID_SIZE or b.y < 0 or b.y >= GRID_SIZE:
                continue

            hit = False
            
            # Terrain hit
            tile = self.grid[b.y][b.x]
            if tile == BRICK:
                self.grid[b.y][b.x] = EMPTY
                hit = True
            elif tile == STEEL:
                hit = True
            elif tile == EAGLE:
                self.eagle_alive = False
                self.game_over = True
                hit = True
                
            # Tank hit
            if not hit:
                if b.owner_type == 'enemy' and b.x == self.player.x and b.y == self.player.y:
                    self.player.hp -= 1
                    hit = True
                elif b.owner_type == 'player':
                    for e in self.enemies:
                        if b.x == e.x and b.y == e.y:
                            e.hp -= 1
                            if e.hp <= 0:
                                self.kills += 1
                            hit = True
                            break

            if not hit:
                active_bullets.append(b)
                
        self.bullets = active_bullets
