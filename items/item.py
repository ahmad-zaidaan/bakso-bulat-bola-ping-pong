from dataclasses import dataclass
import pygame
from core.assets import assets


@dataclass
class ItemDefinition:
    """
    Centralized data definition for an ingredient or game item.
    - id: Unique identifier (e.g., 'bakso_halus', 'mi_kuning')
    - display_name: Clean name shown in orders, receipts, and trays (e.g., 'B. Halus')
    - sprite_id: Name of the sprite registered in AssetManager
    - price: Selling price contribution for customer orders
    - category: Type classification ('meatball', 'noodle', 'topping', etc.)
    """

    id: str
    display_name: str
    sprite_id: str
    price: int
    category: str = "ingredient"

    @property
    def sprite(self) -> pygame.Surface | None:
        """Helper to get sprite surface directly from the asset manager."""
        return assets.get_sprite(self.sprite_id) or assets.get_sprite(self.id)

    @property
    def shadow_sprite(self) -> pygame.Surface | None:
        """Helper to get silhouette shadow directly from the asset manager."""
        return assets.get_shadow_sprite(
            self.sprite_id, alpha=60
        ) or assets.get_shadow_sprite(self.id, alpha=60)
