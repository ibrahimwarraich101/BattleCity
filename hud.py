import pygame
from constants import *

class HUD:
    def __init__(self):
        # Use Standard System Fonts for maximum browser compatibility
        self.font_main = pygame.font.SysFont('Arial', 24, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 16)
        self.font_stat = pygame.font.SysFont('Arial', 14)
        self.font_overlay = pygame.font.SysFont('Arial', 64, bold=True)

    def draw(self, screen, player_lives, enemies_left, level, game_state, stats=(0,0)):
        # HUD Panel background with slight border
        hud_rect = pygame.Rect(GAME_AREA_WIDTH, 0, HUD_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(screen, COLOR_HUD, hud_rect)
        pygame.draw.line(screen, COLOR_CARD_BORDER, (GAME_AREA_WIDTH, 0), (GAME_AREA_WIDTH, SCREEN_HEIGHT), 2)

        # Header
        y = 30
        self._draw_text(screen, "BATTLE CITY", (GAME_AREA_WIDTH + HUD_WIDTH//2, y), center=True, color=COLOR_ACCENT)
        y += 40
        
        # Level Box
        self._draw_box(screen, GAME_AREA_WIDTH + 15, y, HUD_WIDTH - 30, 60, "LEVEL", str(level))
        y += 80
        
        # Lives Box
        self._draw_box(screen, GAME_AREA_WIDTH + 15, y, HUD_WIDTH - 30, 60, "LIVES", str(player_lives))
        y += 80
        
        # Enemies Box
        self._draw_box(screen, GAME_AREA_WIDTH + 15, y, HUD_WIDTH - 30, 60, "ENEMIES", str(enemies_left))
        y += 100

        # Minimax Stats for Boss
        if game_state in ["BOSS_FIGHT", "VICTORY"]:
            stat_rect = pygame.Rect(GAME_AREA_WIDTH + 10, y, HUD_WIDTH - 20, 110)
            pygame.draw.rect(screen, COLOR_CARD_BG, stat_rect, border_radius=8)
            pygame.draw.rect(screen, COLOR_CARD_BORDER, stat_rect, 1, border_radius=8)
            
            st_y = y + 10
            self._draw_text(screen, "AI ANALYSIS", (GAME_AREA_WIDTH + HUD_WIDTH//2, st_y), center=True, font=self.font_small, color=COLOR_ACCENT)
            st_y += 25
            self._draw_stat(screen, "RAW:", str(stats[0]), (GAME_AREA_WIDTH + 20, st_y))
            st_y += 20
            self._draw_stat(screen, "PRUNED:", str(stats[1]), (GAME_AREA_WIDTH + 20, st_y))
            st_y += 20
            ratio = stats[0] / stats[1] if stats[1] > 0 else 1
            self._draw_stat(screen, "SPEEDUP:", f"{ratio:.1f}x", (GAME_AREA_WIDTH + 20, st_y), color=COLOR_ACCENT)

        # Overlays
        if game_state == "GAME_OVER":
            self._draw_overlay(screen, "MISSION FAILED", (255, 50, 50))
        elif game_state == "STAGE_CLEAR":
            self._draw_overlay(screen, "STAGE CLEAR", COLOR_ACCENT)
        elif game_state == "VICTORY":
            self._draw_overlay(screen, "VICTORY", COLOR_ACCENT, "All threats neutralized.")

    def _draw_box(self, screen, x, y, w, h, label, value):
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(screen, COLOR_CARD_BG, rect, border_radius=10)
        pygame.draw.rect(screen, COLOR_CARD_BORDER, rect, 1, border_radius=10)
        
        lbl_surf = self.font_small.render(label, True, (150, 150, 170))
        screen.blit(lbl_surf, (x + 10, y + 8))
        
        val_surf = self.font_main.render(value, True, COLOR_SELECTED)
        screen.blit(val_surf, (x + w - val_surf.get_width() - 15, y + 25))

    def _draw_stat(self, screen, label, value, pos, color=(200, 200, 220)):
        lbl = self.font_stat.render(label, True, (150, 150, 170))
        val = self.font_stat.render(value, True, color)
        screen.blit(lbl, pos)
        screen.blit(val, (pos[0] + 75, pos[1]))

    def _draw_text(self, screen, text, pos, center=False, color=COLOR_UI_TEXT, font=None):
        if font is None: font = self.font_main
        surface = font.render(text, True, color)
        if center:
            rect = surface.get_rect(center=pos)
            screen.blit(surface, rect)
        else:
            screen.blit(surface, pos)

    def _draw_overlay(self, screen, text, color, sub_text="Press any key to continue"):
        # Dim background
        overlay = pygame.Surface((GAME_AREA_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 15, 200))
        screen.blit(overlay, (0, 0))
        
        # Main text
        surf = self.font_overlay.render(text, True, color)
        rect = surf.get_rect(center=(GAME_AREA_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        
        # Shadow
        shadow = self.font_overlay.render(text, True, (5, 5, 10))
        screen.blit(shadow, (rect.x + 4, rect.y + 4))
        screen.blit(surf, rect)
        
        # Sub text
        sub_surf = self.font_small.render(sub_text, True, (150, 150, 170))
        sub_rect = sub_surf.get_rect(center=(GAME_AREA_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(sub_surf, sub_rect)
