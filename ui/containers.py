import pygame
from ui.control import AlignItems, AlignSelf, Control, FlexDirection, JustifyContent


class FlexContainer(Control):
    """
    CSS Flexbox / Unity UI Toolkit / Godot BoxContainer engine.
    """

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        direction: FlexDirection = "column",
        gap: int = 4,
        separation: int | None = None,
        padding: tuple[int, ...] | int = 0,
        margin: tuple[int, ...] | int = 0,
        justify_content: JustifyContent = "flex-start",
        align_items: AlignItems = "center",
        align: str | None = None,
        width: int | None = None,
        height: int | None = None,
        children: list[Control] | None = None,
        bg_color: tuple[int, int, int] | tuple[int, int, int, int] | None = None,
        border_color: tuple[int, int, int] | None = None,
        border_width: int = 0,
    ):
        super().__init__(
            width=width,
            height=height,
            padding=padding,
            margin=margin,
            bg_color=bg_color,
            border_color=border_color,
            border_width=border_width,
        )
        self.rect.topleft = (x, y)
        self.direction = direction
        self.gap = separation if separation is not None else gap

        if align:
            if align == "start":
                self.align_items = "flex-start"
            elif align == "end":
                self.align_items = "flex-end"
            elif align in ["center", "stretch", "flex-start", "flex-end"]:
                self.align_items = align
            else:
                self.align_items = "center"
        else:
            self.align_items = align_items

        self.justify_content = justify_content

        if children:
            for c in children:
                self.add_child(c)

        self.reflow()

    @property
    def x(self) -> int:
        return self.rect.x

    @x.setter
    def x(self, val: int):
        self.rect.x = val
        self.reflow()

    @property
    def y(self) -> int:
        return self.rect.y

    @y.setter
    def y(self, val: int):
        self.rect.y = val
        self.reflow()

    def get_minimum_size(self) -> tuple[int, int]:
        visible_children = [c for c in self.children if c.visible]
        pt, pr, pb, pl = self.padding

        if not visible_children:
            return pl + pr, pt + pb

        child_min_sizes = []
        for c in visible_children:
            cw, ch = c.get_minimum_size()
            mt, mr, mb, ml = c.margin
            child_min_sizes.append((cw + ml + mr, ch + mt + mb))

        if self.direction == "column":
            total_h = sum(h for w, h in child_min_sizes) + (
                self.gap * (len(visible_children) - 1)
            )
            max_w = max(w for w, h in child_min_sizes)
            w = (self.width if self.width is not None else max_w) + pl + pr
            h = (self.height if self.height is not None else total_h) + pt + pb
        else:
            total_w = sum(w for w, h in child_min_sizes) + (
                self.gap * (len(visible_children) - 1)
            )
            max_h = max(h for w, h in child_min_sizes)
            w = (self.width if self.width is not None else total_w) + pl + pr
            h = (self.height if self.height is not None else max_h) + pt + pb

        return max(w, self.min_width), max(h, self.min_height)

    def reflow(self):
        min_w, min_h = self.get_minimum_size()
        actual_w = self.width if self.width is not None else min_w
        actual_h = self.height if self.height is not None else min_h

        self.rect.size = (
            max(actual_w, self.min_width),
            max(actual_h, self.min_height),
        )

        visible_children = [c for c in self.children if c.visible]
        if not visible_children:
            return

        pt, pr, pb, pl = self.padding
        inner_w = self.rect.width - pl - pr
        inner_h = self.rect.height - pt - pb

        child_metrics = []
        for c in visible_children:
            cw, ch = c.get_minimum_size()
            mt, mr, mb, ml = c.margin
            child_metrics.append({
                "control": c,
                "base_w": cw,
                "base_h": ch,
                "margin": (mt, mr, mb, ml),
                "grow": c.flex_grow,
            })

        is_col = self.direction == "column"
        main_gap = self.gap
        total_gaps = main_gap * (len(visible_children) - 1)

        if is_col:
            base_main_sum = sum(
                m["base_h"] + m["margin"][0] + m["margin"][2] for m in child_metrics
            )
            available_main = max(0, inner_h - total_gaps - base_main_sum)
        else:
            base_main_sum = sum(
                m["base_w"] + m["margin"][1] + m["margin"][3] for m in child_metrics
            )
            available_main = max(0, inner_w - total_gaps - base_main_sum)

        total_grow = sum(m["grow"] for m in child_metrics)
        for m in child_metrics:
            if is_col:
                extra = (
                    int(available_main * (m["grow"] / total_grow))
                    if total_grow > 0
                    else 0
                )
                m["target_h"] = m["base_h"] + extra
                m["target_w"] = m["base_w"]
            else:
                extra = (
                    int(available_main * (m["grow"] / total_grow))
                    if total_grow > 0
                    else 0
                )
                m["target_w"] = m["base_w"] + extra
                m["target_h"] = m["base_h"]

        final_main_sum = (
            sum(
                (m["target_h"] + m["margin"][0] + m["margin"][2])
                if is_col
                else (m["target_w"] + m["margin"][1] + m["margin"][3])
                for m in child_metrics
            )
            + total_gaps
        )

        main_space = (inner_h - final_main_sum) if is_col else (inner_w - final_main_sum)
        main_space = max(0, main_space)

        if self.justify_content == "center":
            start_main = main_space // 2
            step_gap = main_gap
        elif self.justify_content == "flex-end":
            start_main = main_space
            step_gap = main_gap
        elif self.justify_content == "space-between" and len(visible_children) > 1:
            start_main = 0
            step_gap = main_gap + (main_space // (len(visible_children) - 1))
        elif self.justify_content == "space-around" and len(visible_children) > 0:
            slice_space = main_space // len(visible_children)
            start_main = slice_space // 2
            step_gap = main_gap + slice_space
        elif self.justify_content == "space-evenly" and len(visible_children) > 0:
            slice_space = main_space // (len(visible_children) + 1)
            start_main = slice_space
            step_gap = main_gap + slice_space
        else:
            start_main = 0
            step_gap = main_gap

        curr_main = (
            (self.rect.y + pt + start_main)
            if is_col
            else (self.rect.x + pl + start_main)
        )

        for m in child_metrics:
            c: Control = m["control"]
            mt, mr, mb, ml = m["margin"]

            effective_align = (
                c.align_self if c.align_self != "auto" else self.align_items
            )

            if is_col:
                child_h = m["target_h"]
                if effective_align == "stretch":
                    child_w = inner_w - ml - mr
                    child_x = self.rect.x + pl + ml
                elif effective_align == "flex-start":
                    child_w = m["target_w"]
                    child_x = self.rect.x + pl + ml
                elif effective_align == "flex-end":
                    child_w = m["target_w"]
                    child_x = self.rect.x + self.rect.width - pr - mr - child_w
                else:
                    child_w = m["target_w"]
                    child_x = (
                        self.rect.x + pl + ml + ((inner_w - ml - mr - child_w) // 2)
                    )

                child_y = curr_main + mt
                c.layout(pygame.Rect(child_x, child_y, child_w, child_h))
                curr_main += child_h + mt + mb + step_gap
            else:
                child_w = m["target_w"]
                if effective_align == "stretch":
                    child_h = inner_h - mt - mb
                    child_y = self.rect.y + pt + mt
                elif effective_align == "flex-start":
                    child_h = m["target_h"]
                    child_y = self.rect.y + pt + mt
                elif effective_align == "flex-end":
                    child_h = m["target_h"]
                    child_y = self.rect.y + self.rect.height - pb - mb - child_h
                else:
                    child_h = m["target_h"]
                    child_y = (
                        self.rect.y + pt + mt + ((inner_h - mt - mb - child_h) // 2)
                    )

                child_x = curr_main + ml
                c.layout(pygame.Rect(child_x, child_y, child_w, child_h))
                curr_main += child_w + ml + mr + step_gap

    def layout(self, rect: pygame.Rect):
        self.rect = pygame.Rect(rect)
        self.reflow()


class VBoxContainer(FlexContainer):
    def __init__(self, *args, **kwargs):
        kwargs["direction"] = "column"
        super().__init__(*args, **kwargs)


class HBoxContainer(FlexContainer):
    def __init__(self, *args, **kwargs):
        kwargs["direction"] = "row"
        super().__init__(*args, **kwargs)


class PanelContainer(Control):
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int | None = None,
        height: int | None = None,
        padding: tuple[int, ...] | int = 24,
        margin: tuple[int, ...] | int = 0,
        use_texture: bool = True,
        texture_id: str = "ui-background",
        slice_margin: int = 32,
        bg_color: tuple[int, int, int] | tuple[int, int, int, int] | None = None,
        border_color: tuple[int, int, int] | None = None,
        border_width: int = 0,
        children: list[Control] | None = None,
    ):
        super().__init__(
            width=width,
            height=height,
            padding=padding,
            margin=margin,
            bg_color=bg_color,
            border_color=border_color,
            border_width=border_width,
        )
        self.rect.topleft = (x, y)
        self.use_texture = use_texture
        self.texture_id = texture_id
        self.slice_margin = slice_margin
        if children:
            for c in children:
                self.add_child(c)
        self.reflow()

    def get_minimum_size(self) -> tuple[int, int]:
        pt, pr, pb, pl = self.padding
        if not self.children:
            return (self.width or 0) + pl + pr, (self.height or 0) + pt + pb

        max_cw = max(c.get_minimum_size()[0] for c in self.children if c.visible)
        max_ch = max(c.get_minimum_size()[1] for c in self.children if c.visible)
        w = max_cw + pl + pr
        h = max_ch + pt + pb
        return max(w, self.width or 0), max(h, self.height or 0)

    def layout(self, rect: pygame.Rect):
        self.rect = pygame.Rect(rect)
        self.reflow()

    def reflow(self):
        min_w, min_h = self.get_minimum_size()
        self.rect.size = (self.width or min_w, self.height or min_h)
        pt, pr, pb, pl = self.padding
        inner_rect = pygame.Rect(
            self.rect.x + pl,
            self.rect.y + pt,
            self.rect.width - pl - pr,
            self.rect.height - pt - pb,
        )
        for c in self.children:
            if c.visible:
                c.layout(inner_rect)

    def draw(self, surface: pygame.Surface, mouse_pos: tuple[int, int]):
        if not self.visible:
            return

        from core.assets import assets

        if self.use_texture and assets.get_sprite(self.texture_id):
            bg_surf = assets.get_9slice_surface(
                self.texture_id,
                self.rect.width,
                self.rect.height,
                slice_margin=self.slice_margin,
            )
            surface.blit(bg_surf, self.rect.topleft)
        else:
            super().draw(surface, mouse_pos)

        for child in self.children:
            if child.visible:
                child.draw(surface, mouse_pos)


# Backward compatibility aliases
VBox = VBoxContainer
HBox = HBoxContainer
AutoLayout = FlexContainer
