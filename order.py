import random

import pygame

from assets_loader import assets
from settings import (
    BASE_BOWL_PRICE,
    COLOR_TEXT_DARK,
    COLOR_TEXT_MUTED,
    COLOR_TICKET_BG,
    COLOR_TICKET_BORDER,
    ITEM_BAKSO,
    ITEM_BAKSO_URAT,
    ITEM_MI_KUNING,
    PRICE_BAKSO,
    PRICE_BAKSO_URAT,
    PRICE_MI_KUNING,
)

PRICES = {
    ITEM_BAKSO: PRICE_BAKSO,
    ITEM_BAKSO_URAT: PRICE_BAKSO_URAT,
    ITEM_MI_KUNING: PRICE_MI_KUNING,
}


class Order:
    def __init__(self, items: dict[str, int]):
        self.items = (
            items  # e.g., {ITEM_BAKSO: 2, ITEM_BAKSO_URAT: 1, ITEM_MI_KUNING: 1}
        )
        self.total_price = self.calculate_price()

    @classmethod
    def generate_random(cls) -> "Order":
        bakso_count = random.randint(1, 4)
        bakso_urat_count = random.randint(0, 3)
        mie_count = random.choice([0, 1, 1])  # most customers want 1 portion of noodles

        if bakso_count == 0 and bakso_urat_count == 0:
            bakso_count = 2

        items = {}
        if mie_count > 0:
            items[ITEM_MI_KUNING] = mie_count
        if bakso_count > 0:
            items[ITEM_BAKSO] = bakso_count
        if bakso_urat_count > 0:
            items[ITEM_BAKSO_URAT] = bakso_urat_count

        return cls(items)

    def calculate_price(self) -> int:
        price = BASE_BOWL_PRICE
        for key, count in self.items.items():
            price += count * PRICES.get(key, 0)
        return price

    def matches(self, bowl_items: dict[str, int]) -> bool:
        # Check all requested items match exactly
        for key, count in self.items.items():
            if bowl_items.get(key, 0) != count:
                return False
        # Check no unexpected items were added
        for key, count in bowl_items.items():
            if self.items.get(key, 0) != count:
                return False
        return True

    def draw_ticket(
        self, surface: pygame.Surface, x: int, y: int, width: int = 70, height: int = 56
    ):
        ticket_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, COLOR_TICKET_BG, ticket_rect)
        pygame.draw.rect(surface, COLOR_TICKET_BORDER, ticket_rect, 1)

        # Header
        hdr_surf = assets.render_text("PESANAN", color=COLOR_TEXT_DARK)
        surface.blit(hdr_surf, (x + 4, y + 2))

        # Dotted line
        pygame.draw.line(
            surface, COLOR_TICKET_BORDER, (x + 3, y + 12), (x + width - 4, y + 12), 1
        )

        # List requested items
        curr_y = y + 14
        for item_key, count in self.items.items():
            if count <= 0:
                continue
            spr = assets.get_sprite(item_key)
            if spr:
                surface.blit(spr, (x + 4, curr_y))
                txt = f"x{count}"
                txt_surf = assets.render_text(txt, color=COLOR_TEXT_DARK)
                surface.blit(txt_surf, (x + 20, curr_y))
            else:
                txt_surf = assets.render_text(
                    f"{item_key}: {count}", color=COLOR_TEXT_DARK
                )
                surface.blit(txt_surf, (x + 4, curr_y))
            curr_y += 11

        # Price tag at bottom
        price_str = f"Rp{self.total_price:,}"
        price_surf = assets.render_text(price_str, color=COLOR_TEXT_MUTED)
        surface.blit(
            price_surf, (x + width - price_surf.get_width() - 3, y + height - 11)
        )
