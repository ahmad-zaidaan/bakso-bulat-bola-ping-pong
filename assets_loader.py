import os

import pygame

from bitmap_font import bitmap_font


class AssetManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def initialize(self):
        if self.initialized:
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        sprites_dir = os.path.join(base_dir, "assets", "sprites")

        self.sprites = {}
        self.shadow_cache = {}

        # Dynamically load all .png sprites in assets/sprites
        if os.path.exists(sprites_dir):
            for filename in os.listdir(sprites_dir):
                if filename.endswith(".png"):
                    name = os.path.splitext(filename)[0]
                    file_path = os.path.join(sprites_dir, filename)
                    try:
                        self.sprites[name] = pygame.image.load(file_path).convert_alpha()
                    except Exception as e:
                        print(f"Error loading sprite {filename}: {e}")

        self.bitmap_font = bitmap_font
        self.initialized = True

    def get_sprite(self, name: str) -> pygame.Surface | None:
        return self.sprites.get(name)

    def create_shadow_surface(
        self,
        surface: pygame.Surface,
        alpha: int = 90,
        tint: tuple[int, int, int] = (0, 0, 0),
    ) -> pygame.Surface:
        """
        Creates a sprite-shaped silhouette shadow by converting the alpha mask
        into a solid black surface with transparent opacity.
        """
        mask = pygame.mask.from_surface(surface)
        shadow_color = (tint[0], tint[1], tint[2], alpha)
        return mask.to_surface(setcolor=shadow_color, unsetcolor=(0, 0, 0, 0))

    def get_shadow_sprite(
        self, name: str, alpha: int = 90, tint: tuple[int, int, int] = (0, 0, 0)
    ) -> pygame.Surface | None:
        cache_key = (name, alpha, tint)
        if cache_key in self.shadow_cache:
            return self.shadow_cache[cache_key]

        spr = self.get_sprite(name)
        if not spr:
            return None

        shadow_surf = self.create_shadow_surface(spr, alpha=alpha, tint=tint)
        self.shadow_cache[cache_key] = shadow_surf
        return shadow_surf

    def render_text(
        self,
        text: str,
        color: tuple[int, int, int] = (255, 255, 255),
        scale: int = 1,
        line_spacing: int = 2,
    ) -> pygame.Surface:
        """Render 100% crisp pixel-perfect text using Monogram bitmap font."""
        return self.bitmap_font.render(
            text, color=color, scale=scale, line_spacing=line_spacing
        )

    def render_text_with_shadow(
        self,
        text: str,
        color: tuple[int, int, int] = (255, 255, 255),
        shadow_color: tuple[int, int, int] = (0, 0, 0),
        offset: tuple[int, int] = (1, 1),
        scale: int = 1,
    ) -> pygame.Surface:
        return self.bitmap_font.render_with_shadow(
            text, color=color, shadow_color=shadow_color, offset=offset, scale=scale
        )

    def get_text_width(self, text: str, scale: int = 1) -> int:
        return self.bitmap_font.get_width(text, scale=scale)

    def get_text_height(
        self, text: str = "", scale: int = 1, line_spacing: int = 2
    ) -> int:
        return self.bitmap_font.get_height(text, scale=scale, line_spacing=line_spacing)


assets = AssetManager()
