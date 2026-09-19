import pygame
from scene_manager import BaseScene
from assets_loader import assets
from settings import INTERNAL_WIDTH, INTERNAL_HEIGHT
from ui import VBox, HBox, Button, Label

class SettingsScene(BaseScene):
    def __init__(self):
        super().__init__()
        self.is_overlay = True
        self.scale_options = [2, 3, 4]
        self.build_ui()

    def build_ui(self):
        card_w = 190
        card_h = 136
        cx = INTERNAL_WIDTH // 2 - card_w // 2
        cy = INTERNAL_HEIGHT // 2 - card_h // 2
        self.card_rect = pygame.Rect(cx, cy, card_w, card_h)

        # Scale Buttons Row (HBox)
        self.scale_buttons = []
        for s in self.scale_options:
            btn = Button(
                f"{s}x",
                width=36,
                height=16,
                on_click=lambda val=s: self.set_scale(val)
            )
            self.scale_buttons.append(btn)

        self.scale_row = HBox(gap=6, align="center", children=self.scale_buttons)

        # Fullscreen Button
        self.fullscreen_btn = Button(
            "Layar Penuh: OFF",
            width=120,
            height=16,
            on_click=self.toggle_fullscreen
        )

        # Back Button
        self.back_btn = Button(
            "KEMBALI",
            width=80,
            height=18,
            bg_color=(190, 80, 50),
            hover_color=(220, 100, 70),
            border_color=(100, 30, 20),
            on_click=self.go_back
        )

        # Main Vertical Auto Layout
        self.main_layout = VBox(
            x=self.card_rect.left + 15,
            y=self.card_rect.top + 28,
            gap=8,
            align="center",
            children=[
                Label("Ukuran Layar (Scale):"),
                self.scale_row,
                self.fullscreen_btn,
                self.back_btn
            ]
        )

        # Re-center main layout inside card
        layout_w, layout_h = self.main_layout.compute_size()
        self.main_layout.x = self.card_rect.centerx - layout_w // 2
        self.main_layout.reflow()

    def on_enter(self):
        self.update_button_states()

    def update_button_states(self):
        cur_scale = self.manager.app.current_scale
        is_fs = self.manager.app.is_fullscreen

        for s, btn in zip(self.scale_options, self.scale_buttons):
            btn.is_active = (cur_scale == s and not is_fs)

        self.fullscreen_btn.set_text("Layar Penuh: ON" if is_fs else "Layar Penuh: OFF")
        self.fullscreen_btn.is_active = is_fs
        self.main_layout.reflow()

    def set_scale(self, scale_val: int):
        self.manager.app.set_scale(scale_val)
        self.update_button_states()

    def toggle_fullscreen(self):
        self.manager.app.toggle_fullscreen()
        self.update_button_states()

    def go_back(self):
        self.manager.pop_scene()

    def handle_event(self, event: pygame.event.Event, mouse_canvas_pos: tuple[int, int]):
        # Mapped Key Actions
        key_actions = {
            pygame.K_ESCAPE: self.go_back,
            pygame.K_BACKSPACE: self.go_back,
        }

        if event.type == pygame.KEYDOWN and event.key in key_actions:
            key_actions[event.key]()
            return

        self.main_layout.handle_event(event, mouse_canvas_pos)

    def draw(self, canvas: pygame.Surface):
        # Overlay
        overlay = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        canvas.blit(overlay, (0, 0))

        # Modal Card
        pygame.draw.rect(canvas, (245, 240, 220), self.card_rect)
        pygame.draw.rect(canvas, (120, 80, 40), self.card_rect, 2)

        # Title
        title = assets.render_text("PENGATURAN", color=(60, 40, 20))
        canvas.blit(title, (self.card_rect.centerx - title.get_width() // 2, self.card_rect.top + 8))

        # Draw Auto-Layout Tree
        mouse_pos = self.manager.app.window_to_canvas_pos(pygame.mouse.get_pos())
        self.update_button_states()
        self.main_layout.draw(canvas, mouse_pos)
