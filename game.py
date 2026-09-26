import random

import pygame

from main import (
    COLOR_BLACK,
    COLOR_GOLD,
    COLOR_WHITE,
    INTERNAL_HEIGHT,
    INTERNAL_WIDTH,
    BaseScene,
    assets,
    save_manager,
)

DAY_START_HOUR = 10
DAY_END_HOUR = 20
MIN_CUSTOMERS_PER_DAY = 5
MAX_CUSTOMERS_PER_DAY = 7

INITIAL_MONEY = 0
INITIAL_REPUTATION = 100
DEFAULT_PATIENCE_TIME = 25.0

BASE_BOWL_PRICE = 2000
REPUTATION_GAIN = 10
REPUTATION_LOSS = 20

CUSTOMER_POS = (650, 315)
BOWL_HOME_POS = (780, 710)
TRASH_CAN_POS = (100, 710)
TRASH_CAN_SIZE = (160, 240)
ORDER_TICKET_POS = (40, 140)
ORDER_TICKET_SIZE = (280, 260)
HUD_HEIGHT = 68
PAUSE_BTN_POS = (1830, 8)
PAUSE_BTN_SIZE = (76, 52)
COLOR_BG_CYAN = (75, 205, 240)

UNLOCKED_ITEMS_BY_DAY = {
    1: {"mi_kuning", "bakso_halus", "kecap"},
    2: {"mi_kuning", "bakso_halus", "kecap", "mi_bihun", "gorengan_panjang"},
    3: {
        "mi_kuning",
        "bakso_halus",
        "kecap",
        "mi_bihun",
        "gorengan_panjang",
        "tahu",
        "saos_sambal",
        "saos_tomat",
    },
    4: {
        "mi_kuning",
        "bakso_halus",
        "kecap",
        "mi_bihun",
        "gorengan_panjang",
        "tahu",
        "saos_sambal",
        "saos_tomat",
        "bawang_goreng",
        "daun_bawang",
    },
}


def get_unlocked_items(day: int) -> set[str]:
    if day <= 1:
        return set(UNLOCKED_ITEMS_BY_DAY[1])
    if day in UNLOCKED_ITEMS_BY_DAY:
        return set(UNLOCKED_ITEMS_BY_DAY[day])
    max_day = max(UNLOCKED_ITEMS_BY_DAY.keys())
    return set(UNLOCKED_ITEMS_BY_DAY[max_day])


ITEM_DATA = {
    "mi_kuning": {"name": "Mie Kuning", "sprite": "mi-kuning", "price": 1000, "category": "noodle"},
    "mi_bihun": {"name": "Bihun", "sprite": "mi-bihun", "price": 1000, "category": "noodle"},
    "bakso_halus": {"name": "Bakso Halus", "sprite": "bakso-halus", "price": 2500, "category": "meatball"},
    "gorengan_panjang": {"name": "Gorengan", "sprite": "gorengan-panjang", "price": 1000, "category": "topping"},
    "tahu": {"name": "Tahu", "sprite": "tahu", "price": 1500, "category": "topping"},
    "kecap": {"name": "Kecap Manis", "sprite": "kecap", "price": 500, "category": "sauce"},
    "saos_sambal": {"name": "Saos Sambal", "sprite": "saos-sambal", "price": 500, "category": "sauce"},
    "saos_tomat": {"name": "Saos Tomat", "sprite": "saos-tomat", "price": 500, "category": "sauce"},
    "bawang_goreng": {"name": "Bawang Goreng", "sprite": "bawang-goreng", "price": 500, "category": "topping"},
    "daun_bawang": {"name": "Daun Bawang", "sprite": "daun-bawang", "price": 500, "category": "topping"},
    "kuah": {"name": "Kuah", "sprite": "kuah", "price": 0, "category": "broth"},
}

ITEM_ALIASES = {
    "mi-kuning": "mi_kuning",
    "mi-bihun": "mi_bihun",
    "bakso": "bakso_halus",
    "bakso-halus": "bakso_halus",
    "gorengan": "gorengan_panjang",
    "gorengan-panjang": "gorengan_panjang",
    "kecap-manis": "kecap",
    "saos-sambal": "saos_sambal",
    "sambal": "saos_sambal",
    "saos-tomat": "saos_tomat",
    "bawang-goreng": "bawang_goreng",
    "daun-bawang": "daun_bawang",
}


def get_canonical_item_id(item_id: str) -> str:
    return ITEM_ALIASES.get(item_id, item_id)


def get_item_price(item_id: str) -> int:
    cid = get_canonical_item_id(item_id)
    return ITEM_DATA.get(cid, {}).get("price", 0)


def get_item_name(item_id: str) -> str:
    cid = get_canonical_item_id(item_id)
    return ITEM_DATA.get(cid, {}).get("name", item_id)


FOOD_STATIONS_LAYOUT = [
    {"id": "bakso_halus", "display_sprite": "bakso-halus-cluster", "x": 1030, "y": 290, "scale": 0.70, "is_pickable": True, "label": "Bakso Halus"},
    {"id": "tahu", "display_sprite": "tahu-cluster", "x": 1350, "y": 320, "scale": 0.70, "is_pickable": True, "label": "Tahu"},
    {"id": "mi_kuning", "display_sprite": "mi-kuning-cluster", "x": 1360, "y": 480, "scale": 0.60, "is_pickable": True, "label": "Mie Kuning"},
    {"id": "mi_bihun", "display_sprite": "mi-bihun-cluster", "x": 1510, "y": 480, "scale": 0.60, "is_pickable": True, "label": "Bihun"},
    {"id": "gorengan_panjang", "display_sprite": "gorengan-panjang-cluster", "x": 1035, "y": 460, "scale": 0.70, "is_pickable": True, "label": "Gorengan"},
    {"id": "kecap", "display_sprite": "kecap-bottle", "x": 1410, "y": 540, "scale": 0.70, "is_pickable": True, "hide_on_drag": True, "label": "Kecap Manis"},
    {"id": "saos_sambal", "display_sprite": "saos-sambal-bottle", "x": 1540, "y": 555, "scale": 0.70, "is_pickable": True, "hide_on_drag": True, "label": "Saos Sambal"},
    {"id": "saos_tomat", "display_sprite": "saos-tomat-bottle", "x": 1670, "y": 550, "scale": 0.70, "is_pickable": True, "hide_on_drag": True, "label": "Saos Tomat"},
    {"id": "bawang_goreng", "display_sprite": "bawang-goreng-cluster", "x": 1215, "y": 695, "scale": 0.65, "is_pickable": True, "label": "Bawang Goreng"},
    {"id": "daun_bawang", "display_sprite": "daun-bawang-cluster", "x": 1040, "y": 700, "scale": 0.65, "is_pickable": True, "label": "Daun Bawang"},
    {"id": "kuah", "display_sprite": "kuah", "x": 240, "y": 490, "scale": 0.67, "is_pickable": False, "label": "Kuah Kaldu"},
    {"id": "kentongan", "display_sprite": "kentongan", "x": 1720, "y": 40, "scale": 0.65, "is_pickable": False, "label": "Kentongan"},
]


class DraggedItem:
    def __init__(self, item_id: str, pos: tuple[int, int], source_tray=None, scale: float = 1.0, drag_offset=None):
        self.item_id = item_id
        self.source_tray = source_tray
        self.scale = scale
        self.drag_offset = drag_offset

        if source_tray and source_tray.hide_on_drag and source_tray.sprite:
            raw_spr = source_tray.sprite
            raw_shadow = source_tray.shadow_sprite
        else:
            raw_spr = assets.get_sprite(item_id)
            raw_shadow = assets.get_shadow_sprite(item_id, alpha=90)

        if scale != 1.0 and raw_spr:
            sw, sh = int(raw_spr.get_width() * scale), int(raw_spr.get_height() * scale)
            self.sprite = pygame.transform.smoothscale(raw_spr, (sw, sh))
            self.shadow_sprite = pygame.transform.smoothscale(raw_shadow, (sw, sh)) if raw_shadow else None
        else:
            self.sprite = raw_spr
            self.shadow_sprite = raw_shadow

        self.pos = list(pos)

    def update(self, pos: tuple[int, int]):
        self.pos = list(pos)

    def draw(self, surface: pygame.Surface):
        if not self.sprite:
            return
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
        display_sprite_id: str = None,
        is_pickable: bool = True,
        hide_on_drag: bool = False,
        scale: float = 1.0,
        label: str = None,
        on_click=None,
        visible: bool = True,
    ):
        self.x = x
        self.y = y
        self.item_id = item_id
        self.display_sprite_id = display_sprite_id or item_id
        self.is_pickable = is_pickable
        self.hide_on_drag = hide_on_drag
        self.scale = scale
        self.label = label or get_item_name(item_id)
        self.on_click = on_click
        self.visible = visible
        self.is_held = False
        self.is_hovered = False

        spr = self.sprite
        if spr:
            self.width = int(spr.get_width() * scale)
            self.height = int(spr.get_height() * scale)
        else:
            self.width, self.height = 120, 100
        self.rect = pygame.Rect(x, y, self.width, self.height)

    @property
    def sprite(self) -> pygame.Surface | None:
        return assets.get_sprite(self.display_sprite_id) or assets.get_sprite(self.item_id)

    @property
    def shadow_sprite(self) -> pygame.Surface | None:
        return assets.get_shadow_sprite(self.display_sprite_id, alpha=80) or assets.get_shadow_sprite(self.item_id, alpha=80)

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
                shadow_to_draw = pygame.transform.smoothscale(shadow_spr, (draw_w, draw_h)) if shadow_spr else None
            else:
                spr_to_draw = spr
                shadow_to_draw = shadow_spr

            if shadow_to_draw:
                surface.blit(shadow_to_draw, (self.rect.x + 4, self.rect.y + 8))

            if self.is_hovered:
                out_spr, pad = assets.get_outlined_sprite(
                    self.display_sprite_id, outline_color=(255, 255, 255), thickness=3, scale=self.scale
                )
                if out_spr:
                    surface.blit(out_spr, (self.rect.x - pad, self.rect.y - pad - 2))
                else:
                    surface.blit(spr_to_draw, (self.rect.x, self.rect.y))
            else:
                surface.blit(spr_to_draw, (self.rect.x, self.rect.y))


class TrashCan:
    def __init__(self, x: int = TRASH_CAN_POS[0], y: int = TRASH_CAN_POS[1], width: int = TRASH_CAN_SIZE[0], height: int = TRASH_CAN_SIZE[1]):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.is_hovered = False

    def contains_point(self, pos: tuple[int, int]) -> bool:
        return self.rect.inflate(20, 20).collidepoint(pos)

    def draw(self, surface: pygame.Surface):
        trash_spr = assets.get_sprite("trash")
        if trash_spr:
            scale = 0.80
            draw_w = int(trash_spr.get_width() * scale)
            draw_h = int(trash_spr.get_height() * scale)
            scaled_trash = pygame.transform.smoothscale(trash_spr, (draw_w, draw_h))
            draw_pos = (self.x + (self.width - draw_w) // 2, self.y + (self.height - draw_h) // 2)

            if self.is_hovered:
                out_spr, pad = assets.get_outlined_sprite("trash", outline_color=(255, 255, 255), thickness=4, scale=scale)
                if out_spr:
                    surface.blit(out_spr, (draw_pos[0] - pad, draw_pos[1] - pad))
                else:
                    surface.blit(scaled_trash, draw_pos)
            else:
                surface.blit(scaled_trash, draw_pos)


BOWL_SCALE = 0.80
BOWL_MEATBALL_OFFSETS = [(90, 75), (210, 70), (150, 110), (80, 120), (220, 125), (150, 50)]
BOWL_NOODLE_OFFSET = (70, 50)
BOWL_GORENGAN_OFFSET = (180, 35)


class Bowl:
    def __init__(self, x: int = BOWL_HOME_POS[0], y: int = BOWL_HOME_POS[1], scale: float = BOWL_SCALE):
        self.home_x = x
        self.home_y = y
        self.x = x
        self.y = y
        self.scale = scale

        raw_back = assets.get_sprite("mangkok-back")
        raw_front = assets.get_sprite("mangkok-front")
        raw_main = assets.get_sprite("mangkok")

        if scale != 1.0:
            self.sprite_back = pygame.transform.smoothscale(raw_back, (int(raw_back.get_width() * scale), int(raw_back.get_height() * scale))) if raw_back else None
            self.sprite_front = pygame.transform.smoothscale(raw_front, (int(raw_front.get_width() * scale), int(raw_front.get_height() * scale))) if raw_front else None
            self.sprite = pygame.transform.smoothscale(raw_main, (int(raw_main.get_width() * scale), int(raw_main.get_height() * scale))) if raw_main else None
        else:
            self.sprite_back = raw_back
            self.sprite_front = raw_front
            self.sprite = raw_main

        raw_shadow = assets.get_shadow_sprite("mangkok", alpha=80)
        raw_drag_shadow = assets.get_shadow_sprite("mangkok", alpha=110)
        self.shadow_sprite = pygame.transform.smoothscale(raw_shadow, (int(raw_shadow.get_width() * scale), int(raw_shadow.get_height() * scale))) if (scale != 1.0 and raw_shadow) else raw_shadow
        self.drag_shadow_sprite = pygame.transform.smoothscale(raw_drag_shadow, (int(raw_drag_shadow.get_width() * scale), int(raw_drag_shadow.get_height() * scale))) if (scale != 1.0 and raw_drag_shadow) else raw_drag_shadow

        ref = self.sprite_back or self.sprite or self.sprite_front
        self.width = ref.get_width() if ref else int(400 * scale)
        self.height = ref.get_height() if ref else int(300 * scale)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.is_dragging = False
        self.is_hovered = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.ingredients: list[dict] = []

    def contains_point(self, pos: tuple[int, int]) -> bool:
        return self.rect.inflate(24, 24).collidepoint(pos)

    def update_hover(self, pos: tuple[int, int]):
        self.is_hovered = not self.is_dragging and self.contains_point(pos)

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

    def place_on_counter(self, min_x: int = 40, max_x: int = 1880, min_y: int = 690, max_y: int = 994):
        self.is_dragging = False
        self.x = max(min_x, min(max_x - self.width, self.x))
        self.y = max(min_y, min(max_y - self.height, self.y))
        self.home_x = self.x
        self.home_y = self.y
        self.rect.topleft = (self.x, self.y)

    def add_ingredient(self, item_id: str, drop_pos: tuple[int, int] = None) -> bool:
        spr = assets.get_sprite(item_id)
        sw = int((spr.get_width() if spr else 80) * self.scale)
        sh = int((spr.get_height() if spr else 80) * self.scale)

        if drop_pos:
            rel_x = (drop_pos[0] - self.x - sw // 2) / self.scale
            rel_y = (drop_pos[1] - self.y - sh // 2) / self.scale
            min_x, max_x = 30, (self.width - sw) / self.scale - 30
            min_y, max_y = 20, (self.height - sh) / self.scale - 70
            rel_x = max(min_x, min(max(min_x, max_x), rel_x))
            rel_y = max(min_y, min(max(min_y, max_y), rel_y))
        else:
            count = len(self.ingredients)
            if item_id in ["daun_bawang", "daun-bawang"]:
                rel_x, rel_y = 45, 65
            elif item_id in ["bawang_goreng", "bawang-goreng"]:
                rel_x, rel_y = 45, 80
            elif item_id in ["kecap", "saos_sambal", "saos-sambal", "saos_tomat", "saos-tomat"]:
                rel_x, rel_y = 110 + (count % 3 * 25), 85 + (count % 2 * 15)
            elif "mi" in item_id:
                rel_x = BOWL_NOODLE_OFFSET[0] + (count % 2 * 10 - 5)
                rel_y = BOWL_NOODLE_OFFSET[1] + (count % 2 * 10)
            elif "gorengan" in item_id:
                rel_x = BOWL_GORENGAN_OFFSET[0]
                rel_y = BOWL_GORENGAN_OFFSET[1] + (count % 3 * 15)
            else:
                idx = count % len(BOWL_MEATBALL_OFFSETS)
                rel_x, rel_y = BOWL_MEATBALL_OFFSETS[idx]

        self.ingredients.append({"type": item_id, "offset_x": int(rel_x), "offset_y": int(rel_y)})
        return True

    def clear(self):
        self.ingredients.clear()

    def get_ingredient_counts(self) -> dict[str, int]:
        counts = {}
        for it in self.ingredients:
            cid = get_canonical_item_id(it["type"])
            counts[cid] = counts.get(cid, 0) + 1
        return counts

    def draw(self, surface: pygame.Surface):
        if self.is_dragging:
            if self.drag_shadow_sprite:
                surface.blit(self.drag_shadow_sprite, (self.x + 8, self.y + 16))
        else:
            if self.shadow_sprite:
                surface.blit(self.shadow_sprite, (self.x + 4, self.y + 8))

        if self.is_hovered and not self.is_dragging:
            out_spr, pad = assets.get_outlined_sprite("mangkok", outline_color=(255, 255, 255), thickness=4, scale=self.scale)
            if out_spr:
                surface.blit(out_spr, (self.x - pad, self.y - pad))

        if self.sprite_back:
            surface.blit(self.sprite_back, (self.x, self.y))
        elif self.sprite:
            surface.blit(self.sprite, (self.x, self.y))

        def layer_key(it):
            t = it["type"]
            if t in ["daun_bawang", "daun-bawang", "bawang_goreng", "bawang-goreng", "kecap", "saos_sambal", "saos_tomat"]:
                return (1, it["offset_y"])
            return (0, it["offset_y"])

        for it in sorted(self.ingredients, key=layer_key):
            item_type = it["type"]
            spr = assets.get_sprite(item_type)
            shadow_spr = assets.get_shadow_sprite(item_type, alpha=70)
            if spr:
                if item_type in ["kecap", "saos_sambal", "saos_tomat", "saos-sambal", "saos-tomat"]:
                    ing_scale = self.scale * 0.50
                elif item_type in ["mi_kuning", "mi-kuning", "mi_bihun", "mi-bihun"]:
                    ing_scale = self.scale * 0.85
                else:
                    ing_scale = self.scale

                sw, sh = int(spr.get_width() * ing_scale), int(spr.get_height() * ing_scale)
                spr_to_draw = pygame.transform.smoothscale(spr, (sw, sh))
                shadow_to_draw = pygame.transform.smoothscale(shadow_spr, (sw, sh)) if shadow_spr else None

                if item_type in ["kecap", "saos_sambal", "saos_tomat", "saos-sambal", "saos-tomat"]:
                    spr_to_draw.set_alpha(205)
                    if shadow_to_draw:
                        shadow_to_draw.set_alpha(60)

                draw_x = self.x + int(it["offset_x"] * self.scale)
                draw_y = self.y + int(it["offset_y"] * self.scale)

                if shadow_to_draw:
                    surface.blit(shadow_to_draw, (draw_x + 4, draw_y + 4))
                surface.blit(spr_to_draw, (draw_x, draw_y))

        if self.sprite_front:
            surface.blit(self.sprite_front, (self.x, self.y))
        elif self.sprite:
            surface.blit(self.sprite, (self.x, self.y))


class Order:
    def __init__(self, items: dict[str, int]):
        self.items = items
        self.total_price = self.calculate_price()

    @classmethod
    def generate_random(cls, day: int = 1) -> "Order":
        items = {}
        unlocked = get_unlocked_items(day)

        has_kuning = "mi_kuning" in unlocked
        has_bihun = "mi_bihun" in unlocked
        noodle_options = ["none"]
        if has_kuning and has_bihun:
            noodle_options.extend(["mi_kuning", "mi_kuning", "mi_bihun", "mi_bihun", "both", "mi_kuning_2", "mi_bihun_2"])
        elif has_kuning:
            noodle_options.extend(["mi_kuning", "mi_kuning", "mi_kuning_2"])
        elif has_bihun:
            noodle_options.extend(["mi_bihun", "mi_bihun", "mi_bihun_2"])

        noodle_choice = random.choice(noodle_options)
        if noodle_choice == "mi_kuning":
            items["mi_kuning"] = 1
        elif noodle_choice == "mi_bihun":
            items["mi_bihun"] = 1
        elif noodle_choice == "both":
            items["mi_kuning"] = 1
            items["mi_bihun"] = 1
        elif noodle_choice == "mi_kuning_2":
            items["mi_kuning"] = 2
        elif noodle_choice == "mi_bihun_2":
            items["mi_bihun"] = 2

        if "bakso_halus" in unlocked:
            items["bakso_halus"] = random.choice([1, 2, 2, 3, 3, 4])
        if "tahu" in unlocked and random.random() < 0.50:
            items["tahu"] = random.choice([1, 1, 2])
        if "gorengan_panjang" in unlocked and random.random() < 0.50:
            items["gorengan_panjang"] = random.choice([1, 1, 2])
        if "daun_bawang" in unlocked and random.random() < 0.65:
            items["daun_bawang"] = 1
        if "bawang_goreng" in unlocked and random.random() < 0.65:
            items["bawang_goreng"] = 1
        if "kecap" in unlocked and random.random() < 0.45:
            items["kecap"] = 1
        if "saos_sambal" in unlocked and random.random() < 0.45:
            items["saos_sambal"] = 1
        if "saos_tomat" in unlocked and random.random() < 0.35:
            items["saos_tomat"] = 1

        if not items:
            items["bakso_halus"] = 1
        return cls(items)

    def calculate_price(self) -> int:
        price = BASE_BOWL_PRICE
        for item_id, count in self.items.items():
            price += count * get_item_price(item_id)
        return price

    def matches(self, bowl_items: dict[str, int]) -> bool:
        normalized = {}
        for raw_id, count in bowl_items.items():
            cid = get_canonical_item_id(raw_id)
            normalized[cid] = normalized.get(cid, 0) + count

        for k, count in self.items.items():
            cid = get_canonical_item_id(k)
            if normalized.get(cid, 0) != count:
                return False
        for k, count in normalized.items():
            cid = get_canonical_item_id(k)
            if self.items.get(cid, 0) != count:
                return False
        return True

    def draw_ticket(self, surface: pygame.Surface, x: int = ORDER_TICKET_POS[0], y: int = ORDER_TICKET_POS[1], width: int = ORDER_TICKET_SIZE[0], height: int = ORDER_TICKET_SIZE[1]):
        active_items = [(k, v) for k, v in self.items.items() if v > 0]
        needed_height = max(height, 56 + len(active_items) * 32 + 48)
        ticket_rect = pygame.Rect(x, y, width, needed_height)

        shadow_rect = ticket_rect.copy()
        shadow_rect.move_ip(4, 6)
        pygame.draw.rect(surface, (0, 0, 0, 60), shadow_rect, border_radius=10)
        pygame.draw.rect(surface, (255, 248, 230), ticket_rect, border_radius=10)
        pygame.draw.rect(surface, (180, 150, 110), ticket_rect, 3, border_radius=10)

        hdr_surf = assets.render_text("ORDER", size=28, color=(70, 40, 40))
        surface.blit(hdr_surf, (x + 14, y + 10))
        pygame.draw.line(surface, (180, 150, 110), (x + 12, y + 44), (x + width - 12, y + 44), 2)

        curr_y = y + 52
        for item_id, count in active_items:
            spr = assets.get_sprite(item_id)
            if spr:
                sw, sh = spr.get_size()
                ratio = min(1.0, 28 / max(1, sw), 28 / max(1, sh))
                tw, th = int(sw * ratio), int(sh * ratio)
                thumb = pygame.transform.smoothscale(spr, (tw, th))
                surface.blit(thumb, (x + 14, curr_y))
                txt = f"{get_item_name(item_id)} x{count}"
                txt_surf = assets.render_text(txt, size=24, color=(70, 40, 40))
                surface.blit(txt_surf, (x + 14 + 36, curr_y + max(0, (th - txt_surf.get_height()) // 2)))
                curr_y += max(th, 22) + 6
            else:
                txt_surf = assets.render_text(f"{get_item_name(item_id)}: {count}", size=22, color=(70, 40, 40))
                surface.blit(txt_surf, (x + 14, curr_y))
                curr_y += 28

        price_str = f"Rp {self.total_price:,}"
        price_surf = assets.render_text(price_str, size=26, color=(160, 90, 30))
        surface.blit(price_surf, (x + width - price_surf.get_width() - 14, y + needed_height - 38))


CUSTOMER_NAMES = ["Wowo Sawit", "Fufufafa", "Tung Tung Tung Sahur", "Mulyono"]


class Customer:
    def __init__(self, x: int = CUSTOMER_POS[0], y: int = CUSTOMER_POS[1], scale: float = 1.0, day: int = 1):
        self.x = x
        self.y = y
        self.scale = scale
        self.day = day
        self.name = random.choice(CUSTOMER_NAMES)
        self.order = Order.generate_random(day=day)
        self.patience_max = DEFAULT_PATIENCE_TIME
        self.patience = DEFAULT_PATIENCE_TIME
        self.state = "waiting"
        self.feedback_timer = 0.0

        raw_spr = assets.get_sprite("customer")
        raw_shadow = assets.get_shadow_sprite("customer", alpha=80)
        self.sprite = pygame.transform.smoothscale(raw_spr, (int(raw_spr.get_width() * scale), int(raw_spr.get_height() * scale))) if (scale != 1.0 and raw_spr) else raw_spr
        self.shadow_sprite = pygame.transform.smoothscale(raw_shadow, (int(raw_shadow.get_width() * scale), int(raw_shadow.get_height() * scale))) if (scale != 1.0 and raw_shadow) else raw_shadow

        self.width = self.sprite.get_width() if self.sprite else 352
        self.height = self.sprite.get_height() if self.sprite else 408

    def update(self, dt: float):
        if self.state == "waiting":
            self.patience -= dt
            if self.patience <= 0:
                self.patience = 0
                self.state = "angry"
                self.feedback_timer = 2.0
        elif self.state in ["happy", "angry"]:
            self.feedback_timer -= dt
            if self.feedback_timer <= 0:
                self.state = "done"

    def contains_point(self, pos: tuple[int, int]) -> bool:
        return pygame.Rect(self.x - 140, self.y - 115, 280, 230).collidepoint(pos)

    def serve(self, bowl_items: dict[str, int]) -> tuple[bool, int]:
        if self.state != "waiting":
            return False, 0
        if self.order.matches(bowl_items):
            self.state = "happy"
            self.feedback_timer = 1.8
            return True, self.order.total_price
        else:
            self.state = "angry"
            self.feedback_timer = 1.8
            return False, 0

    def draw(self, surface: pygame.Surface):
        draw_x = self.x - self.width // 2
        draw_y = self.y - self.height // 2

        if self.shadow_sprite:
            surface.blit(self.shadow_sprite, (draw_x + 6, draw_y + 10))
        if self.sprite:
            surface.blit(self.sprite, (draw_x, draw_y))

        if self.state == "waiting":
            name_surf = assets.render_text_with_shadow(self.name, size=26, color=COLOR_BLACK, shadow_color=COLOR_WHITE, offset=(1, 1))
            surface.blit(name_surf, (self.x - name_surf.get_width() // 2, draw_y - 48))

            bar_w, bar_h = 160, 12
            bar_x = self.x - bar_w // 2
            bar_y = draw_y - 18
            ratio = max(0.0, self.patience / self.patience_max)
            bar_color = (70, 210, 90) if ratio > 0.3 else (240, 70, 60)

            pygame.draw.rect(surface, (30, 25, 20), (bar_x - 2, bar_y - 2, bar_w + 4, bar_h + 4), border_radius=6)
            pygame.draw.rect(surface, (70, 65, 60), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
            if ratio > 0:
                pygame.draw.rect(surface, bar_color, (bar_x, bar_y, int(bar_w * ratio), bar_h), border_radius=4)
        elif self.state == "happy":
            fb_surf = assets.render_text_with_shadow("CORRECT", size=34, color=(60, 240, 80), shadow_color=(20, 60, 20), offset=(2, 2))
            surface.blit(fb_surf, (self.x - fb_surf.get_width() // 2, draw_y - 56))
        elif self.state == "angry":
            fb_surf = assets.render_text_with_shadow("WRONG", size=34, color=(255, 75, 75), shadow_color=(80, 20, 20), offset=(2, 2))
            surface.blit(fb_surf, (self.x - fb_surf.get_width() // 2, draw_y - 56))


class GameScene(BaseScene):
    def __init__(self, save_data: dict = None):
        super().__init__()
        if save_data:
            self.day = save_data.get("day", 1)
            self.money = save_data.get("money", INITIAL_MONEY)
            self.reputation = save_data.get("reputation", INITIAL_REPUTATION)
        else:
            self.day = 1
            self.money = INITIAL_MONEY
            self.reputation = INITIAL_REPUTATION
            self.persist_save()

        self.state = "PLAYING"
        self.is_time_paused = False
        self.elapsed_seconds = 0.0
        self.target_customers = random.randint(MIN_CUSTOMERS_PER_DAY, MAX_CUSTOMERS_PER_DAY)
        self.customers_spawned = 1
        self.day_earnings = 0
        self.customers_served = 0
        self.customers_failed = 0

        self.cached_bg = None
        self.cached_gerobak = None

        self.bowl = Bowl(x=BOWL_HOME_POS[0], y=BOWL_HOME_POS[1])
        self.trash_can = TrashCan(x=TRASH_CAN_POS[0], y=TRASH_CAN_POS[1])

        self.trays: list[IngredientTray] = []
        for cfg in FOOD_STATIONS_LAYOUT:
            on_click = (lambda: assets.play_sound("bakso.mp3", volume=1.0)) if cfg["id"] == "kentongan" else None
            tray = IngredientTray(
                x=cfg["x"],
                y=cfg["y"],
                item_id=cfg["id"],
                display_sprite_id=cfg.get("display_sprite"),
                is_pickable=cfg.get("is_pickable", True),
                hide_on_drag=cfg.get("hide_on_drag", False),
                scale=cfg.get("scale", 1.0),
                label=cfg.get("label"),
                on_click=on_click,
            )
            self.trays.append(tray)

        self.update_tray_unlocks()
        self.current_customer: Customer | None = Customer(x=CUSTOMER_POS[0], y=CUSTOMER_POS[1], day=self.day)
        self.customer_spawn_timer = 0.0
        self.dragged_item: DraggedItem | None = None

        self.pause_btn_rect = pygame.Rect(PAUSE_BTN_POS[0], PAUSE_BTN_POS[1], PAUSE_BTN_SIZE[0], PAUSE_BTN_SIZE[1])
        self.next_day_btn_rect = pygame.Rect(INTERNAL_WIDTH // 2 - 140, 680, 280, 72)
        self.restart_btn_rect = pygame.Rect(INTERNAL_WIDTH // 2 - 140, 640, 280, 72)
        self.pause_btn_hovered = False
        self.next_day_hovered = False
        self.restart_hovered = False

    def update_tray_unlocks(self):
        unlocked = get_unlocked_items(self.day)
        for tray in self.trays:
            if tray.item_id in ["kuah", "kentongan"]:
                tray.visible = True
            else:
                tray.visible = tray.item_id in unlocked

    def persist_save(self):
        save_manager.save_game({"day": self.day, "money": self.money, "reputation": self.reputation})

    def open_pause_menu(self):
        from ui import PauseScene
        if self.dragged_item and self.dragged_item.source_tray:
            self.dragged_item.source_tray.is_held = False
        self.dragged_item = None
        self.bowl.reset_position()
        self.trash_can.is_hovered = False
        self.manager.push_scene(PauseScene(game_scene=self))

    def serve_current_bowl(self):
        if not self.current_customer or self.current_customer.state != "waiting":
            return
        bowl_contents = self.bowl.get_ingredient_counts()
        is_correct, earned = self.current_customer.serve(bowl_contents)

        if is_correct:
            self.money += earned
            self.day_earnings += earned
            self.reputation = min(100, self.reputation + REPUTATION_GAIN)
            self.customers_served += 1
        else:
            self.reputation = max(0, self.reputation - REPUTATION_LOSS)
            self.customers_failed += 1
            if self.reputation <= 0:
                self.state = "GAME_OVER"
                save_manager.delete_save()
        self.bowl.clear()

    def handle_event(self, event: pygame.event.Event, mouse_canvas_pos: tuple[int, int]):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_ESCAPE, pygame.K_p]:
                self.open_pause_menu()
                return
            elif event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                self.serve_current_bowl()
                return
            elif event.key in [pygame.K_c, pygame.K_BACKSPACE]:
                self.bowl.clear()
                return
            elif event.key == pygame.K_F4:
                self.is_time_paused = not self.is_time_paused
                return

        if self.state == "PLAYING":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.pause_btn_rect.collidepoint(mouse_canvas_pos):
                    assets.play_sound("click2.ogg", volume=1.0)
                    self.open_pause_menu()
                    return

                tray_clicked = False
                for tray in self.trays:
                    drag = tray.handle_mouse_down(mouse_canvas_pos)
                    if drag:
                        self.dragged_item = drag
                        tray_clicked = True
                        break

                if not tray_clicked and self.bowl.contains_point(mouse_canvas_pos):
                    self.bowl.start_drag(mouse_canvas_pos)

            elif event.type == pygame.MOUSEMOTION:
                if self.dragged_item:
                    self.dragged_item.update(mouse_canvas_pos)

                if self.bowl.is_dragging:
                    self.bowl.update_drag(mouse_canvas_pos)
                    bowl_center = (self.bowl.x + self.bowl.width // 2, self.bowl.y + self.bowl.height // 2)
                    self.trash_can.is_hovered = self.trash_can.contains_point(bowl_center) or self.trash_can.contains_point(mouse_canvas_pos)
                else:
                    self.trash_can.is_hovered = False

                for tray in self.trays:
                    tray.update_hover(mouse_canvas_pos)
                self.bowl.update_hover(mouse_canvas_pos)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.dragged_item:
                    source = self.dragged_item.source_tray
                    if self.bowl.contains_point(mouse_canvas_pos):
                        self.bowl.add_ingredient(self.dragged_item.item_id, drop_pos=mouse_canvas_pos)
                    if source:
                        source.is_held = False
                    self.dragged_item = None

                if self.bowl.is_dragging:
                    bowl_center = (self.bowl.x + self.bowl.width // 2, self.bowl.y + self.bowl.height // 2)
                    if self.trash_can.contains_point(bowl_center) or self.trash_can.contains_point(mouse_canvas_pos):
                        self.bowl.clear()
                        self.bowl.reset_position()
                    elif self.current_customer and self.current_customer.contains_point(bowl_center):
                        self.serve_current_bowl()
                        self.bowl.reset_position()
                    else:
                        self.bowl.place_on_counter()
                    self.trash_can.is_hovered = False

        elif self.state == "DAY_SUMMARY":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.next_day_btn_rect.collidepoint(mouse_canvas_pos):
                    assets.play_sound("click2.ogg", volume=1.0)
                    self.start_next_day()

        elif self.state == "GAME_OVER":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.restart_btn_rect.collidepoint(mouse_canvas_pos):
                    assets.play_sound("click2.ogg", volume=1.0)
                    self.restart_game()

    def update(self, dt: float):
        if self.state == "PLAYING":
            if not self.is_time_paused:
                self.elapsed_seconds += dt

            if self.current_customer:
                if not self.is_time_paused:
                    self.current_customer.update(dt)
                if self.current_customer.state == "angry" and self.current_customer.patience == 0 and self.current_customer.feedback_timer >= 1.95:
                    self.reputation = max(0, self.reputation - REPUTATION_LOSS)
                    self.customers_failed += 1
                    if self.reputation <= 0:
                        self.state = "GAME_OVER"
                        save_manager.delete_save()
                        return

                if self.current_customer.state == "done":
                    self.current_customer = None
                    if self.customers_spawned < self.target_customers:
                        self.customer_spawn_timer = 1.0
                    else:
                        self.state = "DAY_SUMMARY"
                        self.persist_save()
                        return
            else:
                if self.customers_spawned < self.target_customers:
                    if not self.is_time_paused:
                        self.customer_spawn_timer -= dt
                    if self.customer_spawn_timer <= 0:
                        self.current_customer = Customer(x=CUSTOMER_POS[0], y=CUSTOMER_POS[1], day=self.day)
                        self.customers_spawned += 1

    def start_next_day(self):
        self.day += 1
        self.elapsed_seconds = 0.0
        self.day_earnings = 0
        self.customers_served = 0
        self.customers_failed = 0
        self.update_tray_unlocks()
        self.target_customers = random.randint(MIN_CUSTOMERS_PER_DAY, MAX_CUSTOMERS_PER_DAY)
        self.customers_spawned = 1
        self.current_customer = Customer(x=CUSTOMER_POS[0], y=CUSTOMER_POS[1], day=self.day)
        self.bowl.clear()
        self.bowl.reset_position()
        if self.dragged_item and self.dragged_item.source_tray:
            self.dragged_item.source_tray.is_held = False
        self.dragged_item = None
        self.persist_save()
        self.state = "PLAYING"

    def restart_game(self):
        self.day = 1
        self.money = INITIAL_MONEY
        self.reputation = INITIAL_REPUTATION
        self.elapsed_seconds = 0.0
        self.day_earnings = 0
        self.customers_served = 0
        self.customers_failed = 0
        self.update_tray_unlocks()
        self.target_customers = random.randint(MIN_CUSTOMERS_PER_DAY, MAX_CUSTOMERS_PER_DAY)
        self.customers_spawned = 1
        self.current_customer = Customer(x=CUSTOMER_POS[0], y=CUSTOMER_POS[1], day=self.day)
        self.bowl.clear()
        self.bowl.reset_position()
        if self.dragged_item and self.dragged_item.source_tray:
            self.dragged_item.source_tray.is_held = False
        self.dragged_item = None
        self.persist_save()
        self.state = "PLAYING"

    def draw_environment(self, canvas: pygame.Surface):
        bg_spr = assets.get_sprite("background")
        if bg_spr:
            if self.cached_bg is None:
                bw, bh = bg_spr.get_size()
                scale = max(INTERNAL_WIDTH / bw, INTERNAL_HEIGHT / bh)
                rw, rh = int(bw * scale), int(bh * scale)
                self.cached_bg = pygame.transform.smoothscale(bg_spr, (rw, rh))
            canvas.blit(self.cached_bg, ((INTERNAL_WIDTH - self.cached_bg.get_width()) // 2, 0))
            dim_surf = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
            dim_surf.fill((0, 0, 0, 26))
            canvas.blit(dim_surf, (0, 0))
        else:
            canvas.fill(COLOR_BG_CYAN)

        gerobak_spr = assets.get_sprite("gerobak") or assets.get_sprite("main")
        if gerobak_spr:
            if self.cached_gerobak is None:
                gw, gh = gerobak_spr.get_size()
                scale = max(INTERNAL_WIDTH / gw, INTERNAL_HEIGHT / gh)
                rw, rh = int(gw * scale), int(gh * scale)
                self.cached_gerobak = pygame.transform.smoothscale(gerobak_spr, (rw, rh))
            gx = (INTERNAL_WIDTH - self.cached_gerobak.get_width()) // 2
            gy = (INTERNAL_HEIGHT - self.cached_gerobak.get_height()) // 2
            canvas.blit(self.cached_gerobak, (gx, gy))

    def draw_hud(self, canvas: pygame.Surface):
        hud_bar = pygame.Surface((INTERNAL_WIDTH, HUD_HEIGHT), pygame.SRCALPHA)
        hud_bar.fill((35, 25, 20, 220))
        pygame.draw.line(hud_bar, COLOR_GOLD, (0, HUD_HEIGHT - 1), (INTERNAL_WIDTH, HUD_HEIGHT - 1), 3)
        canvas.blit(hud_bar, (0, 0))

        total_secs = int(10 * 3600 + self.elapsed_seconds)
        hour = (total_secs // 3600) % 24
        minute = (total_secs % 3600) // 60
        second = total_secs % 60

        cust_curr = min(self.target_customers, self.customers_spawned)
        hud_left = f"DAY {self.day}  |  TIME: {hour:02d}:{minute:02d}:{second:02d}  |  CUSTOMER: {cust_curr}/{self.target_customers}"
        surf_left = assets.render_text_with_shadow(hud_left, size=30, color=COLOR_WHITE, shadow_color=(20, 15, 10), offset=(2, 2))
        canvas.blit(surf_left, (32, 18))

        if self.is_time_paused:
            pause_tag = assets.render_text_with_shadow("[DEBUG: TIME PAUSED (F4)]", size=22, color=(255, 220, 60), shadow_color=(40, 20, 10), offset=(1, 2))
            canvas.blit(pause_tag, (32 + surf_left.get_width() + 24, 21))

        money_str = f"Income: Rp{self.money:,}"
        surf_money = assets.render_text_with_shadow(money_str, size=30, color=COLOR_GOLD, shadow_color=(40, 25, 10), offset=(2, 2))
        canvas.blit(surf_money, (INTERNAL_WIDTH // 2 - surf_money.get_width() // 2, 17))

        rep_txt = f"Reputation: {self.reputation}%"
        surf_rep = assets.render_text_with_shadow(rep_txt, size=30, color=COLOR_WHITE, shadow_color=(20, 15, 10), offset=(2, 2))
        canvas.blit(surf_rep, (INTERNAL_WIDTH - surf_rep.get_width() - 110, 18))

        mouse_pos = self.manager.app.window_to_canvas_pos(pygame.mouse.get_pos()) if (self.manager and self.manager.app) else (0, 0)
        is_hover = self.pause_btn_rect.collidepoint(mouse_pos)
        if is_hover and not self.pause_btn_hovered:
            assets.play_sound("click1.ogg", volume=0.3)
        self.pause_btn_hovered = is_hover

        pause_btn_surf = assets.get_9slice_surface("button", self.pause_btn_rect.width, self.pause_btn_rect.height, slice_margin=20)
        canvas.blit(pause_btn_surf, self.pause_btn_rect.topleft)
        if is_hover:
            pygame.draw.rect(canvas, (255, 255, 255), self.pause_btn_rect.inflate(4, 4), width=3, border_radius=12)

        txt_pause = assets.render_text("||", size=24, color=(0, 0, 0))
        canvas.blit(txt_pause, (self.pause_btn_rect.centerx - txt_pause.get_width() // 2, self.pause_btn_rect.centery - txt_pause.get_height() // 2))

    def draw_summary_overlay(self, canvas: pygame.Surface):
        overlay = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        canvas.blit(overlay, (0, 0))

        card = pygame.Rect(INTERNAL_WIDTH // 2 - 340, 240, 680, 540)
        bg_surf = assets.get_9slice_surface("ui-background", card.width, card.height, slice_margin=32)
        canvas.blit(bg_surf, card.topleft)

        title = assets.render_text(f"DAY {self.day} FINISHED!", size=42, color=COLOR_WHITE)
        canvas.blit(title, (card.centerx - title.get_width() // 2, card.top + 40))

        y = card.top + 115
        line1 = assets.render_text(f"Pesanan Berhasil : {self.customers_served}", size=30, color=COLOR_WHITE)
        line2 = assets.render_text(f"Pesanan Gagal/Kabur : {self.customers_failed}", size=30, color=COLOR_WHITE)
        line3 = assets.render_text(f"Total Income : Rp {self.money:,}", size=32, color=COLOR_WHITE)
        canvas.blit(line1, (card.left + 56, y))
        canvas.blit(line2, (card.left + 56, y + 54))
        canvas.blit(line3, (card.left + 56, y + 108))

        mouse_pos = self.manager.app.window_to_canvas_pos(pygame.mouse.get_pos()) if (self.manager and self.manager.app) else (0, 0)
        is_hover = self.next_day_btn_rect.collidepoint(mouse_pos)
        if is_hover and not self.next_day_hovered:
            assets.play_sound("click1.ogg", volume=0.3)
        self.next_day_hovered = is_hover

        btn_surf = assets.get_9slice_surface("button", self.next_day_btn_rect.width, self.next_day_btn_rect.height)
        canvas.blit(btn_surf, self.next_day_btn_rect.topleft)
        if is_hover:
            pygame.draw.rect(canvas, (255, 255, 255), self.next_day_btn_rect.inflate(6, 6), width=4, border_radius=16)

        btn_txt = assets.render_text("NEXT DAY", size=30, color=(0, 0, 0))
        canvas.blit(btn_txt, (self.next_day_btn_rect.centerx - btn_txt.get_width() // 2, self.next_day_btn_rect.centery - btn_txt.get_height() // 2))

    def draw_game_over_overlay(self, canvas: pygame.Surface):
        overlay = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((100, 0, 0, 210))
        canvas.blit(overlay, (0, 0))

        card = pygame.Rect(INTERNAL_WIDTH // 2 - 320, 260, 640, 480)
        bg_surf = assets.get_9slice_surface("ui-background", card.width, card.height, slice_margin=32)
        canvas.blit(bg_surf, card.topleft)

        title = assets.render_text("BANGKRUT / REPUTASI HABIS!", size=40, color=(255, 60, 60))
        canvas.blit(title, (card.centerx - title.get_width() // 2, card.top + 40))

        sub = assets.render_text("Gerobak Anda terpaksa tutup hari ini...", size=26, color=(255, 230, 230))
        canvas.blit(sub, (card.centerx - sub.get_width() // 2, card.top + 100))

        earned_txt = assets.render_text(f"Total Penghasilan Akhir: Rp {self.money:,}", size=28, color=COLOR_WHITE)
        canvas.blit(earned_txt, (card.centerx - earned_txt.get_width() // 2, card.top + 160))

        mouse_pos = self.manager.app.window_to_canvas_pos(pygame.mouse.get_pos()) if (self.manager and self.manager.app) else (0, 0)
        is_hover = self.restart_btn_rect.collidepoint(mouse_pos)
        if is_hover and not self.restart_hovered:
            assets.play_sound("click1.ogg", volume=0.3)
        self.restart_hovered = is_hover

        btn_surf = assets.get_9slice_surface("button", self.restart_btn_rect.width, self.restart_btn_rect.height)
        canvas.blit(btn_surf, self.restart_btn_rect.topleft)
        if is_hover:
            pygame.draw.rect(canvas, (255, 255, 255), self.restart_btn_rect.inflate(6, 6), width=4, border_radius=16)

        btn_txt = assets.render_text("RESTART", size=30, color=(0, 0, 0))
        canvas.blit(btn_txt, (self.restart_btn_rect.centerx - btn_txt.get_width() // 2, self.restart_btn_rect.centery - btn_txt.get_height() // 2))

    def draw(self, canvas: pygame.Surface):
        self.draw_environment(canvas)

        if self.current_customer:
            self.current_customer.draw(canvas)
            if self.current_customer.state == "waiting":
                self.current_customer.order.draw_ticket(canvas)

        for tray in self.trays:
            if tray.item_id == "kuah":
                tray.draw(canvas)
        self.trash_can.draw(canvas)
        for tray in self.trays:
            if tray.item_id != "kuah":
                tray.draw(canvas)

        self.bowl.draw(canvas)

        if self.dragged_item:
            self.dragged_item.draw(canvas)

        self.draw_hud(canvas)

        if self.state == "DAY_SUMMARY":
            self.draw_summary_overlay(canvas)
        elif self.state == "GAME_OVER":
            self.draw_game_over_overlay(canvas)
