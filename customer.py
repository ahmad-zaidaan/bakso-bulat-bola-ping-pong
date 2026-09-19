import random

import pygame

from assets_loader import assets
from order import Order
from settings import (
    COLOR_BLACK,
    COLOR_PATIENCE_BAR,
    COLOR_PATIENCE_LOW,
    COLOR_TEXT_DARK,
    DEFAULT_PATIENCE_TIME,
)

CUSTOMER_NAMES = [
    "Mas Budi",
    "Pak Haji",
    "Mbak Siti",
    "Bang Ojol",
    "Bocil SD",
    "Bu RT",
    "Kak Maya",
]

CUSTOMER_PALETTES = [
    {"shirt": (50, 120, 200), "hair": (40, 25, 15), "skin": (240, 190, 150)},
    {"shirt": (200, 70, 60), "hair": (20, 20, 20), "skin": (215, 160, 120)},
    {"shirt": (50, 160, 90), "hair": (80, 50, 30), "skin": (250, 205, 170)},
    {"shirt": (230, 160, 30), "hair": (30, 20, 20), "skin": (200, 145, 105)},
    {"shirt": (140, 70, 180), "hair": (50, 30, 20), "skin": (245, 195, 155)},
]


class Customer:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.name = random.choice(CUSTOMER_NAMES)
        self.palette = random.choice(CUSTOMER_PALETTES)
        self.order = Order.generate_random()
        self.patience_max = DEFAULT_PATIENCE_TIME
        self.patience = DEFAULT_PATIENCE_TIME
        self.state = "waiting"  # "waiting", "happy", "angry", "done"
        self.feedback_timer = 0.0

    def update(self, dt: float):
        if self.state == "waiting":
            self.patience -= dt
            if self.patience <= 0:
                self.patience = 0
                self.state = "angry"
                self.feedback_timer = 2.0  # display angry feedback for 2s
        elif self.state in ["happy", "angry"]:
            self.feedback_timer -= dt
            if self.feedback_timer <= 0:
                self.state = "done"

    def contains_point(self, pos: tuple[int, int]) -> bool:
        # Serving dropzone covers customer and the counter counter window
        drop_rect = pygame.Rect(self.x - 30, 16, 60, 68)
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
        # Draw retro pixel character behind counter
        cx, cy = self.x, self.y
        skin = self.palette["skin"]
        hair = self.palette["hair"]
        shirt = self.palette["shirt"]

        # Body/Shirt (angled shoulders)
        pygame.draw.rect(surface, shirt, (cx - 10, cy + 14, 20, 22))
        pygame.draw.rect(
            surface,
            (max(0, shirt[0] - 30), max(0, shirt[1] - 30), max(0, shirt[2] - 30)),
            (cx - 10, cy + 14, 20, 22),
            1,
        )

        # Head / Face
        pygame.draw.rect(surface, skin, (cx - 7, cy + 3, 14, 13))

        # Hair
        pygame.draw.rect(surface, hair, (cx - 8, cy, 16, 5))
        pygame.draw.rect(surface, hair, (cx - 8, cy + 3, 3, 4))
        pygame.draw.rect(surface, hair, (cx + 5, cy + 3, 3, 4))

        # Eyes & Mouth based on state
        if self.state == "happy":
            # Smiling ^ ^ eyes
            pygame.draw.line(
                surface, COLOR_BLACK, (cx - 5, cy + 7), (cx - 3, cy + 7), 1
            )
            pygame.draw.line(
                surface, COLOR_BLACK, (cx + 3, cy + 7), (cx + 5, cy + 7), 1
            )
            # Smile
            pygame.draw.line(
                surface, (180, 50, 50), (cx - 3, cy + 11), (cx + 3, cy + 11), 1
            )
        elif self.state == "angry":
            # Angry > < eyes
            pygame.draw.line(
                surface, COLOR_BLACK, (cx - 5, cy + 6), (cx - 3, cy + 8), 1
            )
            pygame.draw.line(
                surface, COLOR_BLACK, (cx + 3, cy + 8), (cx + 5, cy + 6), 1
            )
            # Frown
            pygame.draw.line(
                surface, (180, 50, 50), (cx - 3, cy + 12), (cx + 3, cy + 12), 1
            )
        else:
            # Normal eyes
            pygame.draw.rect(surface, COLOR_BLACK, (cx - 5, cy + 7, 2, 2))
            pygame.draw.rect(surface, COLOR_BLACK, (cx + 3, cy + 7, 2, 2))
            # Mouth
            pygame.draw.rect(surface, (160, 60, 60), (cx - 1, cy + 11, 2, 1))

        # Name label
        name_surf = assets.render_text(self.name, color=COLOR_TEXT_DARK)
        surface.blit(name_surf, (cx - name_surf.get_width() // 2, cy - 14))

        # Patience Bar (if waiting)
        if self.state == "waiting":
            bar_w = 26
            bar_h = 3
            bar_x = cx - bar_w // 2
            bar_y = cy - 4

            patience_ratio = max(0.0, self.patience / self.patience_max)
            bar_color = (
                COLOR_PATIENCE_BAR if patience_ratio > 0.3 else COLOR_PATIENCE_LOW
            )

            pygame.draw.rect(
                surface, (50, 50, 50), (bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2)
            )
            pygame.draw.rect(surface, (100, 100, 100), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(
                surface, bar_color, (bar_x, bar_y, int(bar_w * patience_ratio), bar_h)
            )

        # Feedback text with shadow
        if self.state == "happy":
            fb_surf = assets.render_text_with_shadow(
                "Enak!", color=(60, 220, 70), shadow_color=(20, 60, 20)
            )
            surface.blit(fb_surf, (cx - fb_surf.get_width() // 2, cy - 23))
        elif self.state == "angry":
            fb_surf = assets.render_text_with_shadow(
                "Salah/Lama!", color=(255, 80, 80), shadow_color=(80, 20, 20)
            )
            surface.blit(fb_surf, (cx - fb_surf.get_width() // 2, cy - 23))
