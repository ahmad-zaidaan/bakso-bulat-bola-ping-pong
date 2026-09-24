from collections.abc import Callable

import pygame

from core.assets import assets
from ui.control import AlignSelf, Control

COLOR_BLACK = (0, 0, 0)


class Label(Control):
    def __init__(
        self,
        text: str,
        font_size: int = 28,
        color: tuple[int, int, int] = COLOR_BLACK,
        has_shadow: bool = False,
        shadow_color: tuple[int, int, int] = (30, 20, 10),
        margin: tuple[int, ...] | int = 0,
        align_self: AlignSelf = "auto",
        visible: bool = True,
    ):
        super().__init__(margin=margin, align_self=align_self, visible=visible)
        self.text = str(text)
        self.font_size = font_size
        self.color = color
        self.has_shadow = has_shadow
        self.shadow_color = shadow_color

    def set_text(self, text: str):
        self.text = str(text)
        self.queue_reflow()

    def get_minimum_size(self) -> tuple[int, int]:
        w = assets.get_text_width(self.text, size=self.font_size)
        h = assets.get_text_height(self.text, size=self.font_size)
        pt, pr, pb, pl = self.padding
        return w + pl + pr, h + pt + pb

    def draw(self, surface: pygame.Surface, mouse_pos: tuple[int, int]):
        if not self.visible:
            return
        super().draw(surface, mouse_pos)
        pt, pr, pb, pl = self.padding
        if self.has_shadow:
            surf = assets.render_text_with_shadow(
                self.text,
                size=self.font_size,
                color=self.color,
                shadow_color=self.shadow_color,
                offset=(2, 2),
            )
        else:
            surf = assets.render_text(
                self.text,
                size=self.font_size,
                color=self.color,
            )
        surface.blit(surf, (self.rect.x + pl, self.rect.y + pt))


class Button(Control):
    def __init__(
        self,
        text: str,
        on_click: Callable[[], None] | None = None,
        width: int = 220,
        height: int = 64,
        font_size: int = 26,
        padding: tuple[int, ...] | int = (4, 12),
        margin: tuple[int, ...] | int = 0,
        flex_grow: float = 0.0,
        align_self: AlignSelf = "auto",
        use_texture: bool = True,
        texture_id: str = "button",
        slice_margin: int = 32,
        bg_color: tuple[int, int, int] = (235, 150, 50),
        hover_color: tuple[int, int, int] = (255, 255, 255),
        active_color: tuple[int, int, int] = (90, 190, 95),
        border_color: tuple[int, int, int] = (120, 70, 25),
        border_width: int = 0,
        text_color: tuple[int, int, int] = COLOR_BLACK,
        shadow_color: tuple[int, int, int] | None = None,
        is_active: bool = False,
        visible: bool = True,
    ):
        super().__init__(
            width=width,
            height=height,
            padding=padding,
            margin=margin,
            flex_grow=flex_grow,
            align_self=align_self,
            bg_color=bg_color,
            border_color=border_color,
            border_width=border_width,
            visible=visible,
        )
        self.text = str(text)
        self.font_size = font_size
        self.on_click = on_click
        self.use_texture = use_texture
        self.texture_id = texture_id
        self.slice_margin = slice_margin
        self.hover_color = hover_color
        self.active_color = active_color
        self.text_color = text_color
        self.shadow_color = shadow_color
        self.is_active = is_active
        self.is_hovered = False

    def set_text(self, text: str):
        self.text = str(text)
        self.queue_reflow()

    def get_minimum_size(self) -> tuple[int, int]:
        txt_w = assets.get_text_width(self.text, size=self.font_size)
        txt_h = assets.get_text_height(self.text, size=self.font_size)
        pt, pr, pb, pl = self.padding
        w = self.width if self.width is not None else (txt_w + pl + pr + 24)
        h = self.height if self.height is not None else (txt_h + pt + pb + 12)
        return w, h

    def handle_event(
        self, event: pygame.event.Event, mouse_pos: tuple[int, int]
    ) -> bool:
        if not self.visible:
            return False

        hovered = self.rect.collidepoint(mouse_pos)
        if hovered and not self.is_hovered:
            assets.play_sound("click1.ogg", volume=0.3)
        self.is_hovered = hovered

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                assets.play_sound("click2.ogg", volume=1)
                if self.on_click:
                    self.on_click()
                return True
        return False

    def draw(self, surface: pygame.Surface, mouse_pos: tuple[int, int]):
        if not self.visible:
            return

        hovered = self.rect.collidepoint(mouse_pos)
        if hovered and not self.is_hovered:
            assets.play_sound("click1.ogg", volume=0.3)
        self.is_hovered = hovered

        w, h = self.rect.width, self.rect.height

        if self.use_texture and assets.get_sprite(self.texture_id):
            btn_surf = assets.get_9slice_surface(
                self.texture_id, w, h, slice_margin=self.slice_margin
            )
            surface.blit(btn_surf, self.rect.topleft)

            # Draw crisp outline on hover (white) and active (green)
            if self.is_active:
                pygame.draw.rect(
                    surface,
                    (75, 225, 105),
                    self.rect.inflate(6, 6),
                    width=4,
                    border_radius=16,
                )
            elif self.is_hovered:
                pygame.draw.rect(
                    surface,
                    (255, 255, 255),  # Pure white outline on hover
                    self.rect.inflate(6, 6),
                    width=4,
                    border_radius=16,
                )
        else:
            col = self.active_color if self.is_active else (self.hover_color if self.is_hovered else self.bg_color)
            if col:
                pygame.draw.rect(surface, col, self.rect, border_radius=12)

            if self.is_active:
                pygame.draw.rect(
                    surface, (75, 225, 105), self.rect.inflate(4, 4), width=4, border_radius=14
                )
            elif self.is_hovered:
                pygame.draw.rect(
                    surface, (255, 255, 255), self.rect.inflate(4, 4), width=4, border_radius=14
                )
            elif self.border_color and self.border_width > 0:
                pygame.draw.rect(
                    surface, self.border_color, self.rect, self.border_width, border_radius=12
                )

        # Center Text
        if self.shadow_color:
            txt_surf = assets.render_text_with_shadow(
                self.text,
                size=self.font_size,
                color=self.text_color,
                shadow_color=self.shadow_color,
                offset=(1, 2),
            )
        else:
            txt_surf = assets.render_text(
                self.text,
                size=self.font_size,
                color=self.text_color,
            )

        tx = self.rect.centerx - txt_surf.get_width() // 2
        ty = self.rect.centery - txt_surf.get_height() // 2
        surface.blit(txt_surf, (tx, ty))


class Slider(Control):
    def __init__(
        self,
        min_value: float = 0.0,
        max_value: float = 1.0,
        value: float = 1.0,
        step: float | None = 0.05,
        width: int = 280,
        height: int = 36,
        on_value_change: Callable[[float], None] | None = None,
        margin: tuple[int, ...] | int = 0,
        align_self: AlignSelf = "auto",
        visible: bool = True,
    ):
        super().__init__(
            width=width,
            height=height,
            margin=margin,
            align_self=align_self,
            visible=visible,
        )
        self.min_value = float(min_value)
        self.max_value = float(max_value)
        self.value = float(min(max_value, max(min_value, value)))
        self.step = step
        self.on_value_change = on_value_change
        self.is_dragging = False
        self.is_hovered = False

    def set_value(self, val: float):
        clamped = max(self.min_value, min(self.max_value, float(val)))
        if self.step:
            clamped = round(clamped / self.step) * self.step
            clamped = max(self.min_value, min(self.max_value, clamped))
        if clamped != self.value:
            self.value = clamped
            if self.on_value_change:
                self.on_value_change(self.value)

    def _update_from_mouse_x(self, mouse_x: int):
        track_left = self.rect.x + 14
        track_right = self.rect.right - 14
        track_w = max(1, track_right - track_left)
        rel_x = max(0, min(track_w, mouse_x - track_left))
        ratio = rel_x / track_w
        raw_val = self.min_value + ratio * (self.max_value - self.min_value)
        self.set_value(raw_val)

    def handle_event(
        self, event: pygame.event.Event, mouse_pos: tuple[int, int]
    ) -> bool:
        if not self.visible:
            return False

        hovered = self.rect.collidepoint(mouse_pos)
        if hovered and not self.is_hovered and not self.is_dragging:
            assets.play_sound("click1.ogg", volume=0.3)
        self.is_hovered = hovered

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(mouse_pos):
                self.is_dragging = True
                self._update_from_mouse_x(mouse_pos[0])
                assets.play_sound("click2.ogg", volume=0.6)
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging:
                self.is_dragging = False
                return True

        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                self._update_from_mouse_x(mouse_pos[0])
                return True

        return False

    def draw(self, surface: pygame.Surface, mouse_pos: tuple[int, int]):
        if not self.visible:
            return

        hovered = self.rect.collidepoint(mouse_pos)
        if hovered and not self.is_hovered and not self.is_dragging:
            assets.play_sound("click1.ogg", volume=0.3)
        self.is_hovered = hovered

        # Track bounds
        pad_x = 14
        track_rect = pygame.Rect(
            self.rect.x + pad_x,
            self.rect.centery - 6,
            self.rect.width - pad_x * 2,
            12,
        )

        # Track background (dark inset)
        pygame.draw.rect(surface, (45, 30, 20), track_rect, border_radius=6)
        pygame.draw.rect(surface, (80, 55, 35), track_rect, width=2, border_radius=6)

        # Active filled track
        ratio = 0.0
        if self.max_value > self.min_value:
            ratio = (self.value - self.min_value) / (self.max_value - self.min_value)
        fill_w = int(track_rect.width * ratio)
        if fill_w > 0:
            fill_rect = pygame.Rect(
                track_rect.x,
                track_rect.y,
                fill_w,
                track_rect.height,
            )
            pygame.draw.rect(surface, (235, 155, 45), fill_rect, border_radius=6)

        # Knob / Handle position
        knob_cx = track_rect.x + fill_w
        knob_cy = self.rect.centery
        knob_radius = 12

        # Knob hover / drag outline
        if self.is_dragging or self.is_hovered:
            pygame.draw.circle(
                surface, (255, 255, 255), (knob_cx, knob_cy), knob_radius + 4
            )

        # Knob shadow
        pygame.draw.circle(
            surface, (30, 20, 10), (knob_cx, knob_cy + 2), knob_radius
        )
        # Knob body
        pygame.draw.circle(
            surface, (250, 245, 235), (knob_cx, knob_cy), knob_radius
        )
        # Knob border
        pygame.draw.circle(
            surface, (120, 70, 25), (knob_cx, knob_cy), knob_radius, width=3
        )


