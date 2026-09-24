import random
import pygame

from config import DEFAULT_PATIENCE_TIME
from core.assets import assets
from entities.order import Order

CUSTOMER_POS = (650, 315)
CUSTOMER_SCALE = 1.0
CUSTOMER_DROPZONE_SIZE = (280, 230)
COLOR_PATIENCE_BAR = (70, 210, 90)
COLOR_PATIENCE_LOW = (240, 70, 60)
COLOR_BLACK = (0, 0, 0)

CUSTOMER_NAMES = [
    "Mas Budi",
    "Pak Haji",
    "Mbak Siti",
    "Bang Ojol",
    "Bocil SD",
    "Bu RT",
    "Kak Maya",
    "Pak Guru",
]

CUSTOMER_PALETTES = [
    {"shirt": (50, 120, 210), "hair": (40, 25, 15), "skin": (245, 195, 155)},
    {"shirt": (215, 75, 65), "hair": (25, 25, 25), "skin": (225, 170, 130)},
    {"shirt": (55, 175, 95), "hair": (90, 55, 30), "skin": (255, 215, 180)},
    {"shirt": (240, 165, 35), "hair": (35, 25, 20), "skin": (210, 155, 115)},
    {"shirt": (150, 75, 190), "hair": (55, 35, 25), "skin": (250, 205, 165)},
]


class Customer:
    def __init__(
        self,
        x: int = CUSTOMER_POS[0],
        y: int = CUSTOMER_POS[1],
        scale: float = CUSTOMER_SCALE,
    ):
        self.x = x
        self.y = y
        self.scale = scale
        self.name = random.choice(CUSTOMER_NAMES)
        self.order = Order.generate_random()
        self.patience_max = DEFAULT_PATIENCE_TIME
        self.patience = DEFAULT_PATIENCE_TIME
        self.state = "waiting"  # "waiting", "happy", "angry", "done"
        self.feedback_timer = 0.0

        raw_spr = assets.get_sprite("customer")
        raw_shadow = assets.get_shadow_sprite("customer", alpha=80)

        if self.scale != 1.0 and raw_spr:
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
        dw, dh = CUSTOMER_DROPZONE_SIZE
        drop_rect = pygame.Rect(self.x - dw // 2, self.y - dh // 2, dw, dh)
        return drop_rect.collidepoint(pos)

    def serve(self, bowl_items: dict[str, int]) -> tuple[bool, int]:
        """Returns (is_correct, earned_money)"""
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
        cx, cy = self.x, self.y
        draw_x = cx - self.width // 2
        draw_y = cy - self.height // 2

        # 1. Shadow
        if self.shadow_sprite:
            surface.blit(self.shadow_sprite, (draw_x + 6, draw_y + 10))
        else:
            shadow_rect = pygame.Rect(cx - 90, cy + self.height // 2 - 20, 180, 30)
            shadow_surf = pygame.Surface((180, 30), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60), (0, 0, 180, 30))
            surface.blit(shadow_surf, shadow_rect.topleft)

        # 2. Customer Sprite (assets/game/customer.png)
        if self.sprite:
            surface.blit(self.sprite, (draw_x, draw_y))

        # 3. Name label & Patience Bar
        if self.state == "waiting":
            name_surf = assets.render_text_with_shadow(
                self.name,
                size=26,
                color=COLOR_BLACK,
                shadow_color=(255, 255, 255),
                offset=(1, 1),
            )
            surface.blit(name_surf, (cx - name_surf.get_width() // 2, draw_y - 48))

            # Patience Bar
            bar_w = 160
            bar_h = 12
            bar_x = cx - bar_w // 2
            bar_y = draw_y - 18

            patience_ratio = max(0.0, self.patience / self.patience_max)
            bar_color = (
                COLOR_PATIENCE_BAR
                if patience_ratio > 0.3
                else COLOR_PATIENCE_LOW
            )

            pygame.draw.rect(
                surface, (30, 25, 20), (bar_x - 2, bar_y - 2, bar_w + 4, bar_h + 4), border_radius=6
            )
            pygame.draw.rect(
                surface, (70, 65, 60), (bar_x, bar_y, bar_w, bar_h), border_radius=4
            )
            if patience_ratio > 0:
                pygame.draw.rect(
                    surface,
                    bar_color,
                    (bar_x, bar_y, int(bar_w * patience_ratio), bar_h),
                    border_radius=4,
                )

        # 4. Feedback Balloon
        if self.state == "happy":
            fb_surf = assets.render_text_with_shadow(
                "Enak Banget!", size=34, color=(60, 240, 80), shadow_color=(20, 60, 20), offset=(2, 2)
            )
            surface.blit(fb_surf, (cx - fb_surf.get_width() // 2, draw_y - 56))
        elif self.state == "angry":
            fb_surf = assets.render_text_with_shadow(
                "Salah / Kelamaan!", size=34, color=(255, 75, 75), shadow_color=(80, 20, 20), offset=(2, 2)
            )
            surface.blit(fb_surf, (cx - fb_surf.get_width() // 2, draw_y - 56))

