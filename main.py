import json
import math
import os
import sys
import pygame

# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================
TITLE = "So Bakso"
INTERNAL_WIDTH = 1920
INTERNAL_HEIGHT = 1080
DEFAULT_WINDOW_WIDTH = 1280
DEFAULT_WINDOW_HEIGHT = 720
FPS = 60
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GOLD = (255, 205, 45)


# ==============================================================================
# ASSET MANAGER (Images, Sounds, Fonts, 9-Slice UI)
# ==============================================================================
class AssetManager:
    def __init__(self):
        self.sprites: dict[str, pygame.Surface] = {}
        self.shadow_cache: dict[tuple, pygame.Surface] = {}
        self.nine_slice_cache: dict[tuple, pygame.Surface] = {}
        self.font_cache: dict[tuple, pygame.font.Font] = {}
        self.outline_cache: dict[tuple, tuple[pygame.Surface, int]] = {}
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.master_volume: float = 1.0
        self.font_regular_path = ""
        self.font_italic_path = ""
        self.initialized = False

    def initialize(self):
        if self.initialized:
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(base_dir, "assets")

        # 1. Fonts
        font_dir = os.path.join(assets_dir, "font")
        reg_font = os.path.join(font_dir, "BadComic-Regular.otf")
        ita_font = os.path.join(font_dir, "BadComic-Italic.otf")
        if os.path.exists(reg_font):
            self.font_regular_path = reg_font
        if os.path.exists(ita_font):
            self.font_italic_path = ita_font

        # 2. Images & Audio
        if os.path.exists(assets_dir):
            for root, _, files in os.walk(assets_dir):
                for filename in files:
                    file_lower = filename.lower()
                    file_path = os.path.join(root, filename)

                    if file_lower.endswith((".png", ".jpg", ".jpeg")):
                        base_name = os.path.splitext(filename)[0]
                        try:
                            surf = pygame.image.load(file_path).convert_alpha()
                            self.sprites[base_name] = surf
                            self.sprites[base_name.replace("-", "_")] = surf
                            self.sprites[base_name.replace("_", "-")] = surf
                        except Exception as e:
                            print(f"Error loading image {filename}: {e}")

                    elif file_lower.endswith((".ogg", ".wav", ".mp3")):
                        base_name = os.path.splitext(filename)[0]
                        try:
                            if not pygame.mixer.get_init():
                                pygame.mixer.init()
                            snd = pygame.mixer.Sound(file_path)
                            self.sounds[base_name] = snd
                            rel_key = os.path.relpath(file_path, assets_dir).replace("\\", "/").rsplit(".", 1)[0]
                            self.sounds[rel_key] = snd
                            self.sounds[f"sounds/{base_name}"] = snd
                        except Exception as e:
                            print(f"Error loading sound {filename}: {e}")

        self.initialized = True

    def get_sprite(self, name_id: str) -> pygame.Surface | None:
        if not self.initialized:
            self.initialize()
        return self.sprites.get(name_id) or self.sprites.get(name_id.replace("_", "-")) or self.sprites.get(name_id.replace("-", "_"))

    def get_sound(self, sound_id: str) -> pygame.mixer.Sound | None:
        if not self.initialized:
            self.initialize()
        if sound_id in self.sounds:
            return self.sounds[sound_id]
        base = os.path.basename(sound_id).rsplit(".", 1)[0]
        return self.sounds.get(base) or self.sounds.get(f"sounds/{base}")

    def set_master_volume(self, volume: float):
        self.master_volume = max(0.0, min(1.0, float(volume)))

    def get_master_volume(self) -> float:
        return self.master_volume

    def play_sound(self, sound_id: str, volume: float = 1.0):
        try:
            snd = self.get_sound(sound_id)
            if snd:
                snd.set_volume(max(0.0, min(1.0, volume * self.master_volume)))
                snd.play()
        except Exception:
            pass

    def get_font(self, size: int = 24, font_type: str = "regular") -> pygame.font.Font:
        if not pygame.font.get_init():
            pygame.font.init()

        cache_key = (font_type, size)
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]

        font_path = self.font_italic_path if font_type == "italic" and self.font_italic_path else self.font_regular_path
        try:
            if font_path and os.path.exists(font_path):
                f = pygame.font.Font(font_path, size)
            else:
                f = pygame.font.SysFont("Comic Sans MS, Arial, sans-serif", size)
        except Exception:
            f = pygame.font.Font(None, size)

        self.font_cache[cache_key] = f
        return f

    def render_text(self, text: str, size: int = 24, color: tuple[int, int, int] = (50, 35, 20), font_type: str = "regular") -> pygame.Surface:
        font = self.get_font(size, font_type=font_type)
        return font.render(str(text), True, color)

    def render_text_with_shadow(self, text: str, size: int = 24, color: tuple[int, int, int] = (255, 255, 255), shadow_color: tuple[int, int, int] = (30, 20, 10), offset: tuple[int, int] = (2, 2), font_type: str = "regular") -> pygame.Surface:
        font = self.get_font(size, font_type=font_type)
        main_surf = font.render(str(text), True, color)
        shadow_surf = font.render(str(text), True, shadow_color)
        ox, oy = offset
        w = main_surf.get_width() + abs(ox)
        h = main_surf.get_height() + abs(oy)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.blit(shadow_surf, (max(0, ox), max(0, oy)))
        surf.blit(main_surf, (0 if ox >= 0 else -ox, 0 if oy >= 0 else -oy))
        return surf

    def get_shadow_sprite(self, name_id: str, alpha: int = 90) -> pygame.Surface | None:
        cache_key = (name_id, alpha)
        if cache_key in self.shadow_cache:
            return self.shadow_cache[cache_key]

        spr = self.get_sprite(name_id)
        if not spr:
            return None

        mask = pygame.mask.from_surface(spr)
        shadow_surf = mask.to_surface(setcolor=(0, 0, 0, alpha), unsetcolor=(0, 0, 0, 0))
        self.shadow_cache[cache_key] = shadow_surf
        return shadow_surf

    def get_9slice_surface(self, image_id: str = "button", target_width: int = 200, target_height: int = 60, slice_margin: int = 32) -> pygame.Surface:
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
        tl = src.subsurface((0, 0, m, m))
        tr = src.subsurface((sw - m, 0, m, m))
        bl = src.subsurface((0, sh - m, m, m))
        br = src.subsurface((sw - m, sh - m, m, m))

        if tw > 2 * m and th > 2 * m:
            center = pygame.transform.scale(src.subsurface((m, m, sw - 2 * m, sh - 2 * m)), (tw - 2 * m, th - 2 * m))
            surf.blit(center, (m, m))

        if tw > 2 * m:
            top = pygame.transform.scale(src.subsurface((m, 0, sw - 2 * m, m)), (tw - 2 * m, m))
            bottom = pygame.transform.scale(src.subsurface((m, sh - m, sw - 2 * m, m)), (tw - 2 * m, m))
            surf.blit(top, (m, 0))
            surf.blit(bottom, (m, th - m))

        if th > 2 * m:
            left = pygame.transform.scale(src.subsurface((0, m, m, sh - 2 * m)), (m, th - 2 * m))
            right = pygame.transform.scale(src.subsurface((sw - m, m, m, sh - 2 * m)), (m, th - 2 * m))
            surf.blit(left, (0, m))
            surf.blit(right, (tw - m, m))

        surf.blit(tl, (0, 0))
        surf.blit(tr, (tw - m, 0))
        surf.blit(bl, (0, th - m))
        surf.blit(br, (tw - m, th - m))

        self.nine_slice_cache[cache_key] = surf
        return surf

    def get_outlined_sprite(self, name_id: str, outline_color: tuple[int, int, int] = (255, 255, 255), thickness: int = 3, scale: float = 1.0) -> tuple[pygame.Surface | None, int]:
        cache_key = (name_id, outline_color, thickness, scale)
        if cache_key in self.outline_cache:
            return self.outline_cache[cache_key]

        spr = self.get_sprite(name_id)
        if not spr:
            return None, 0

        if scale != 1.0:
            sw, sh = int(spr.get_width() * scale), int(spr.get_height() * scale)
            spr = pygame.transform.smoothscale(spr, (sw, sh))

        w, h = spr.get_size()
        mask = pygame.mask.from_surface(spr)
        pad = thickness
        out_surf = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
        mask_surf = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))

        for dx in range(-thickness, thickness + 1):
            for dy in range(-thickness, thickness + 1):
                if dx * dx + dy * dy <= thickness * thickness and (dx != 0 or dy != 0):
                    out_surf.blit(mask_surf, (pad + dx, pad + dy))

        out_surf.blit(spr, (pad, pad))
        result = (out_surf, thickness)
        self.outline_cache[cache_key] = result
        return result


assets = AssetManager()


# ==============================================================================
# SAVE MANAGER
# ==============================================================================
class SaveManager:
    def __init__(self, filename: str = "save_data.json"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.filepath = os.path.join(base_dir, filename)

    def has_save(self) -> bool:
        return os.path.exists(self.filepath)

    def load_game(self) -> dict | None:
        if not self.has_save():
            return None
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading save file: {e}")
            return None

    def save_game(self, data: dict) -> bool:
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    def delete_save(self):
        if self.has_save():
            try:
                os.remove(self.filepath)
            except Exception as e:
                print(f"Error deleting save file: {e}")


save_manager = SaveManager()


# ==============================================================================
# SCENE SYSTEM
# ==============================================================================
class BaseScene:
    def __init__(self):
        self.manager = None
        self.is_overlay = False

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def handle_event(self, event: pygame.event.Event, mouse_canvas_pos: tuple[int, int]):
        pass

    def update(self, dt: float):
        pass

    def draw(self, canvas: pygame.Surface):
        pass


class SceneManager:
    def __init__(self, app):
        self.app = app
        self.scene_stack: list[BaseScene] = []

    @property
    def current_scene(self) -> BaseScene | None:
        return self.scene_stack[-1] if self.scene_stack else None

    def push_scene(self, scene: BaseScene):
        scene.manager = self
        self.scene_stack.append(scene)
        scene.on_enter()

    def pop_scene(self) -> BaseScene | None:
        if not self.scene_stack:
            return None
        popped = self.scene_stack.pop()
        popped.on_exit()
        if self.scene_stack:
            self.scene_stack[-1].on_enter()
        return popped

    def change_scene(self, scene: BaseScene):
        while self.scene_stack:
            self.pop_scene()
        self.push_scene(scene)

    def handle_event(self, event: pygame.event.Event, mouse_canvas_pos: tuple[int, int]):
        if self.current_scene:
            self.current_scene.handle_event(event, mouse_canvas_pos)

    def update(self, dt: float):
        if self.current_scene:
            self.current_scene.update(dt)

    def draw(self, canvas: pygame.Surface):
        if not self.scene_stack:
            return

        start_idx = len(self.scene_stack) - 1
        while start_idx > 0 and self.scene_stack[start_idx].is_overlay:
            start_idx -= 1

        for i in range(start_idx, len(self.scene_stack)):
            self.scene_stack[i].draw(canvas)


# ==============================================================================
# MAIN APPLICATION
# ==============================================================================
class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)

        try:
            icon_image = pygame.image.load("assets/sprites/game/mangkok.png")
            pygame.display.set_icon(icon_image)
        except Exception:
            pass

        self.is_fullscreen = False
        self.show_hitboxes = False

        self.window = pygame.display.set_mode(
            (DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT), pygame.RESIZABLE
        )
        self.canvas = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
        self.clock = pygame.time.Clock()

        # Load all assets
        assets.initialize()

        self.scene_manager = SceneManager(self)
        from ui import TitleScene
        self.scene_manager.push_scene(TitleScene())

        self.global_key_actions = {
            pygame.K_F11: self.toggle_fullscreen,
            pygame.K_F3: self.toggle_hitboxes,
        }

    def toggle_hitboxes(self):
        self.show_hitboxes = not self.show_hitboxes

    def set_window_size(self, width: int, height: int):
        self.is_fullscreen = False
        self.window = pygame.display.set_mode((width, height), pygame.RESIZABLE)

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.window = pygame.display.set_mode(
                (DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT), pygame.RESIZABLE
            )

    def window_to_canvas_pos(self, window_pos: tuple[int, int]) -> tuple[int, int]:
        win_w, win_h = self.window.get_size()
        scale = min(win_w / INTERNAL_WIDTH, win_h / INTERNAL_HEIGHT)
        if scale <= 0:
            return 0, 0

        render_w = int(INTERNAL_WIDTH * scale)
        render_h = int(INTERNAL_HEIGHT * scale)
        offset_x = (win_w - render_w) // 2
        offset_y = (win_h - render_h) // 2

        wx, wy = window_pos
        cx = int((wx - offset_x) / scale)
        cy = int((wy - offset_y) / scale)
        return cx, cy

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN and event.key in self.global_key_actions:
                    self.global_key_actions[event.key]()

                mouse_canvas_pos = self.window_to_canvas_pos(pygame.mouse.get_pos())
                self.scene_manager.handle_event(event, mouse_canvas_pos)

            self.scene_manager.update(dt)
            self.scene_manager.draw(self.canvas)
            self.render_upscaled()
            pygame.display.flip()

    def render_upscaled(self):
        win_w, win_h = self.window.get_size()
        scale = min(win_w / INTERNAL_WIDTH, win_h / INTERNAL_HEIGHT)
        render_w = int(INTERNAL_WIDTH * scale)
        render_h = int(INTERNAL_HEIGHT * scale)
        offset_x = (win_w - render_w) // 2
        offset_y = (win_h - render_h) // 2

        scaled_surf = pygame.transform.smoothscale(self.canvas, (render_w, render_h))
        self.window.fill(COLOR_BLACK)
        self.window.blit(scaled_surf, (offset_x, offset_y))


if __name__ == "__main__":
    app = App()
    app.run()
