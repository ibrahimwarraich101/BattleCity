import copy
import math
import random
from constants import *

class BossAgent:
    def __init__(self):
        self.nodes_raw = 0
        self.nodes_pruned = 0

    def decide(self, boss, game_state):
        self.nodes_raw = 0
        self.nodes_pruned = 0

        player = game_state.get('player')
        if not player or not player.active:
            return ('move', random.choice(['down', 'left', 'right'])), 0, 0

        phase_data = self.get_phase(boss.hp)
        depth = phase_data['depth']

        # Check for immediate LOS to shoot
        los_dir = self.get_los_direction(boss, player, game_state['grid'])
        if los_dir:
            return ('shoot', los_dir), 1, 1

        best_val = -float('inf')
        best_action = ('move', 'down')
        
        # Branching: Move directions
        for move_dir in ['up', 'down', 'left', 'right']:
            action = ('move', move_dir)
            new_state = self.simulate(game_state, action, is_boss=True)
            val = self.minimax(new_state, depth - 1, -float('inf'), float('inf'), False)
            
            # For logging/stats
            self.nodes_raw += self.count_nodes(depth - 1)
            
            if val > best_val:
                best_val = val
                best_action = action

        return best_action, self.nodes_raw, self.nodes_pruned

    def count_nodes(self, depth):
        # Estimated nodes without pruning: 5^depth
        return 5 ** depth

    def minimax(self, state, depth, alpha, beta, maximizing):
        self.nodes_pruned += 1
        
        if depth == 0 or self.is_terminal(state):
            return self.evaluate(state)

        if maximizing:
            val = -float('inf')
            for action in self.get_possible_actions(state['boss'], state):
                val = max(val, self.minimax(self.simulate(state, action, True), depth - 1, alpha, beta, False))
                alpha = max(alpha, val)
                if beta <= alpha: break
            return val
        else:
            val = float('inf')
            for action in self.get_possible_actions(state['player'], state):
                val = min(val, self.minimax(self.simulate(state, action, False), depth - 1, alpha, beta, True))
                beta = min(beta, val)
                if beta <= alpha: break
            return val

    def get_possible_actions(self, tank, state):
        if not tank: return [('stay', None)]
        actions = [('move', d) for d in ['up', 'down', 'left', 'right']]
        actions.append(('shoot', None))
        return actions

    def simulate(self, state, action, is_boss):
        new_state = {
            'grid': state['grid'],
            'boss': copy.copy(state['boss']),
            'player': copy.copy(state['player']) if state['player'] else None,
            'eagle_pos': state['eagle_pos']
        }
        target = new_state['boss'] if is_boss else new_state['player']
        if not target: return new_state

        atype, aval = action
        if atype == 'move':
            dx, dy = {'up': (0,-1), 'down': (0,1), 'left': (-1,0), 'right': (1,0)}[aval]
            nx, ny = target.x + dx, target.y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                if new_state['grid'][ny][nx] in [0, 4]:
                    target.x, target.y = nx, ny
        return new_state

    def evaluate(self, state):
        boss = state['boss']
        player = state['player']
        if not player: return 2000
        
        score = 0
        dist = abs(boss.x - player.x) + abs(boss.y - player.y)
        score -= dist * 5
        
        if self.get_los_direction(boss, player, state['grid']):
            score += 100
        
        score += (3 - player.hp) * 50 # Assuming player lives
        score -= (BOSS_HP_MAX - boss.hp) * 20
        
        return score

    def is_terminal(self, state):
        return not state['player'] or state['player'].hp <= 0 or state['boss'].hp <= 0

    def get_los_direction(self, boss, player, grid):
        bx, by, px, py = boss.x, boss.y, player.x, player.y
        if bx == px:
            step = 1 if py > by else -1
            for y in range(by + step, py, step):
                if grid[y][bx] in [1, 2, 3]: return None
            return 'down' if py > by else 'up'
        if by == py:
            step = 1 if px > bx else -1
            for x in range(bx + step, px, step):
                if grid[by][x] in [1, 2, 3]: return None
            return 'right' if px > bx else 'left'
        return None

    def get_phase(self, hp):
        for p, data in BOSS_PHASES.items():
            if data['hp'][0] <= hp <= data['hp'][1]: return data
        return BOSS_PHASES[3]
