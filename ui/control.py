from typing import Literal
import pygame

# Type Aliases matching CSS / Unity / Godot standards
FlexDirection = Literal["column", "row"]
JustifyContent = Literal[
    "flex-start", "center", "flex-end", "space-between", "space-around", "space-evenly"
]
AlignItems = Literal["flex-start", "center", "flex-end", "stretch"]
AlignSelf = Literal["auto", "flex-start", "center", "flex-end", "stretch"]


def parse_box_model(
    value: tuple[int, ...] | list[int] | int | None,
) -> tuple[int, int, int, int]:
    """Parse box model properties (padding / margin) like CSS: top, right, bottom, left."""
    if value is None:
        return (0, 0, 0, 0)
    if isinstance(value, int):
        return (value, value, value, value)
    if len(value) == 1:
        return (value[0], value[0], value[0], value[0])
    if len(value) == 2:
        return (value[0], value[1], value[0], value[1])
    if len(value) == 3:
        return (value[0], value[1], value[2], value[1])
    if len(value) >= 4:
        return (value[0], value[1], value[2], value[3])
    return (0, 0, 0, 0)


class Control:
    """Base UI element with box-model and layout hierarchy."""

    def __init__(
        self,
        width: int | None = None,
        height: int | None = None,
        min_width: int = 0,
        min_height: int = 0,
        padding: tuple[int, ...] | int = 0,
        margin: tuple[int, ...] | int = 0,
        flex_grow: float = 0.0,
        align_self: AlignSelf = "auto",
        bg_color: tuple[int, int, int] | tuple[int, int, int, int] | None = None,
        border_color: tuple[int, int, int] | None = None,
        border_width: int = 0,
        visible: bool = True,
    ):
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.width = width
        self.height = height
        self.min_width = min_width
        self.min_height = min_height
        self.padding = parse_box_model(padding)
        self.margin = parse_box_model(margin)
        self.flex_grow = flex_grow
        self.align_self = align_self
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_width = border_width
        self.visible = visible
        self.parent: "Control | None" = None
        self.children: list["Control"] = []

    def add_child(self, child: "Control") -> "Control":
        child.parent = self
        self.children.append(child)
        self.queue_reflow()
        return child

    def remove_child(self, child: "Control"):
        if child in self.children:
            child.parent = None
            self.children.remove(child)
            self.queue_reflow()

    def clear_children(self):
        for child in self.children:
            child.parent = None
        self.children.clear()
        self.queue_reflow()

    def queue_reflow(self):
        curr = self
        while curr.parent:
            curr = curr.parent
        if hasattr(curr, "reflow"):
            curr.reflow()

    def get_minimum_size(self) -> tuple[int, int]:
        pt, pr, pb, pl = self.padding
        w = self.width if self.width is not None else self.min_width
        h = self.height if self.height is not None else self.min_height
        return max(w, self.min_width) + pl + pr, max(h, self.min_height) + pt + pb

    def layout(self, rect: pygame.Rect):
        self.rect = pygame.Rect(rect)
        for child in self.children:
            if child.visible:
                child.layout(self.rect)

    def handle_event(
        self, event: pygame.event.Event, mouse_pos: tuple[int, int]
    ) -> bool:
        if not self.visible:
            return False
        for child in reversed(self.children):
            if child.visible and child.handle_event(event, mouse_pos):
                return True
        return False

    def draw(self, surface: pygame.Surface, mouse_pos: tuple[int, int]):
        if not self.visible:
            return

        # Background
        if self.bg_color:
            if len(self.bg_color) == 4 and self.bg_color[3] < 255:
                bg_surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
                bg_surf.fill(self.bg_color)
                surface.blit(bg_surf, self.rect.topleft)
            else:
                pygame.draw.rect(surface, self.bg_color[:3], self.rect)

        # Border
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(surface, self.border_color, self.rect, self.border_width)

        # Draw children
        for child in self.children:
            if child.visible:
                child.draw(surface, mouse_pos)
