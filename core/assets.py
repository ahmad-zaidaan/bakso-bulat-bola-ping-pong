import os
import pygame

from core.bitmap_font import bitmap_font


class AssetManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
            cls._instance.sprites: dict[str, pygame.Surface] = {}
            cls._instance.shadow_cache: dict[tuple, pygame.Surface] = {}
            cls._instance.nine_slice_cache: dict[tuple, pygame.Surface] = {}
            cls._instance.font_cache: dict[tuple, pygame.font.Font] = {}
            cls._instance.bitmap_font = bitmap_font
            cls._instance.font_regular_path = ""
            cls._instance.font_italic_path = ""
            cls._instance.sounds: dict[str, pygame.mixer.Sound] = {}
            cls._instance.master_volume: float = 1.0
        return cls._instance

    def initialize(self):
        if self.initialized:
            return

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        assets_dir = os.path.join(base_dir, "assets")

        self.sprites = {}
        self.shadow_cache = {}
        self.nine_slice_cache = {}
        self.font_cache = {}
        self.sounds = {}

        # 1. Setup font paths
        font_dir = os.path.join(assets_dir, "font")
        regular_candidate = os.path.join(font_dir, "BadComic-Regular.otf")
        italic_candidate = os.path.join(font_dir, "BadComic-Italic.otf")
        if os.path.exists(regular_candidate):
            self.font_regular_path = regular_candidate
        if os.path.exists(italic_candidate):
            self.font_italic_path = italic_candidate

        # 2. Recursively load all PNG/JPG sprites and audio in assets/
        if os.path.exists(assets_dir):
            for root, _, files in os.walk(assets_dir):
                for filename in files:
                    file_lower = filename.lower()
                    file_path = os.path.join(root, filename)

                    if file_lower.endswith((".png", ".jpg", ".jpeg")):
                        base_name = os.path.splitext(filename)[0]
                        try:
                            surf = pygame.image.load(file_path).convert_alpha()
                            # Register with exact name
                            self.sprites[base_name] = surf
                            # Register with both underscore and hyphen aliases
                            underscore_name = base_name.replace("-", "_")
                            hyphen_name = base_name.replace("_", "-")
                            self.sprites[underscore_name] = surf
                            self.sprites[hyphen_name] = surf
                        except Exception as e:
                            print(f"Error loading asset {filename}: {e}")

                    elif file_lower.endswith((".ogg", ".wav", ".mp3")):
                        base_name = os.path.splitext(filename)[0]
                        try:
                            if not pygame.mixer.get_init():
                                pygame.mixer.init()
                            snd = pygame.mixer.Sound(file_path)
                            self.sounds[base_name] = snd
                            # Register with relative path and hyphen/underscore variants
                            rel_key = os.path.relpath(file_path, assets_dir).replace("\\", "/").rsplit(".", 1)[0]
                            self.sounds[rel_key] = snd
                            self.sounds[f"sounds/{base_name}"] = snd
                        except Exception as e:
                            print(f"Error loading sound {filename}: {e}")

        self.initialized = True

    def get_sound(self, sound_id: str) -> pygame.mixer.Sound | None:
        """Retrieve loaded Sound by name or path."""
        if not self.initialized:
            self.initialize()
        if sound_id in self.sounds:
            return self.sounds[sound_id]
        base_name = os.path.basename(sound_id).rsplit(".", 1)[0]
        return self.sounds.get(base_name) or self.sounds.get(f"sounds/{base_name}")

    def set_master_volume(self, volume: float):
        """Set master volume between 0.0 and 1.0."""
        self.master_volume = max(0.0, min(1.0, float(volume)))

    def get_master_volume(self) -> float:
        """Get current master volume."""
        return getattr(self, "master_volume", 1.0)

    def play_sound(self, sound_id: str, volume: float = 1.0):
        """Plays sound effect with safety checks and master volume scaling."""
        try:
            snd = self.get_sound(sound_id)
            if snd:
                master = getattr(self, "master_volume", 1.0)
                snd.set_volume(max(0.0, min(1.0, volume * master)))
                snd.play()
        except Exception:
            pass

    def get_sprite(self, name_id: str) -> pygame.Surface | None:
        """Retrieve loaded sprite surface by its unique name/id (supports hyphen/underscore)."""
        if not self.initialized:
            self.initialize()
        return self.sprites.get(name_id) or self.sprites.get(
            name_id.replace("_", "-")
        ) or self.sprites.get(name_id.replace("-", "_"))

    def get_font(
        self, size: int = 24, font_type: str = "regular"
    ) -> pygame.font.Font:
        """Get cached BadComic TTF/OTF font."""
        if not pygame.font.get_init():
            pygame.font.init()

        cache_key = (font_type, size)
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]

        font_path = (
            self.font_italic_path
            if font_type == "italic" and self.font_italic_path
            else self.font_regular_path
        )

        try:
            if font_path and os.path.exists(font_path):
                f = pygame.font.Font(font_path, size)
            else:
                f = pygame.font.SysFont("Comic Sans MS, Arial, sans-serif", size)
        except Exception:
            f = pygame.font.Font(None, size)

        self.font_cache[cache_key] = f
        return f

    def render_text(
        self,
        text: str,
        size: int = 24,
        color: tuple[int, int, int] = (50, 35, 20),
        font_type: str = "regular",
        scale: int = 1,
        line_spacing: int = 2,
    ) -> pygame.Surface:
        """Renders anti-aliased cartoon text."""
        font = self.get_font(size * scale, font_type=font_type)
        return font.render(str(text), True, color)

    def render_text_with_shadow(
        self,
        text: str,
        size: int = 24,
        color: tuple[int, int, int] = (255, 255, 255),
        shadow_color: tuple[int, int, int] = (30, 20, 10),
        offset: tuple[int, int] = (2, 2),
        font_type: str = "regular",
        scale: int = 1,
    ) -> pygame.Surface:
        """Renders cartoon text with drop shadow."""
        font = self.get_font(size * scale, font_type=font_type)
        main_surf = font.render(str(text), True, color)
        shadow_surf = font.render(str(text), True, shadow_color)

        ox, oy = offset
        w = main_surf.get_width() + abs(ox)
        h = main_surf.get_height() + abs(oy)

        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.blit(shadow_surf, (max(0, ox), max(0, oy)))
        surf.blit(main_surf, (0 if ox >= 0 else -ox, 0 if oy >= 0 else -oy))
        return surf

    def get_text_width(
        self, text: str, size: int = 24, font_type: str = "regular", scale: int = 1
    ) -> int:
        font = self.get_font(size * scale, font_type=font_type)
        return font.size(str(text))[0]

    def get_text_height(
        self, text: str = "", size: int = 24, font_type: str = "regular", scale: int = 1, line_spacing: int = 2
    ) -> int:
        font = self.get_font(size * scale, font_type=font_type)
        return font.size(str(text) if text else "A")[1]

    def create_shadow_surface(
        self,
        surface: pygame.Surface,
        alpha: int = 90,
        tint: tuple[int, int, int] = (0, 0, 0),
    ) -> pygame.Surface:
        """Generates a sprite-shaped silhouette shadow via alpha masking."""
        mask = pygame.mask.from_surface(surface)
        shadow_color = (tint[0], tint[1], tint[2], alpha)
        return mask.to_surface(setcolor=shadow_color, unsetcolor=(0, 0, 0, 0))

    def get_shadow_sprite(
        self, name_id: str, alpha: int = 90, tint: tuple[int, int, int] = (0, 0, 0)
    ) -> pygame.Surface | None:
        """Returns cached sprite-shaped silhouette shadow."""
        cache_key = (name_id, alpha, tint)
        if cache_key in self.shadow_cache:
            return self.shadow_cache[cache_key]

        spr = self.get_sprite(name_id)
        if not spr:
            return None

        shadow_surf = self.create_shadow_surface(spr, alpha=alpha, tint=tint)
        self.shadow_cache[cache_key] = shadow_surf
        return shadow_surf

    def get_9slice_surface(
        self,
        image_id: str = "button",
        target_width: int = 200,
        target_height: int = 60,
        slice_margin: int = 32,
    ) -> pygame.Surface:
        """Generates a crisp 9-slice scaled surface (e.g. from button.png)."""
        cache_key = (image_id, target_width, target_height, slice_margin)
        if cache_key in self.nine_slice_cache:
            return self.nine_slice_cache[cache_key]

        src = self.get_sprite(image_id)
        if not src:
            fallback = pygame.Surface((target_width, target_height), pygame.SRCALPHA)
            fallback.fill((235, 150, 50))
            return fallback

        tw, th = max(1, target_width), max(1, target_height)
        sw, sh = src.get_size()
        m = max(1, min(slice_margin, tw // 2, th // 2, sw // 2, sh // 2))

        surf = pygame.Surface((tw, th), pygame.SRCALPHA)

        # Corners
        tl = src.subsurface((0, 0, m, m))
        tr = src.subsurface((sw - m, 0, m, m))
        bl = src.subsurface((0, sh - m, m, m))
        br = src.subsurface((sw - m, sh - m, m, m))

        # Center & Edges
        if tw > 2 * m and th > 2 * m:
            center = pygame.transform.scale(
                src.subsurface((m, m, sw - 2 * m, sh - 2 * m)),
                (tw - 2 * m, th - 2 * m),
            )
            surf.blit(center, (m, m))

        if tw > 2 * m:
            top = pygame.transform.scale(
                src.subsurface((m, 0, sw - 2 * m, m)), (tw - 2 * m, m)
            )
            bottom = pygame.transform.scale(
                src.subsurface((m, sh - m, sw - 2 * m, m)), (tw - 2 * m, m)
            )
            surf.blit(top, (m, 0))
            surf.blit(bottom, (m, th - m))

        if th > 2 * m:
            left = pygame.transform.scale(
                src.subsurface((0, m, m, sh - 2 * m)), (m, th - 2 * m)
            )
            right = pygame.transform.scale(
                src.subsurface((sw - m, m, m, sh - 2 * m)), (m, th - 2 * m)
            )
            surf.blit(left, (0, m))
            surf.blit(right, (tw - m, m))

        surf.blit(tl, (0, 0))
        surf.blit(tr, (tw - m, 0))
        surf.blit(bl, (0, th - m))
        surf.blit(br, (tw - m, th - m))

        self.nine_slice_cache[cache_key] = surf
        return surf

    def create_outline_surface(
        self,
        surface: pygame.Surface,
        outline_color: tuple[int, int, int] = (255, 225, 75),
        thickness: int = 3,
    ) -> pygame.Surface:
        """Generates a crisp outer contour outline around a sprite surface."""
        w, h = surface.get_size()
        mask = pygame.mask.from_surface(surface)
        pad = thickness
        out_surf = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
        mask_surf = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))

        # Blit mask outline in a radius ring
        for dx in range(-thickness, thickness + 1):
            for dy in range(-thickness, thickness + 1):
                if dx * dx + dy * dy <= thickness * thickness and (dx != 0 or dy != 0):
                    out_surf.blit(mask_surf, (pad + dx, pad + dy))

        out_surf.blit(surface, (pad, pad))
        return out_surf

    def get_outlined_sprite(
        self,
        name_id: str,
        outline_color: tuple[int, int, int] = (255, 225, 75),
        thickness: int = 3,
        scale: float = 1.0,
    ) -> tuple[pygame.Surface | None, int]:
        """Returns cached outlined sprite surface and the padding offset."""
        cache_key = (name_id, outline_color, thickness, scale)
        if hasattr(self, "outline_cache") and cache_key in self.outline_cache:
            return self.outline_cache[cache_key]

        if not hasattr(self, "outline_cache"):
            self.outline_cache: dict[tuple, tuple[pygame.Surface, int]] = {}

        spr = self.get_sprite(name_id)
        if not spr:
            return None, 0

        if scale != 1.0:
            sw, sh = int(spr.get_width() * scale), int(spr.get_height() * scale)
            spr = pygame.transform.smoothscale(spr, (sw, sh))

        out_surf = self.create_outline_surface(spr, outline_color=outline_color, thickness=thickness)
        result = (out_surf, thickness)
        self.outline_cache[cache_key] = result
        return result


# Global singleton instance
assets = AssetManager()


