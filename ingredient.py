import pygame

from assets_loader import assets
from settings import COLOR_TEXT_DARK, COLOR_TRAY_BG, COLOR_TRAY_BORDER


class DraggedItem:
    def __init__(self, item_type: str, pos: tuple[int, int]):
        self.item_type = item_type
        self.sprite = assets.get_sprite(item_type)
        self.shadow_sprite = assets.get_shadow_sprite(item_type, alpha=90)
        self.pos = list(pos)

    def update(self, pos: tuple[int, int]):
        self.pos = list(pos)

    def draw(self, surface: pygame.Surface):
        if self.sprite:
            x = self.pos[0] - self.sprite.get_width() // 2
            y = self.pos[1] - self.sprite.get_height() // 2

            # Sprite-shaped transparent shadow (floating 2.5D offset)
            if self.shadow_sprite:
                surface.blit(self.shadow_sprite, (x + 2, y + 3))

            # Main sprite
            surface.blit(self.sprite, (x, y))

class IngredientTray:
    def __init__(self, x: int, y: int, width: int, height: int, item_type: str, label: str):
        self.rect = pygame.Rect(x, y, width, height)
        self.item_type = item_type
        self.label = label
        self.sprite = assets.get_sprite(item_type)
        self.shadow_sprite = assets.get_shadow_sprite(item_type, alpha=60)
        self.is_hovered = False

    def handle_mouse_down(self, pos: tuple[int, int]) -> DraggedItem | None:
        if self.rect.collidepoint(pos):
            return DraggedItem(self.item_type, pos)
        return None

    def update_hover(self, pos: tuple[int, int]):
        self.is_hovered = self.rect.collidepoint(pos)

    def draw(self, surface: pygame.Surface):
        border_col = (120, 120, 130) if self.is_hovered else COLOR_TRAY_BORDER
        bg_col = (180, 180, 190) if self.is_hovered else COLOR_TRAY_BG
        
        pygame.draw.rect(surface, bg_col, self.rect)
        pygame.draw.rect(surface, border_col, self.rect, 1)

        # Draw decorative sample items inside tray with sprite shadows
        if self.sprite:
            sw = self.sprite.get_width()
            sh = self.sprite.get_height()
            cx = self.rect.centerx - sw // 2
            cy = self.rect.centery - sh // 2 - 2
            
            # Shadows
            if self.shadow_sprite:
                surface.blit(self.shadow_sprite, (cx - 3, cy + 1))
                surface.blit(self.shadow_sprite, (cx + 5, cy))
                surface.blit(self.shadow_sprite, (cx + 1, cy + 3))

            # Sprites
            surface.blit(self.sprite, (cx - 4, cy))
            surface.blit(self.sprite, (cx + 4, cy - 1))
            surface.blit(self.sprite, (cx, cy + 2))

        # Pixel-crisp label under tray
        lbl_surf = assets.render_text(self.label, color=COLOR_TEXT_DARK)
        lbl_x = self.rect.centerx - lbl_surf.get_width() // 2
        lbl_y = self.rect.bottom + 2
        surface.blit(lbl_surf, (lbl_x, lbl_y))
