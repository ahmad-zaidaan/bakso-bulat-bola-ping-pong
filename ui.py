import math
import sys
import pygame
from main import (
    INTERNAL_HEIGHT,
    INTERNAL_WIDTH,
    BaseScene,
    assets,
    save_manager,
)

COLOR_BG_CYAN = (75, 205, 240)
COLOR_GOLD = (255, 205, 45)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)


# ==============================================================================
# UI COMPONENTS (Button, Slider, Label)
# ==============================================================================
class Button:
    def __init__(
        self,
        text: str,
        x: int = 0,
        y: int = 0,
        width: int = 240,
        height: int = 60,
        font_size: int = 26,
        on_click=None,
        use_texture: bool = True,
        texture_id: str = "button",
        bg_color: tuple[int, int, int] = (235, 150, 50),
        text_color: tuple[int, int, int] = (0, 0, 0),
        is_active: bool = False,
    ):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.font_size = font_size
        self.on_click = on_click
        self.use_texture = use_texture
        self.texture_id = texture_id
        self.bg_color = bg_color
        self.text_color = text_color
        self.is_active = is_active
        self.is_hovered = False

    def handle_event(self, event: pygame.event.Event, mouse_pos: tuple[int, int]) -> bool:
        hovered = self.rect.collidepoint(mouse_pos)
        if hovered and not self.is_hovered:
            assets.play_sound("click1.ogg", volume=0.3)
        self.is_hovered = hovered

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                assets.play_sound("click2.ogg", volume=1.0)
                if self.on_click:
                    self.on_click()
                return True
        return False

    def draw(self, surface: pygame.Surface, mouse_pos: tuple[int, int] = (0, 0)):
        hovered = self.rect.collidepoint(mouse_pos)
        if hovered and not self.is_hovered:
            assets.play_sound("click1.ogg", volume=0.3)
        self.is_hovered = hovered

        if self.use_texture and assets.get_sprite(self.texture_id):
            btn_surf = assets.get_9slice_surface(
                self.texture_id, self.rect.width, self.rect.height, slice_margin=24
            )
            surface.blit(btn_surf, self.rect.topleft)
        else:
            pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=12)

        # Outlines
        if self.is_active:
            pygame.draw.rect(surface, (75, 225, 105), self.rect.inflate(6, 6), width=4, border_radius=16)
        elif self.is_hovered:
            pygame.draw.rect(surface, (255, 255, 255), self.rect.inflate(6, 6), width=4, border_radius=16)

        # Text
        txt_surf = assets.render_text(self.text, size=self.font_size, color=self.text_color)
        tx = self.rect.centerx - txt_surf.get_width() // 2
        ty = self.rect.centery - txt_surf.get_height() // 2
        surface.blit(txt_surf, (tx, ty))


class Slider:
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 280,
        height: int = 36,
        min_val: float = 0.0,
        max_val: float = 1.0,
        value: float = 1.0,
        step: float = 0.05,
        on_change=None,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = value
        self.step = step
        self.on_change = on_change
        self.is_dragging = False
        self.is_hovered = False

    def set_value(self, val: float):
        clamped = max(self.min_val, min(self.max_val, float(val)))
        if self.step:
            clamped = round(round(clamped / self.step) * self.step, 4)
            clamped = max(self.min_val, min(self.max_val, clamped))
        if clamped != self.value:
            self.value = clamped
            if self.on_change:
                self.on_change(self.value)

    def _update_from_mouse_x(self, mouse_x: int):
        track_left = self.rect.x + 14
        track_right = self.rect.right - 14
        track_w = max(1, track_right - track_left)
        rel_x = max(0, min(track_w, mouse_x - track_left))
        ratio = rel_x / track_w
        raw_val = self.min_val + ratio * (self.max_val - self.min_val)
        self.set_value(raw_val)

    def handle_event(self, event: pygame.event.Event, mouse_pos: tuple[int, int]) -> bool:
        hovered = self.rect.collidepoint(mouse_pos)
        if hovered and not self.is_hovered and not self.is_dragging:
            assets.play_sound("click1.ogg", volume=0.3)
        self.is_hovered = hovered

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(mouse_pos):
                self.is_dragging = True
                self._update_from_mouse_x(mouse_pos[0])
                assets.play_sound("click2.ogg", volume=0.6)
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging:
                self.is_dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                self._update_from_mouse_x(mouse_pos[0])
                return True
        return False

    def draw(self, surface: pygame.Surface, mouse_pos: tuple[int, int] = (0, 0)):
        pad_x = 14
        track_rect = pygame.Rect(self.rect.x + pad_x, self.rect.centery - 6, self.rect.width - pad_x * 2, 12)
        pygame.draw.rect(surface, (45, 30, 20), track_rect, border_radius=6)
        pygame.draw.rect(surface, (80, 55, 35), track_rect, width=2, border_radius=6)

        ratio = (self.value - self.min_val) / max(0.001, (self.max_val - self.min_val))
        fill_w = int(track_rect.width * ratio)
        if fill_w > 0:
            fill_rect = pygame.Rect(track_rect.x, track_rect.y, fill_w, track_rect.height)
            pygame.draw.rect(surface, (235, 155, 45), fill_rect, border_radius=6)

        knob_cx = track_rect.x + fill_w
        knob_cy = self.rect.centery
        knob_radius = 12

        if self.is_dragging or self.rect.collidepoint(mouse_pos):
            pygame.draw.circle(surface, (255, 255, 255), (knob_cx, knob_cy), knob_radius + 4)
        pygame.draw.circle(surface, (30, 20, 10), (knob_cx, knob_cy + 2), knob_radius)
        pygame.draw.circle(surface, (250, 245, 235), (knob_cx, knob_cy), knob_radius)
        pygame.draw.circle(surface, (120, 70, 25), (knob_cx, knob_cy), knob_radius, width=3)


# ==============================================================================
# TITLE SCENE
# ==============================================================================
class TitleScene(BaseScene):
    def __init__(self):
        super().__init__()
        self.time = 0.0
        self.buttons: list[Button] = []
        self.cached_bg = None
        self.cached_gerobak = None
        self.build_buttons()

    def on_enter(self):
        self.build_buttons()

    def build_buttons(self):
        self.buttons = []
        has_save = save_manager.has_save()
        btn_w, btn_h = 280, 64
        btn_x = INTERNAL_WIDTH // 2 - btn_w // 2
        start_y = 520 if has_save else 560
        gap = 76

        curr_y = start_y
        if has_save:
            self.buttons.append(Button("CONTINUE", x=btn_x, y=curr_y, width=btn_w, height=btn_h, on_click=self.continue_game))
            curr_y += gap

        self.buttons.append(Button("NEW GAME", x=btn_x, y=curr_y, width=btn_w, height=btn_h, on_click=self.new_game))
        curr_y += gap
        self.buttons.append(Button("SETTINGS", x=btn_x, y=curr_y, width=btn_w, height=btn_h, on_click=self.open_settings))
        curr_y += gap
        self.buttons.append(Button("EXIT GAME", x=btn_x, y=curr_y, width=btn_w, height=btn_h, on_click=self.quit_app))

    def continue_game(self):
        from game import GameScene
        save_data = save_manager.load_game()
        self.manager.change_scene(GameScene(save_data=save_data))

    def new_game(self):
        from game import GameScene
        self.manager.change_scene(GameScene(save_data=None))

    def open_settings(self):
        self.manager.push_scene(SettingsScene())

    def quit_app(self):
        pygame.quit()
        sys.exit()

    def handle_event(self, event: pygame.event.Event, mouse_pos: tuple[int, int]):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.quit_app()
            return
        for btn in self.buttons:
            btn.handle_event(event, mouse_pos)

    def update(self, dt: float):
        self.time += dt

    def draw(self, canvas: pygame.Surface):
        # 1. Background
        bg_spr = assets.get_sprite("background")
        if bg_spr:
            if self.cached_bg is None:
                bw, bh = bg_spr.get_size()
                scale = max(INTERNAL_WIDTH / bw, INTERNAL_HEIGHT / bh)
                rw, rh = int(bw * scale), int(bh * scale)
                self.cached_bg = pygame.transform.smoothscale(bg_spr, (rw, rh))
            canvas.blit(self.cached_bg, ((INTERNAL_WIDTH - self.cached_bg.get_width()) // 2, 0))
        else:
            canvas.fill(COLOR_BG_CYAN)

        gerobak_spr = assets.get_sprite("gerobak") or assets.get_sprite("main")
        if gerobak_spr:
            if self.cached_gerobak is None:
                gw, gh = gerobak_spr.get_size()
                scale = max(INTERNAL_WIDTH / gw, INTERNAL_HEIGHT / gh)
                rw, rh = int(gw * scale), int(gh * scale)
                self.cached_gerobak = pygame.transform.smoothscale(gerobak_spr, (rw, rh))
            canvas.blit(self.cached_gerobak, ((INTERNAL_WIDTH - self.cached_gerobak.get_width()) // 2, 0))

            dim_surf = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
            dim_surf.fill((0, 0, 0, 80))
            canvas.blit(dim_surf, (0, 0))

        # Title & Subtitle
        bounce_y = int(math.sin(self.time * 2.5) * 8)
        title_surf = assets.render_text_with_shadow("SO BAKSO", size=64, color=COLOR_GOLD, shadow_color=(40, 25, 10), offset=(3, 4))
        canvas.blit(title_surf, (INTERNAL_WIDTH // 2 - title_surf.get_width() // 2, 60 + bounce_y))

        sub_surf = assets.render_text_with_shadow("Bakso Street Stall Simulation", size=32, color=(255, 240, 220), shadow_color=(30, 20, 10), offset=(2, 2))
        canvas.blit(sub_surf, (INTERNAL_WIDTH // 2 - sub_surf.get_width() // 2, 140))

        # Centerpiece Decorative 3-Layer Bowl
        bowl_back = assets.get_sprite("mangkok-back")
        bowl_front = assets.get_sprite("mangkok-front")
        bowl_shadow = assets.get_shadow_sprite("mangkok", alpha=80)
        bw = (bowl_back or bowl_front).get_width() if (bowl_back or bowl_front) else 400
        bowl_x = INTERNAL_WIDTH // 2 - bw // 2
        bowl_y = 200

        if bowl_shadow:
            canvas.blit(bowl_shadow, (bowl_x + 6, bowl_y + 12))
        if bowl_back:
            canvas.blit(bowl_back, (bowl_x, bowl_y))

        # Ingredients in preview bowl
        mie = assets.get_sprite("mi-kuning")
        bihun = assets.get_sprite("mi-bihun")
        halus = assets.get_sprite("bakso-halus")
        gorengan = assets.get_sprite("gorengan-panjang")
        if mie:
            canvas.blit(mie, (bowl_x + 60, bowl_y + 40))
        if bihun:
            canvas.blit(bihun, (bowl_x + 130, bowl_y + 45))
        if gorengan:
            canvas.blit(gorengan, (bowl_x + 200, bowl_y + 30))
        if halus:
            canvas.blit(halus, (bowl_x + 90, bowl_y + 70))
            canvas.blit(halus, (bowl_x + 170, bowl_y + 65))
        if bowl_front:
            canvas.blit(bowl_front, (bowl_x, bowl_y))

        mouse_pos = self.manager.app.window_to_canvas_pos(pygame.mouse.get_pos()) if (self.manager and self.manager.app) else (0, 0)
        for btn in self.buttons:
            btn.draw(canvas, mouse_pos)


# ==============================================================================
# PAUSE SCENE
# ==============================================================================
class PauseScene(BaseScene):
    def __init__(self, game_scene=None):
        super().__init__()
        self.is_overlay = True
        self.game_scene = game_scene

        self.panel_rect = pygame.Rect(INTERNAL_WIDTH // 2 - 200, INTERNAL_HEIGHT // 2 - 230, 400, 460)
        btn_w, btn_h = 260, 60
        btn_x = self.panel_rect.centerx - btn_w // 2
        start_y = self.panel_rect.y + 100
        gap = 72

        self.buttons = [
            Button("RESUME", x=btn_x, y=start_y, width=btn_w, height=btn_h, on_click=self.resume),
            Button("SETTINGS", x=btn_x, y=start_y + gap, width=btn_w, height=btn_h, on_click=self.open_settings),
            Button("MAIN MENU", x=btn_x, y=start_y + gap * 2, width=btn_w, height=btn_h, on_click=self.to_main_menu),
            Button("EXIT GAME", x=btn_x, y=start_y + gap * 3, width=btn_w, height=btn_h, on_click=self.quit_app),
        ]

    def resume(self):
        self.manager.pop_scene()

    def open_settings(self):
        self.manager.push_scene(SettingsScene())

    def to_main_menu(self):
        if self.game_scene:
            self.game_scene.persist_save()
        self.manager.change_scene(TitleScene())

    def quit_app(self):
        if self.game_scene:
            self.game_scene.persist_save()
        pygame.quit()
        sys.exit()

    def handle_event(self, event: pygame.event.Event, mouse_pos: tuple[int, int]):
        if event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_p]:
            self.resume()
            return
        for btn in self.buttons:
            btn.handle_event(event, mouse_pos)

    def draw(self, canvas: pygame.Surface):
        # Dark overlay
        overlay = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        canvas.blit(overlay, (0, 0))

        # Panel frame
        bg_surf = assets.get_9slice_surface("ui-background", self.panel_rect.width, self.panel_rect.height, slice_margin=32)
        canvas.blit(bg_surf, self.panel_rect.topleft)

        title = assets.render_text("GAME PAUSED", size=38, color=COLOR_WHITE)
        canvas.blit(title, (self.panel_rect.centerx - title.get_width() // 2, self.panel_rect.y + 36))

        mouse_pos = self.manager.app.window_to_canvas_pos(pygame.mouse.get_pos()) if (self.manager and self.manager.app) else (0, 0)
        for btn in self.buttons:
            btn.draw(canvas, mouse_pos)


# ==============================================================================
# SETTINGS SCENE
# ==============================================================================
class SettingsScene(BaseScene):
    def __init__(self):
        super().__init__()
        self.is_overlay = True
        self.panel_rect = pygame.Rect(INTERNAL_WIDTH // 2 - 360, INTERNAL_HEIGHT // 2 - 270, 720, 540)

        self.resolution_options = [
            ("1280x720", (1280, 720)),
            ("1600x900", (1600, 900)),
            ("1920x1080", (1920, 1080)),
        ]
        self.pending_resolution = (1280, 720)
        self.pending_fullscreen = False
        self.status_text = ""

        self.build_ui()

    def build_ui(self):
        px, py = self.panel_rect.x, self.panel_rect.y
        # Resolution buttons
        self.res_buttons = []
        rx = px + 45
        for name, res in self.resolution_options:
            btn = Button(name, x=rx, y=py + 140, width=195, height=50, font_size=22, on_click=lambda r=res: self.select_resolution(r))
            self.res_buttons.append(btn)
            rx += 215

        # Fullscreen button
        self.fullscreen_btn = Button("Fullscreen: OFF", x=self.panel_rect.centerx - 160, y=py + 210, width=320, height=52, font_size=24, on_click=self.toggle_fullscreen)

        # Volume Slider
        current_vol = assets.get_master_volume()
        self.vol_slider = Slider(x=px + 240, y=py + 285, width=280, height=36, min_val=0.0, max_val=1.0, value=current_vol, on_change=self.on_volume_change)

        # Apply & Back buttons
        self.apply_btn = Button("APPLY", x=self.panel_rect.centerx - 220, y=py + 430, width=200, height=56, font_size=24, bg_color=(60, 180, 80), on_click=self.apply_settings)
        self.back_btn = Button("BACK", x=self.panel_rect.centerx + 20, y=py + 430, width=200, height=56, font_size=24, on_click=self.go_back)

    def on_volume_change(self, val: float):
        assets.set_master_volume(val)

    def on_enter(self):
        if self.manager and self.manager.app:
            self.pending_resolution = self.manager.app.window.get_size()
            self.pending_fullscreen = self.manager.app.is_fullscreen
        self.vol_slider.set_value(assets.get_master_volume())
        self.status_text = ""
        self.update_states()

    def update_states(self):
        for (name, res), btn in zip(self.resolution_options, self.res_buttons):
            btn.is_active = (self.pending_resolution == res) and not self.pending_fullscreen

        self.fullscreen_btn.text = "Fullscreen: ON" if self.pending_fullscreen else "Fullscreen: OFF"
        self.fullscreen_btn.is_active = self.pending_fullscreen

        if self.manager and self.manager.app:
            app = self.manager.app
            if self.pending_resolution != app.window.get_size() or self.pending_fullscreen != app.is_fullscreen:
                self.status_text = "* Changes not applied yet. Press APPLY."
            else:
                self.status_text = ""

    def select_resolution(self, res: tuple[int, int]):
        self.pending_resolution = res
        self.pending_fullscreen = False
        self.update_states()

    def toggle_fullscreen(self):
        self.pending_fullscreen = not self.pending_fullscreen
        self.update_states()

    def apply_settings(self):
        if not (self.manager and self.manager.app):
            return
        app = self.manager.app
        if app.is_fullscreen != self.pending_fullscreen:
            app.toggle_fullscreen()
        if not self.pending_fullscreen:
            app.set_window_size(self.pending_resolution[0], self.pending_resolution[1])
        self.status_text = "Settings applied successfully!"
        self.update_states()

    def go_back(self):
        self.manager.pop_scene()

    def handle_event(self, event: pygame.event.Event, mouse_pos: tuple[int, int]):
        if event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
            self.go_back()
            return

        for btn in self.res_buttons:
            btn.handle_event(event, mouse_pos)
        self.fullscreen_btn.handle_event(event, mouse_pos)
        self.vol_slider.handle_event(event, mouse_pos)
        self.apply_btn.handle_event(event, mouse_pos)
        self.back_btn.handle_event(event, mouse_pos)

    def draw(self, canvas: pygame.Surface):
        overlay = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        canvas.blit(overlay, (0, 0))

        bg_surf = assets.get_9slice_surface("ui-background", self.panel_rect.width, self.panel_rect.height, slice_margin=32)
        canvas.blit(bg_surf, self.panel_rect.topleft)

        # Labels
        title = assets.render_text("SETTINGS", size=40, color=COLOR_WHITE)
        canvas.blit(title, (self.panel_rect.centerx - title.get_width() // 2, self.panel_rect.y + 30))

        res_lbl = assets.render_text("Window Resolution", size=24, color=COLOR_WHITE)
        canvas.blit(res_lbl, (self.panel_rect.centerx - res_lbl.get_width() // 2, self.panel_rect.y + 95))

        vol_lbl = assets.render_text("Master Volume", size=24, color=COLOR_WHITE)
        canvas.blit(vol_lbl, (self.panel_rect.x + 60, self.panel_rect.y + 290))

        pct_txt = f"{int(round(assets.get_master_volume() * 100))}%"
        pct_surf = assets.render_text(pct_txt, size=24, color=COLOR_WHITE)
        canvas.blit(pct_surf, (self.panel_rect.x + 550, self.panel_rect.y + 290))

        if self.status_text:
            st_surf = assets.render_text(self.status_text, size=20, color=(255, 230, 80))
            canvas.blit(st_surf, (self.panel_rect.centerx - st_surf.get_width() // 2, self.panel_rect.y + 380))

        mouse_pos = self.manager.app.window_to_canvas_pos(pygame.mouse.get_pos()) if (self.manager and self.manager.app) else (0, 0)
        for btn in self.res_buttons:
            btn.draw(canvas, mouse_pos)
        self.fullscreen_btn.draw(canvas, mouse_pos)
        self.vol_slider.draw(canvas, mouse_pos)
        self.apply_btn.draw(canvas, mouse_pos)
        self.back_btn.draw(canvas, mouse_pos)
