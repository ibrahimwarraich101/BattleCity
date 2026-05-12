import os, sys, pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'
sys.path.insert(0, os.path.abspath('.'))
from constants import *
pygame.init()

from main import Game

game = Game()
game.start_splash(2)
for _ in range(STAGE_SPLASH_TIME + 1):
    game.update()

print("Waiting for first enemy to spawn...")
for i in range(300):
    game.update()
    if game.enemies:
        e = game.enemies[0]
        if i % 30 == 0:
            print(f"  Tick {i}: enemy type={e.tank_type} pos=({e.x},{e.y}) path_len={len(e.path)} move_cd={e.move_cooldown}")

if not game.enemies:
    print("ERROR: No enemies spawned!")
    sys.exit(1)

e = game.enemies[0]
start_pos = (e.x, e.y)
print(f"\nTracking enemy from ({e.x},{e.y}) for 200 more ticks...")

for i in range(200):
    game.update()

end_pos = (e.x, e.y)
print(f"End pos: ({e.x},{e.y}), moved: {start_pos != end_pos}, tiles moved: {abs(end_pos[0]-start_pos[0]) + abs(end_pos[1]-start_pos[1])}")
