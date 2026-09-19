import pygame
from assets_loader import assets

class TrashCan:
    def __init__(self, x: int = 18, y: int = 112, width: int = 32, height: int = 46):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.is_hovered = False

    def contains_point(self, pos: tuple[int, int]) -> bool:
        return self.rect.inflate(8, 8).collidepoint(pos)

    def draw(self, surface: pygame.Surface):
        # Shadow on tabletop
        shadow_rect = pygame.Rect(self.x + 2, self.y + self.height - 4, self.width, 6)
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 70))
        surface.blit(shadow_surf, (shadow_rect.x, shadow_rect.y))

        # Color palette: Retro green/gray stainless trash bin
        body_col = (110, 130, 115) if not self.is_hovered else (130, 160, 135)
        border_col = (50, 65, 55)
        rim_col = (150, 175, 155) if not self.is_hovered else (180, 215, 185)
        dark_slit = (35, 45, 38)

        # Body
        body_rect = pygame.Rect(self.x + 2, self.y + 10, self.width - 4, self.height - 10)
        pygame.draw.rect(surface, body_col, body_rect)
        pygame.draw.rect(surface, border_col, body_rect, 1)

        # Vertical ribbed texture
        for gx in range(self.x + 7, self.x + self.width - 6, 5):
            pygame.draw.line(surface, (90, 110, 95), (gx, self.y + 12), (gx, self.y + self.height - 3), 1)

        # Lid / Top Rim (angled perspective)
        lid_rect = pygame.Rect(self.x, self.y + 4, self.width, 8)
        pygame.draw.rect(surface, rim_col, lid_rect)
        pygame.draw.rect(surface, border_col, lid_rect, 1)

        # Inner opening slit
        pygame.draw.rect(surface, dark_slit, (self.x + 4, self.y + 6, self.width - 8, 4))

        # Trash icon / Label
        label_surf = assets.render_text("SAMPAH", color=(240, 240, 240) if self.is_hovered else (200, 205, 200))
        surface.blit(label_surf, (self.rect.centerx - label_surf.get_width() // 2, self.y + 20))

        # Mini trash symbol (small white trash bin glyph)
        icon_cx = self.rect.centerx
        icon_y = self.y + 32
        pygame.draw.rect(surface, (230, 230, 230), (icon_cx - 4, icon_y, 8, 6))
        pygame.draw.line(surface, (100, 100, 100), (icon_cx - 2, icon_y + 1), (icon_cx - 2, icon_y + 4), 1)
        pygame.draw.line(surface, (100, 100, 100), (icon_cx + 1, icon_y + 1), (icon_cx + 1, icon_y + 4), 1)
