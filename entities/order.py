import random
import pygame

from config import BASE_BOWL_PRICE
from core.assets import assets
from items.registry import items_registry

ORDER_TICKET_POS = (40, 140)
ORDER_TICKET_SIZE = (280, 260)
COLOR_TICKET_BG = (255, 248, 230)
COLOR_TICKET_BORDER = (180, 150, 110)
COLOR_TEXT_DARK = (70, 40, 40)


class Order:
    def __init__(self, items: dict[str, int]):
        self.items = items
        self.total_price = self.calculate_price()

    @classmethod
    def generate_random(cls) -> "Order":
        items = {}

        # 1. Noodles: None, Mie Kuning, Bihun, or Mixed (Campur)
        noodle_choice = random.choice([
            "none",
            "mi_kuning",
            "mi_kuning",
            "mi_bihun",
            "mi_bihun",
            "both",
            "mi_kuning_2",
            "mi_bihun_2",
        ])
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

        # 2. Main Meatball: Bakso Halus (1 to 4)
        items["bakso_halus"] = random.choice([1, 2, 2, 3, 3, 4])

        # 3. Tahu (50% chance: 1 or 2)
        if random.random() < 0.50:
            items["tahu"] = random.choice([1, 1, 2])

        # 4. Gorengan (50% chance: 1 or 2)
        if random.random() < 0.50:
            items["gorengan_panjang"] = random.choice([1, 1, 2])

        # 5. Garnish Sprinkles (Daun Bawang & Bawang Goreng)
        if random.random() < 0.65:
            items["daun_bawang"] = 1
        if random.random() < 0.65:
            items["bawang_goreng"] = 1

        # 6. Sauces / Condiments (Kecap, Saos Sambal, Saos Tomat)
        if random.random() < 0.45:
            items["kecap"] = 1
        if random.random() < 0.45:
            items["saos_sambal"] = 1
        if random.random() < 0.35:
            items["saos_tomat"] = 1

        return cls(items)

    def calculate_price(self) -> int:
        price = BASE_BOWL_PRICE
        for item_id, count in self.items.items():
            price += count * items_registry.get_price(item_id)
        return price

    def matches(self, bowl_items: dict[str, int]) -> bool:
        # Normalize keys via ItemRegistry to handle aliases cleanly
        normalized_bowl: dict[str, int] = {}
        for raw_id, count in bowl_items.items():
            item_def = items_registry.get(raw_id)
            canonical_id = item_def.id if item_def else raw_id
            normalized_bowl[canonical_id] = (
                normalized_bowl.get(canonical_id, 0) + count
            )

        # Check all requested items match exactly
        for key, count in self.items.items():
            item_def = items_registry.get(key)
            canonical_id = item_def.id if item_def else key
            if normalized_bowl.get(canonical_id, 0) != count:
                return False

        # Check no unexpected items exist
        for key, count in normalized_bowl.items():
            item_def = items_registry.get(key)
            canonical_id = item_def.id if item_def else key
            if self.items.get(canonical_id, 0) != count:
                return False

        return True

    def draw_ticket(
        self,
        surface: pygame.Surface,
        x: int = ORDER_TICKET_POS[0],
        y: int = ORDER_TICKET_POS[1],
        width: int = ORDER_TICKET_SIZE[0],
        height: int = ORDER_TICKET_SIZE[1],
    ):
        active_items = [(k, v) for k, v in self.items.items() if v > 0]
        # Dynamic height so all requested ingredients fit comfortably
        needed_height = max(height, 56 + len(active_items) * 32 + 48)
        ticket_rect = pygame.Rect(x, y, width, needed_height)

        # Drop shadow for ticket
        shadow_rect = ticket_rect.copy()
        shadow_rect.move_ip(4, 6)
        pygame.draw.rect(surface, (0, 0, 0, 60), shadow_rect, border_radius=10)

        pygame.draw.rect(surface, COLOR_TICKET_BG, ticket_rect, border_radius=10)
        pygame.draw.rect(surface, COLOR_TICKET_BORDER, ticket_rect, 3, border_radius=10)

        # Header
        hdr_surf = assets.render_text("ORDER", size=28, color=COLOR_TEXT_DARK)
        surface.blit(hdr_surf, (x + 14, y + 10))

        # Divider line
        pygame.draw.line(
            surface,
            COLOR_TICKET_BORDER,
            (x + 12, y + 44),
            (x + width - 12, y + 44),
            2,
        )

        # List items
        curr_y = y + 52
        for item_id, count in active_items:
            item_def = items_registry.get(item_id)
            spr = (
                item_def.sprite
                if item_def
                else assets.get_sprite(item_id)
            )

            if spr:
                sw, sh = spr.get_size()
                # Scale sprite down to thumbnail size
                thumb_max = 28
                ratio = min(1.0, thumb_max / max(1, sw), thumb_max / max(1, sh))
                tw, th = int(sw * ratio), int(sh * ratio)
                thumb = pygame.transform.smoothscale(spr, (tw, th))
                surface.blit(thumb, (x + 14, curr_y))

                name_txt = item_def.display_name if item_def else item_id
                txt = f"{name_txt} x{count}"
                txt_surf = assets.render_text(txt, size=24, color=COLOR_TEXT_DARK)
                surface.blit(
                    txt_surf,
                    (
                        x + 14 + thumb_max + 8,
                        curr_y + max(0, (th - txt_surf.get_height()) // 2),
                    ),
                )
                curr_y += max(th, 22) + 6
            else:
                display_name = item_def.display_name if item_def else item_id
                txt_surf = assets.render_text(
                    f"{display_name}: {count}", size=22, color=COLOR_TEXT_DARK
                )
                surface.blit(txt_surf, (x + 14, curr_y))
                curr_y += 28

        # Total price tag
        price_str = f"Rp {self.total_price:,}"
        price_surf = assets.render_text(price_str, size=26, color=(160, 90, 30))
        surface.blit(
            price_surf,
            (x + width - price_surf.get_width() - 14, y + needed_height - 38),
        )
