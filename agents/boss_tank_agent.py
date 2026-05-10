import copy
import math
import random
from constants import *

# TANK TYPE: Boss Tank (Tank Commander)
# AI Model: Adversarial Agent (Minimax with Alpha-Beta Pruning)
# Complexity: O(b^d) where b is branching factor (~5) and d is depth.
# Pruning significantly reduces nodes visited in average case.

class BossAgent:
    def __init__(self):
        self.nodes_without_pruning = 0
        self.nodes_with_pruning = 0

    def decide(self, boss, game_state):
        self.nodes_without_pruning = 0
        self.nodes_with_pruning = 0
        
        phase = self.get_phase(boss.hp)
        depth = phase['depth']
        
        best_val = -float('inf')
        best_action = ('stay', None)
        
        # Possible actions for Boss
        actions = self.get_actions(boss, game_state)
        
        for action in actions:
            new_state = self.apply_action(game_state, boss, action)
            # Count pruned nodes
            val = self.minimax(new_state, depth - 1, -float('inf'), float('inf'), False)
            # Count raw nodes
            self.minimax_raw(new_state, depth - 1, False)
            
            if val > best_val:
                best_val = val
                best_action = action
        
        return best_action, self.nodes_without_pruning, self.nodes_with_pruning

    def minimax(self, state, depth, alpha, beta, is_maximizing):
        self.nodes_with_pruning += 1
        
        if depth == 0 or self.is_terminal(state):
            return self.eval_heuristic(state)

        if is_maximizing:
            max_eval = -float('inf')
            for action in self.get_actions(state['boss'], state):
                eval = self.minimax(self.apply_action(state, state['boss'], action), depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            player = state['player']
            if not player: return self.eval_heuristic(state)
            
            for action in self.get_actions(player, state):
                eval = self.minimax(self.apply_action(state, player, action), depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def minimax_raw(self, state, depth, is_maximizing):
        self.nodes_without_pruning += 1
        if depth == 0 or self.is_terminal(state):
            return
        
        tank = state['boss'] if is_maximizing else state['player']
        if not tank: return
        
        for action in self.get_actions(tank, state):
            self.minimax_raw(self.apply_action(state, tank, action), depth - 1, not is_maximizing)

    def get_phase(self, hp):
        for p, data in BOSS_PHASES.items():
            if data['hp'][0] <= hp <= data['hp'][1]:
                return data
        return BOSS_PHASES[3]

    def get_actions(self, tank, state):
        # Possible actions: ['up', 'down', 'left', 'right', 'shoot']
        actions = [('move', 'up'), ('move', 'down'), ('move', 'left'), ('move', 'right'), ('shoot', None)]
        return actions

    def apply_action(self, state, tank, action):
        # Return a COPY of state with action applied
        new_state = {
            'grid': state['grid'], # Grid is static for heuristic purposes in Minimax
            'boss': copy.copy(state['boss']),
            'player': copy.copy(state['player']) if state['player'] else None,
            'eagle_pos': state['eagle_pos']
        }
        
        target = new_state['boss'] if tank == state['boss'] else new_state['player']
        if not target: return new_state
        
        type, val = action
        if type == 'move':
            # Simplified move for simulation (ignore collisions for deep heuristic)
            dx, dy = 0, 0
            if val == 'up': dy = -1
            elif val == 'down': dy = 1
            elif val == 'left': dx = -1
            elif val == 'right': dx = 1
            
            nx, ny = target.x + dx, target.y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                if new_state['grid'][ny][nx] in [0, 4]:
                    target.x, target.y = nx, ny
        elif type == 'shoot':
            # Shooting doesn't change position but heuristic accounts for LOS
            pass
            
        return new_state

    def is_terminal(self, state):
        if not state['player'] or state['player'].hp <= 0: return True
        if state['boss'].hp <= 0: return True
        return False

    def eval_heuristic(self, state):
        boss = state['boss']
        player = state['player']
        if not player: return 1000
        
        grid = state['grid']
        score = 0
        
        # 1. Manhattan Distance
        dist = abs(boss.x - player.x) + abs(boss.y - player.y)
        if dist <= 3:
            score += 60
        
        # 2. Line of Sight
        if self.has_los(boss, player, grid):
            score += 50
            
        # 3. Adjacency to Steel
        if self.is_near_steel(boss, grid):
            score += 30
            
        # 4. HP Difference
        score += (PLAYER_LIVES - player.hp) * 20 # Assuming player hp here is current lives
        score -= (BOSS_HP_MAX - boss.hp) * 40
        
        # 5. Forest Penalty
        if grid[player.y][player.x] == 4:
            score -= 20
            
        return score

    def has_los(self, b, p, grid):
        if b.x == p.x:
            step = 1 if p.y > b.y else -1
            for y in range(b.y + step, p.y, step):
                if grid[y][b.x] in [1, 2, 3]: return False
            return True
        if b.y == p.y:
            step = 1 if p.x > b.x else -1
            for x in range(b.x + step, p.x, step):
                if grid[b.y][x] in [1, 2, 3]: return False
            return True
        return False

    def is_near_steel(self, b, grid):
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx, ny = b.x + dx, b.y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                if grid[ny][nx] == 2: return True
        return False
