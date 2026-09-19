"""
Lightweight Figma-inspired Auto Layout UI system for Pygame.
Supports VBox (vertical auto-layout), HBox (horizontal auto-layout),
Buttons, Labels, automatic padding, gap, and alignment.
"""

from collections.abc import Callable
from typing import Literal

import pygame

from assets_loader import assets
from settings import COLOR_BUTTON, COLOR_BUTTON_HOVER, COLOR_TEXT_DARK, COLOR_WHITE

AlignType = Literal["start", "center", "end"]

class UIElement:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.visible = True

    def compute_size(self) -> tuple[int, int]:
        return self.rect.width, self.rect.height

    def set_position(self, x: int, y: int):
        self.rect.x = x
        self.rect.y = y

    def handle_event(self, event: pygame.event.Event, mouse_pos: tuple[int, int]) -> bool:
        return False

    def draw(self, surface: pygame.Surface, mouse_pos: tuple[int, int]):
        pass

class Label(UIElement):
    def __init__(self, text: str, color: tuple[int, int, int] = COLOR_TEXT_DARK, scale: int = 1):
        super().__init__()
        self.text = text
        self.color = color
        self.scale = scale
        self._update_size()

    def set_text(self, text: str):
        self.text = text
        self._update_size()

    def _update_size(self):
        w = assets.get_text_width(self.text, scale=self.scale)
        h = assets.get_text_height(self.text, scale=self.scale)
        self.rect.size = (w, h)

    def compute_size(self) -> tuple[int, int]:
        self._update_size()
        return self.rect.width, self.rect.height

    def draw(self, surface: pygame.Surface, mouse_pos: tuple[int, int]):
        if not self.visible:
            return
        surf = assets.render_text(self.text, color=self.color, scale=self.scale)
        surface.blit(surf, (self.rect.x, self.rect.y))

class Button(UIElement):
    def __init__(
        self,
        text: str,
        on_click: Callable[[], None] | None = None,
        width: int | None = None,
        height: int = 16,
        padding_x: int = 6,
        bg_color: tuple[int, int, int] = COLOR_BUTTON,
        hover_color: tuple[int, int, int] = COLOR_BUTTON_HOVER,
        border_color: tuple[int, int, int] = (130, 75, 25),
        text_color: tuple[int, int, int] = COLOR_WHITE,
        active_color: tuple[int, int, int] | None = None,
        is_active: bool = False
    ):
        super().__init__()
        self.text = text
        self.on_click = on_click
        self.fixed_width = width
        self.height = height
        self.padding_x = padding_x
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.border_color = border_color
        self.text_color = text_color
        self.active_color = active_color or (60, 160, 70)
        self.is_active = is_active
        self.is_hovered = False
        self._update_size()

    def set_text(self, text: str):
        self.text = text
        self._update_size()

    def _update_size(self):
        if self.fixed_width is not None:
            w = self.fixed_width
        else:
            # Hug content: text width + padding
            txt_w = assets.get_text_width(self.text)
            w = txt_w + (self.padding_x * 2)
        self.rect.size = (w, self.height)

    def compute_size(self) -> tuple[int, int]:
        self._update_size()
        return self.rect.width, self.rect.height

    def handle_event(self, event: pygame.event.Event, mouse_pos: tuple[int, int]) -> bool:
        if not self.visible:
            return False

        self.is_hovered = self.rect.collidepoint(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                if self.on_click:
                    self.on_click()
                return True
        return False

    def draw(self, surface: pygame.Surface, mouse_pos: tuple[int, int]):
        if not self.visible:
            return

        self.is_hovered = self.rect.collidepoint(mouse_pos)

        if self.is_active:
            col = self.active_color
        elif self.is_hovered:
            col = self.hover_color
        else:
            col = self.bg_color

        pygame.draw.rect(surface, col, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 1)

        txt_surf = assets.render_text(self.text, color=self.text_color)
        tx = self.rect.centerx - txt_surf.get_width() // 2
        ty = self.rect.centery - txt_surf.get_height() // 2
        surface.blit(txt_surf, (tx, ty))

class AutoLayout(UIElement):
    """
    Base Auto Layout container behaving like Figma's Auto Layout.
    Manages children positioning with gap, padding, and alignment.
    """
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        gap: int = 4,
        padding: tuple[int, int, int, int] | int = 0,
        align: AlignType = "center",
        children: list[UIElement] | None = None
    ):
        super().__init__()
        self.x = x
        self.y = y
        self.gap = gap
        
        # padding: (top, right, bottom, left)
        if isinstance(padding, int):
            self.padding = (padding, padding, padding, padding)
        elif len(padding) == 2:
            self.padding = (padding[0], padding[1], padding[0], padding[1])
        else:
            self.padding = padding

        self.align = align
        self.children = children or []
        self.reflow()

    def add_child(self, child: UIElement):
        self.children.append(child)
        self.reflow()

    def remove_child(self, child: UIElement):
        if child in self.children:
            self.children.remove(child)
            self.reflow()

    def clear(self):
        self.children.clear()
        self.reflow()

    def reflow(self):
        pass

    def handle_event(self, event: pygame.event.Event, mouse_pos: tuple[int, int]) -> bool:
        if not self.visible:
            return False
        for child in self.children:
            if child.visible and child.handle_event(event, mouse_pos):
                return True
        return False

    def draw(self, surface: pygame.Surface, mouse_pos: tuple[int, int]):
        if not self.visible:
            return
        for child in self.children:
            if child.visible:
                child.draw(surface, mouse_pos)

class VBox(AutoLayout):
    """Vertical Auto Layout (Figma Column)"""
    def reflow(self):
        visible_children = [c for c in self.children if c.visible]
        if not visible_children:
            self.rect.size = (0, 0)
            return

        pt, pr, pb, pl = self.padding

        # First pass: compute child sizes
        child_sizes = [c.compute_size() for c in visible_children]
        max_child_w = max(w for w, h in child_sizes)
        total_child_h = sum(h for w, h in child_sizes) + (self.gap * (len(visible_children) - 1))

        container_w = max_child_w + pl + pr
        container_h = total_child_h + pt + pb
        self.rect = pygame.Rect(self.x, self.y, container_w, container_h)

        # Second pass: position children
        curr_y = self.y + pt
        for child, (cw, ch) in zip(visible_children, child_sizes):
            if self.align == "start":
                cx = self.x + pl
            elif self.align == "end":
                cx = self.x + container_w - pr - cw
            else:  # "center"
                cx = self.x + pl + ((max_child_w - cw) // 2)

            child.set_position(cx, curr_y)
            if isinstance(child, AutoLayout):
                child.reflow()
            curr_y += ch + self.gap

    def compute_size(self) -> tuple[int, int]:
        self.reflow()
        return self.rect.width, self.rect.height

class HBox(AutoLayout):
    """Horizontal Auto Layout (Figma Row)"""
    def reflow(self):
        visible_children = [c for c in self.children if c.visible]
        if not visible_children:
            self.rect.size = (0, 0)
            return

        pt, pr, pb, pl = self.padding

        child_sizes = [c.compute_size() for c in visible_children]
        max_child_h = max(h for w, h in child_sizes)
        total_child_w = sum(w for w, h in child_sizes) + (self.gap * (len(visible_children) - 1))

        container_w = total_child_w + pl + pr
        container_h = max_child_h + pt + pb
        self.rect = pygame.Rect(self.x, self.y, container_w, container_h)

        curr_x = self.x + pl
        for child, (cw, ch) in zip(visible_children, child_sizes):
            if self.align == "start":
                cy = self.y + pt
            elif self.align == "end":
                cy = self.y + container_h - pb - ch
            else:  # "center"
                cy = self.y + pt + ((max_child_h - ch) // 2)

            child.set_position(curr_x, cy)
            if isinstance(child, AutoLayout):
                child.reflow()
            curr_x += cw + self.gap

    def compute_size(self) -> tuple[int, int]:
        self.reflow()
        return self.rect.width, self.rect.height
