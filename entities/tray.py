from collections.abc import Callable
import pygame

from core.assets import assets
from items.registry import items_registry

COLOR_OUTLINE_HOVER = (255, 255, 255)


class DraggedItem:
    def __init__(
        self,
        item_id: str,
        pos: tuple[int, int],
        source_tray: "IngredientTray | None" = None,
        scale: float = 1.0,
        drag_offset: tuple[int, int] | None = None,
    ):
        self.item_id = item_id
        self.source_tray = source_tray
        self.scale = scale
        self.drag_offset = drag_offset
        self.item_def = items_registry.get(item_id)
        if source_tray and source_tray.hide_on_drag and source_tray.sprite:
            raw_spr = source_tray.sprite
            raw_shadow = source_tray.shadow_sprite
        else:
            raw_spr = self.item_def.sprite if self.item_def else assets.get_sprite(item_id)
            raw_shadow = (
                self.item_def.shadow_sprite
                if self.item_def
                else assets.get_shadow_sprite(item_id, alpha=90)
            )

        if scale != 1.0 and raw_spr:
            sw = int(raw_spr.get_width() * scale)
            sh = int(raw_spr.get_height() * scale)
            self.sprite = pygame.transform.smoothscale(raw_spr, (sw, sh))
            self.shadow_sprite = (
                pygame.transform.smoothscale(raw_shadow, (sw, sh))
                if raw_shadow
                else None
            )
        else:
            self.sprite = raw_spr
            self.shadow_sprite = raw_shadow

        self.pos = list(pos)

    def update(self, pos: tuple[int, int]):
        self.pos = list(pos)

    def draw(self, surface: pygame.Surface):
        if self.sprite:
            if self.drag_offset:
                x = self.pos[0] - self.drag_offset[0]
                y = self.pos[1] - self.drag_offset[1]
            else:
                x = self.pos[0] - self.sprite.get_width() // 2
                y = self.pos[1] - self.sprite.get_height() // 2

            if self.shadow_sprite:
                surface.blit(self.shadow_sprite, (x + 6, y + 8))

            surface.blit(self.sprite, (x, y))


class IngredientTray:
    def __init__(
        self,
        x: int,
        y: int,
        item_id: str,
        display_sprite_id: str | None = None,
        is_pickable: bool = True,
        hide_on_drag: bool = False,
        scale: float = 1.0,
        width: int | None = None,
        height: int | None = None,
        label: str | None = None,
        on_click: Callable[[], None] | None = None,
        visible: bool = True,
    ):
        self.x = x
        self.y = y
        self.item_id = item_id
        self.display_sprite_id = (
            display_sprite_id if display_sprite_id is not None else item_id
        )
        self.is_pickable = is_pickable
        self.hide_on_drag = hide_on_drag
        self.visible = visible
        self.is_held = False
        self.scale = scale
        self.on_click = on_click
        self.item_def = items_registry.get(item_id)
        self.label = (
            label
            if label is not None
            else (self.item_def.display_name if self.item_def else item_id)
        )
        self.is_hovered = False

        # Calculate dimensions from actual display sprite
        spr = self.sprite
        if spr:
            sw = int(spr.get_width() * scale)
            sh = int(spr.get_height() * scale)
        else:
            sw, sh = (width or 120), (height or 100)

        self.width = width if width is not None else sw
        self.height = height if height is not None else sh
        self.rect = pygame.Rect(x, y, self.width, self.height)

    @property
    def sprite(self) -> pygame.Surface | None:
        return assets.get_sprite(self.display_sprite_id) or (
            self.item_def.sprite if self.item_def else None
        )

    @property
    def shadow_sprite(self) -> pygame.Surface | None:
        return assets.get_shadow_sprite(self.display_sprite_id, alpha=80) or (
            self.item_def.shadow_sprite if self.item_def else None
        )

    def handle_mouse_down(self, pos: tuple[int, int]) -> DraggedItem | None:
        if not self.visible:
            return None
        if self.rect.inflate(16, 16).collidepoint(pos):
            if self.on_click:
                self.on_click()
            if not self.is_pickable or self.is_held:
                return None
            if self.hide_on_drag:
                self.is_held = True
            drag_offset = (pos[0] - self.x, pos[1] - self.y)
            return DraggedItem(
                self.item_id,
                pos,
                source_tray=self if self.hide_on_drag else None,
                scale=self.scale if self.hide_on_drag else 1.0,
                drag_offset=drag_offset if self.hide_on_drag else None,
            )
        return None

    def update_hover(self, pos: tuple[int, int]):
        if not self.visible or self.is_held:
            self.is_hovered = False
        else:
            self.is_hovered = self.rect.inflate(16, 16).collidepoint(pos)

    def place_on_counter(
        self,
        x: int,
        y: int,
        min_x: int = 40,
        max_x: int = 1880,
        min_y: int = 480,
        max_y: int = 1060,
    ):
        self.is_held = False
        self.x = max(min_x, min(max_x - self.width, x))
        self.y = max(min_y, min(max_y - self.height, y))
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface: pygame.Surface):
        if not self.visible or self.is_held:
            return

        spr = self.sprite
        shadow_spr = self.shadow_sprite

        if spr:
            if self.scale != 1.0:
                draw_w = int(spr.get_width() * self.scale)
                draw_h = int(spr.get_height() * self.scale)
                spr_to_draw = pygame.transform.smoothscale(spr, (draw_w, draw_h))
                shadow_to_draw = (
                    pygame.transform.smoothscale(shadow_spr, (draw_w, draw_h))
                    if shadow_spr
                    else None
                )
            else:
                spr_to_draw = spr
                shadow_to_draw = shadow_spr

            # Draw contact shadow
            if shadow_to_draw:
                surface.blit(shadow_to_draw, (self.rect.x + 4, self.rect.y + 8))

            # Hover outline effect (crisp white contour outline)
            if self.is_hovered:
                out_spr, pad = assets.get_outlined_sprite(
                    self.display_sprite_id,
                    outline_color=COLOR_OUTLINE_HOVER,
                    thickness=3,
                    scale=self.scale,
                )
                if out_spr:
                    surface.blit(out_spr, (self.rect.x - pad, self.rect.y - pad - 2))
                else:
                    surface.blit(spr_to_draw, (self.rect.x, self.rect.y))
            else:
                surface.blit(spr_to_draw, (self.rect.x, self.rect.y))
