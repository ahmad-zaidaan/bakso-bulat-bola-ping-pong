import pygame
from assets_loader import assets

class Bowl:
    def __init__(self, x: int, y: int):
        self.home_x = x
        self.home_y = y
        self.x = x
        self.y = y
        
        self.sprite = assets.get_sprite("mangkok")
        self.shadow_sprite = assets.get_shadow_sprite("mangkok", alpha=70)
        self.drag_shadow_sprite = assets.get_shadow_sprite("mangkok", alpha=90)
        
        self.width = self.sprite.get_width() if self.sprite else 25
        self.height = self.sprite.get_height() if self.sprite else 20
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Drag state
        self.is_dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        # Content list: elements are dicts with {'type': str, 'offset_x': int, 'offset_y': int}
        self.ingredients = []

    def contains_point(self, pos: tuple[int, int]) -> bool:
        # Hitbox for clicking/dropping
        expanded_rect = self.rect.inflate(8, 8)
        return expanded_rect.collidepoint(pos)

    def start_drag(self, mouse_pos: tuple[int, int]):
        self.is_dragging = True
        self.drag_offset_x = mouse_pos[0] - self.x
        self.drag_offset_y = mouse_pos[1] - self.y

    def update_drag(self, mouse_pos: tuple[int, int]):
        if self.is_dragging:
            self.x = mouse_pos[0] - self.drag_offset_x
            self.y = mouse_pos[1] - self.drag_offset_y
            self.rect.topleft = (self.x, self.y)

    def reset_position(self):
        self.is_dragging = False
        self.x = self.home_x
        self.y = self.home_y
        self.rect.topleft = (self.x, self.y)

    def add_ingredient(self, item_type: str, drop_pos: tuple[int, int] = None) -> bool:
        """Add an ingredient inside the bowl with angled perspective positioning."""
        sprite = assets.get_sprite(item_type)
        sw = sprite.get_width() if sprite else 7
        sh = sprite.get_height() if sprite else 7

        if drop_pos:
            rel_x = drop_pos[0] - self.x - sw // 2
            rel_y = drop_pos[1] - self.y - sh // 2
            min_x, max_x = 2, self.width - sw - 2
            min_y, max_y = 1, 8
            rel_x = max(min_x, min(max_x, rel_x))
            rel_y = max(min_y, min(max_y, rel_y))
        else:
            count = len(self.ingredients)
            offsets = [
                (4, 3), (12, 3), (8, 6), (2, 5), (14, 5), (8, 2), (5, 7), (11, 7)
            ]
            idx = count % len(offsets)
            rel_x, rel_y = offsets[idx]

        self.ingredients.append({
            "type": item_type,
            "offset_x": rel_x,
            "offset_y": rel_y
        })
        return True

    def clear(self):
        self.ingredients.clear()

    def get_ingredient_counts(self) -> dict[str, int]:
        counts = {}
        for item in self.ingredients:
            t = item["type"]
            counts[t] = counts.get(t, 0) + 1
        return counts

    def draw(self, surface: pygame.Surface):
        # Draw sprite-shaped shadow beneath the bowl
        if self.is_dragging:
            # Floating elevation shadow
            if self.drag_shadow_sprite:
                surface.blit(self.drag_shadow_sprite, (self.x + 3, self.y + 6))
        else:
            if self.shadow_sprite:
                surface.blit(self.shadow_sprite, (self.x + 1, self.y + 2))

        # Draw base bowl
        if self.sprite:
            surface.blit(self.sprite, (self.x, self.y))
        else:
            pygame.draw.ellipse(surface, (200, 200, 200), self.rect)

        # Draw ingredients sorted by Y coordinate for angled depth/layering
        sorted_ingredients = sorted(self.ingredients, key=lambda it: it["offset_y"])
        for item in sorted_ingredients:
            spr = assets.get_sprite(item["type"])
            shadow_spr = assets.get_shadow_sprite(item["type"], alpha=60)
            draw_x = self.x + item["offset_x"]
            draw_y = self.y + item["offset_y"]
            
            # Subtle contact shadow for ingredients inside the bowl
            if shadow_spr:
                surface.blit(shadow_spr, (draw_x + 1, draw_y + 1))
            if spr:
                surface.blit(spr, (draw_x, draw_y))
