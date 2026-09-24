import pygame

from config import INTERNAL_HEIGHT, INTERNAL_WIDTH
from core import BaseScene, assets
from ui import Button, HBoxContainer, Label, PanelContainer, Slider, VBoxContainer


class SettingsScene(BaseScene):
    def __init__(self):
        super().__init__()
        self.is_overlay = True
        self.resolution_options = [
            ("1280x720 (HD)", (1280, 720)),
            ("1600x900", (1600, 900)),
            ("1920x1080 (FHD)", (1920, 1080)),
        ]

        self.pending_resolution = (1280, 720)
        self.pending_fullscreen = False

        self.build_ui()

    def build_ui(self):
        self.res_buttons = []
        for name, res in self.resolution_options:
            btn = Button(
                name,
                width=220,
                height=54,
                font_size=22,
                on_click=lambda r=res: self.select_resolution(r),
            )
            self.res_buttons.append(btn)

        self.res_row = HBoxContainer(
            separation=12, align_items="center", children=self.res_buttons
        )

        self.fullscreen_btn = Button(
            "Layar Penuh: OFF",
            width=320,
            height=56,
            font_size=24,
            on_click=self.toggle_pending_fullscreen,
        )

        # Master Volume
        current_vol = assets.get_master_volume()
        self.vol_value_label = Label(f"{int(round(current_vol * 100))}%", font_size=24, color=(255, 255, 255))
        self.vol_slider = Slider(
            min_value=0.0,
            max_value=1.0,
            value=current_vol,
            step=0.05,
            width=300,
            height=36,
            on_value_change=self.on_volume_change,
        )
        self.vol_row = HBoxContainer(
            separation=16,
            align_items="center",
            children=[
                Label("Volume Master", font_size=24, color=(255, 255, 255)),
                self.vol_slider,
                self.vol_value_label,
            ],
        )

        self.apply_btn = Button(
            "APPLY",
            width=240,
            height=58,
            font_size=24,
            bg_color=(60, 180, 80),
            hover_color=(80, 210, 100),
            on_click=self.apply_settings,
        )

        self.back_btn = Button(
            "BACK",
            width=200,
            height=58,
            font_size=24,
            on_click=self.go_back,
        )

        self.action_row = HBoxContainer(
            separation=18, align_items="center", children=[self.apply_btn, self.back_btn]
        )

        self.status_label = Label(
            "",
            font_size=22,
            color=(0, 0, 0),
            margin=(0, 0, 0, 0),
        )

        self.panel = PanelContainer(
            padding=(32, 48, 32, 48),
            use_texture=True,
            texture_id="ui-background",
            slice_margin=32,
            children=[
                VBoxContainer(
                    separation=16,
                    align_items="center",
                    children=[
                        Label("SETTINGS", font_size=40, color=(255, 255, 255)),
                        Label("Window Resolution", font_size=24, color=(255, 255, 255)),
                        self.res_row,
                        self.fullscreen_btn,
                        self.vol_row,
                        self.status_label,
                        self.action_row,
                    ],
                )
            ],
        )
        pw, ph = self.panel.get_minimum_size()
        self.panel.rect.topleft = (
            INTERNAL_WIDTH // 2 - pw // 2,
            INTERNAL_HEIGHT // 2 - ph // 2,
        )
        self.panel.reflow()

        self.key_actions = {
            pygame.K_ESCAPE: self.go_back,
            pygame.K_BACKSPACE: self.go_back,
        }

    def on_volume_change(self, val: float):
        assets.set_master_volume(val)
        self.vol_value_label.set_text(f"{int(round(val * 100))}%")
        self.panel.reflow()

    def on_enter(self):
        if self.manager and hasattr(self.manager, "app") and self.manager.app:
            self.pending_resolution = self.manager.app.window.get_size()
            self.pending_fullscreen = self.manager.app.is_fullscreen
        self.vol_slider.set_value(assets.get_master_volume())
        self.vol_value_label.set_text(f"{int(round(assets.get_master_volume() * 100))}%")
        self.status_label.set_text("")
        self.update_button_states()

    def update_button_states(self):
        for (name, res), btn in zip(self.resolution_options, self.res_buttons):
            btn.is_active = (self.pending_resolution == res) and not self.pending_fullscreen

        self.fullscreen_btn.set_text(
            "Fullscreen: ON" if self.pending_fullscreen else "Fullscreen: OFF"
        )
        self.fullscreen_btn.is_active = self.pending_fullscreen

        # Check if changes are pending
        if self.manager and hasattr(self.manager, "app") and self.manager.app:
            app = self.manager.app
            has_changes = (
                self.pending_resolution != app.window.get_size()
                or self.pending_fullscreen != app.is_fullscreen
            )
            if has_changes:
                self.status_label.set_text("* Perubahan belum diterapkan. Tekan TERAPKAN.")
            else:
                self.status_label.set_text("")

        self.panel.reflow()

    def select_resolution(self, res: tuple[int, int]):
        self.pending_resolution = res
        self.pending_fullscreen = False
        self.update_button_states()

    def toggle_pending_fullscreen(self):
        self.pending_fullscreen = not self.pending_fullscreen
        self.update_button_states()

    def apply_settings(self):
        if not (self.manager and hasattr(self.manager, "app") and self.manager.app):
            return
        app = self.manager.app

        # Apply fullscreen if changed
        if app.is_fullscreen != self.pending_fullscreen:
            app.toggle_fullscreen()

        # Apply resolution if not in fullscreen
        if not self.pending_fullscreen:
            app.set_window_size(self.pending_resolution[0], self.pending_resolution[1])

        self.status_label.set_text("Changes applied!")
        self.update_button_states()

    def go_back(self):
        self.manager.pop_scene()

    def handle_event(
        self, event: pygame.event.Event, mouse_canvas_pos: tuple[int, int]
    ):
        if event.type == pygame.KEYDOWN and event.key in self.key_actions:
            self.key_actions[event.key]()
            return

        self.panel.handle_event(event, mouse_canvas_pos)

    def draw(self, canvas: pygame.Surface):
        overlay = pygame.Surface(
            (INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 180))
        canvas.blit(overlay, (0, 0))

        mouse_pos = (
            self.manager.app.window_to_canvas_pos(pygame.mouse.get_pos())
            if (self.manager and hasattr(self.manager, "app") and self.manager.app)
            else (0, 0)
        )
        self.panel.draw(canvas, mouse_pos)
