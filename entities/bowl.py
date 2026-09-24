import pygame

from core.assets import assets
from items.registry import items_registry

# Bowl layout & ingredient placement parameters
BOWL_HOME_POS = (780, 710)
BOWL_SCALE = 0.80
BOWL_DROPZONE_EXPAND = (24, 24)
COLOR_OUTLINE_HOVER = (255, 255, 255)

BOWL_INGREDIENT_MIN_X = 30
BOWL_INGREDIENT_MAX_X_OFFSET = 30
BOWL_INGREDIENT_MIN_Y = 20
BOWL_INGREDIENT_MAX_Y_OFFSET = 70

BOWL_MEATBALL_OFFSETS = [
    (90, 75),
    (210, 70),
    (150, 110),
    (80, 120),
    (220, 125),
    (150, 50),
]
BOWL_NOODLE_OFFSET = (70, 50)
BOWL_GORENGAN_OFFSET = (180, 35)


class Bowl:
    """
    3-Layer Bowl Entity:
    1. mangkok_back: Inner back rim and bowl bottom
    2. Food layer: Ingredients depth-sorted with contact shadows
    3. mangkok_front: Front rim and rooster motif overlapping bottom of food
    """

    def __init__(
        self,
        x: int = BOWL_HOME_POS[0],
        y: int = BOWL_HOME_POS[1],
        scale: float = BOWL_SCALE,
    ):
        self.home_x = x
        self.home_y = y
        self.x = x
        self.y = y
        self.scale = scale

        raw_back = assets.get_sprite("mangkok-back")
        raw_front = assets.get_sprite("mangkok-front")
        raw_main = assets.get_sprite("mangkok")

        if self.scale != 1.0:
            self.sprite_back = (
                pygame.transform.smoothscale(
                    raw_back,
                    (int(raw_back.get_width() * scale), int(raw_back.get_height() * scale)),
                )
                if raw_back
                else None
            )
            self.sprite_front = (
                pygame.transform.smoothscale(
                    raw_front,
                    (int(raw_front.get_width() * scale), int(raw_front.get_height() * scale)),
                )
                if raw_front
                else None
            )
            self.sprite = (
                pygame.transform.smoothscale(
                    raw_main,
                    (int(raw_main.get_width() * scale), int(raw_main.get_height() * scale)),
                )
                if raw_main
                else None
            )
        else:
            self.sprite_back = raw_back
            self.sprite_front = raw_front
            self.sprite = raw_main

        raw_shadow = assets.get_shadow_sprite("mangkok", alpha=80)
        raw_drag_shadow = assets.get_shadow_sprite("mangkok", alpha=110)

        if self.scale != 1.0:
            if raw_shadow:
                sw = int(raw_shadow.get_width() * scale)
                sh = int(raw_shadow.get_height() * scale)
                self.shadow_sprite = pygame.transform.smoothscale(raw_shadow, (sw, sh))
            else:
                self.shadow_sprite = None

            if raw_drag_shadow:
                sw = int(raw_drag_shadow.get_width() * scale)
                sh = int(raw_drag_shadow.get_height() * scale)
                self.drag_shadow_sprite = pygame.transform.smoothscale(raw_drag_shadow, (sw, sh))
            else:
                self.drag_shadow_sprite = None
        else:
            self.shadow_sprite = raw_shadow
            self.drag_shadow_sprite = raw_drag_shadow

        ref_spr = self.sprite_back or self.sprite or self.sprite_front
        self.width = ref_spr.get_width() if ref_spr else int(400 * scale)
        self.height = ref_spr.get_height() if ref_spr else int(300 * scale)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.is_dragging = False
        self.is_hovered = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        # Ingredients list: dicts with {'type': str, 'offset_x': int, 'offset_y': int}
        self.ingredients: list[dict] = []

    def update_hover(self, pos: tuple[int, int]):
        if self.is_dragging:
            self.is_hovered = False
        else:
            self.is_hovered = self.contains_point(pos)

    def contains_point(self, pos: tuple[int, int]) -> bool:
        ew, eh = BOWL_DROPZONE_EXPAND
        expanded_rect = self.rect.inflate(ew, eh)
        return expanded_rect.collidepoint(pos)

    def start_drag(self, mouse_pos: tuple[int, int]):
        self.is_dragging = True
        self.is_hovered = False
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

    def place_on_counter(
        self,
        min_x: int = 40,
        max_x: int = 1880,
        min_y: int = 690,
        max_y: int = 994,
    ):
        self.is_dragging = False
        self.x = max(min_x, min(max_x - self.width, self.x))
        self.y = max(min_y, min(max_y - self.height, self.y))
        self.home_x = self.x
        self.home_y = self.y
        self.rect.topleft = (self.x, self.y)

    def add_ingredient(
        self, item_id: str, drop_pos: tuple[int, int] = None
    ) -> bool:
        """Add an ingredient inside the bowl with depth positioning."""
        item_def = items_registry.get(item_id)
        spr = item_def.sprite if item_def else assets.get_sprite(item_id)
        sw = int((spr.get_width() if spr else 80) * self.scale)
        sh = int((spr.get_height() if spr else 80) * self.scale)

        if drop_pos:
            rel_x = (drop_pos[0] - self.x - sw // 2) / self.scale
            rel_y = (drop_pos[1] - self.y - sh // 2) / self.scale
            min_x = BOWL_INGREDIENT_MIN_X
            max_x = (self.width - sw) / self.scale - BOWL_INGREDIENT_MAX_X_OFFSET
            min_y = BOWL_INGREDIENT_MIN_Y
            max_y = (self.height - sh) / self.scale - BOWL_INGREDIENT_MAX_Y_OFFSET
            rel_x = max(min_x, min(max(min_x, max_x), rel_x))
            rel_y = max(min_y, min(max(min_y, max_y), rel_y))
        else:
            count = len(self.ingredients)
            # Standard placements
            if item_id in ["daun_bawang", "daun-bawang"]:
                rel_x, rel_y = 45, 65
            elif item_id in ["bawang_goreng", "bawang-goreng"]:
                rel_x, rel_y = 45, 80
            elif item_id in ["kecap", "saos_sambal", "saos-sambal", "saos_tomat", "saos-tomat"]:
                rel_x, rel_y = 110 + (count % 3 * 25), 85 + (count % 2 * 15)
            elif item_def and item_def.category == "noodle":
                rel_x = BOWL_NOODLE_OFFSET[0] + (count % 2 * 10 - 5)
                rel_y = BOWL_NOODLE_OFFSET[1] + (count % 2 * 10)
            elif "gorengan" in item_id:
                rel_x = BOWL_GORENGAN_OFFSET[0]
                rel_y = BOWL_GORENGAN_OFFSET[1] + (count % 3 * 15)
            else:
                offsets = BOWL_MEATBALL_OFFSETS
                idx = count % len(offsets)
                rel_x, rel_y = offsets[idx]

        self.ingredients.append({
            "type": item_id,
            "offset_x": int(rel_x),
            "offset_y": int(rel_y),
        })
        return True

    def clear(self):
        self.ingredients.clear()

    def get_ingredient_counts(self) -> dict[str, int]:
        counts = {}
        for item in self.ingredients:
            t = item["type"]
            # Resolve canonical ID
            item_def = items_registry.get(t)
            canonical = item_def.id if item_def else t
            counts[canonical] = counts.get(canonical, 0) + 1
        return counts

    def draw(self, surface: pygame.Surface):
        # 1. Shadow underneath the bowl
        if self.is_dragging:
            if self.drag_shadow_sprite:
                surface.blit(self.drag_shadow_sprite, (self.x + 8, self.y + 16))
        else:
            if self.shadow_sprite:
                surface.blit(self.shadow_sprite, (self.x + 4, self.y + 8))

        # 2. White hover outline (traced from game/mangkok.png)
        if self.is_hovered and not self.is_dragging:
            out_spr, pad = assets.get_outlined_sprite(
                "mangkok",
                outline_color=COLOR_OUTLINE_HOVER,
                thickness=4,
                scale=self.scale,
            )
            if out_spr:
                surface.blit(out_spr, (self.x - pad, self.y - pad))

        # 3. LAYER 1: Mangkok Back
        if self.sprite_back:
            surface.blit(self.sprite_back, (self.x, self.y))
        elif self.sprite:
            surface.blit(self.sprite, (self.x, self.y))

        # 4. LAYER 2: Food Layer (Sprinkle toppings & sauces render on top of meats/noodles)
        def get_item_layer_key(it):
            t = it["type"]
            if t in ["daun_bawang", "daun-bawang", "bawang_goreng", "bawang-goreng", "kecap", "saos_sambal", "saos_tomat"]:
                return (1, it["offset_y"])
            return (0, it["offset_y"])

        sorted_ingredients = sorted(
            self.ingredients, key=get_item_layer_key
        )
        for item in sorted_ingredients:
            item_type = item["type"]
            item_def = items_registry.get(item_type)
            spr = (
                item_def.sprite if item_def else assets.get_sprite(item_type)
            )
            shadow_spr = (
                item_def.shadow_sprite
                if item_def
                else assets.get_shadow_sprite(item_type, alpha=70)
            )

            if spr:
                # Custom ingredient scale modifiers inside the bowl
                if item_type in ["kecap", "saos_sambal", "saos_tomat", "saos-sambal", "saos-tomat"]:
                    ing_scale = self.scale * 0.50
                elif item_type in ["mi_kuning", "mi-kuning", "mi_bihun", "mi-bihun"]:
                    ing_scale = self.scale * 0.85
                else:
                    ing_scale = self.scale

                sw, sh = int(spr.get_width() * ing_scale), int(spr.get_height() * ing_scale)
                spr_to_draw = pygame.transform.smoothscale(spr, (sw, sh))
                shadow_to_draw = (
                    pygame.transform.smoothscale(shadow_spr, (sw, sh))
                    if shadow_spr
                    else None
                )

                draw_x = self.x + int(item["offset_x"] * self.scale)
                draw_y = self.y + int(item["offset_y"] * self.scale)

                if shadow_to_draw:
                    surface.blit(shadow_to_draw, (draw_x + 4, draw_y + 4))
                surface.blit(spr_to_draw, (draw_x, draw_y))

        # 5. LAYER 3: Mangkok Front
        if self.sprite_front:
            surface.blit(self.sprite_front, (self.x, self.y))
        elif self.sprite:
            surface.blit(self.sprite, (self.x, self.y))
