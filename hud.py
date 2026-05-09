import pygame
from constants import *

class HUD:
    def __init__(self):
        self.font = pygame.font.SysFont('Arial', 18, bold=True)
        self.big_font = pygame.font.SysFont('Arial', 48, bold=True)

    def draw(self, screen, player_lives, enemies_left, level, game_state):
        # HUD Panel background
        hud_rect = pygame.Rect(GAME_AREA_WIDTH, 0, HUD_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(screen, COLOR_HUD, hud_rect)
        pygame.draw.line(screen, (255, 255, 255), (GAME_AREA_WIDTH, 0), (GAME_AREA_WIDTH, SCREEN_HEIGHT), 2)

        # Stats
        y_offset = 20
        self._draw_text(screen, f"LEVEL: {level}", (GAME_AREA_WIDTH + 10, y_offset))
        y_offset += 40
        self._draw_text(screen, f"LIVES: {player_lives}", (GAME_AREA_WIDTH + 10, y_offset))
        y_offset += 40
        self._draw_text(screen, f"ENEMIES:", (GAME_AREA_WIDTH + 10, y_offset))
        y_offset += 25
        self._draw_text(screen, f"  {enemies_left}", (GAME_AREA_WIDTH + 10, y_offset))

        # Game Over / Stage Clear Overlay
        if game_state == "GAME_OVER":
            self._draw_overlay(screen, "GAME OVER", (255, 0, 0))
        elif game_state == "STAGE_CLEAR":
            self._draw_overlay(screen, "STAGE CLEAR", (0, 255, 0))

    def _draw_text(self, screen, text, pos, color=COLOR_TEXT):
        surface = self.font.render(text, True, color)
        screen.blit(surface, pos)

    def _draw_overlay(self, screen, text, color):
        surface = self.big_font.render(text, True, color)
        rect = surface.get_rect(center=(GAME_AREA_WIDTH // 2, SCREEN_HEIGHT // 2))
        # Semi-transparent background
        bg_rect = pygame.Rect(0, 0, GAME_AREA_WIDTH, SCREEN_HEIGHT)
        s = pygame.Surface((GAME_AREA_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        screen.blit(s, (0,0))
        screen.blit(surface, rect)
