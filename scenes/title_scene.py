import sys
import math
import pygame
from scene_manager import BaseScene
from save_manager import save_manager
from assets_loader import assets
from settings import (
    INTERNAL_WIDTH, INTERNAL_HEIGHT,
    COLOR_BG_SKY, COLOR_WARUNG_WALL, COLOR_GEROBAK_WOOD, COLOR_GEROBAK_DARK,
    COLOR_GOLD
)
from ui import VBox, Button

class TitleScene(BaseScene):
    def __init__(self):
        super().__init__()
        self.time = 0.0
        self.menu_layout = None
        self.rebuild_layout()

    def on_enter(self):
        self.rebuild_layout()

    def rebuild_layout(self):
        has_save = save_manager.has_save()
        btn_w = 90
        btn_h = 16

        children = []
        if has_save:
            children.append(Button("LANJUTKAN", width=btn_w, height=btn_h, on_click=self.continue_game))

        children.extend([
            Button("GAME BARU", width=btn_w, height=btn_h, on_click=self.new_game),
            Button("PENGATURAN", width=btn_w, height=btn_h, on_click=self.open_settings),
            Button("KELUAR", width=btn_w, height=btn_h, on_click=self.quit_app),
        ])

        start_y = 86 if has_save else 96
        self.menu_layout = VBox(
            x=INTERNAL_WIDTH // 2 - btn_w // 2,
            y=start_y,
            gap=3,
            align="center",
            children=children
        )

    def continue_game(self):
        from scenes.game_scene import GameScene
        save_data = save_manager.load_game()
        self.manager.change_scene(GameScene(save_data=save_data))

    def new_game(self):
        from scenes.game_scene import GameScene
        self.manager.change_scene(GameScene(save_data=None))

    def open_settings(self):
        from scenes.settings_scene import SettingsScene
        self.manager.push_scene(SettingsScene())

    def quit_app(self):
        pygame.quit()
        sys.exit()

    def handle_event(self, event: pygame.event.Event, mouse_canvas_pos: tuple[int, int]):
        # Mapped Key Actions
        key_actions = {
            pygame.K_ESCAPE: self.quit_app,
        }

        if event.type == pygame.KEYDOWN and event.key in key_actions:
            key_actions[event.key]()
            return

        if self.menu_layout:
            self.menu_layout.handle_event(event, mouse_canvas_pos)

    def update(self, dt: float):
        self.time += dt

    def draw(self, canvas: pygame.Surface):
        # Background
        canvas.fill(COLOR_BG_SKY)
        pygame.draw.rect(canvas, COLOR_WARUNG_WALL, (0, 36, INTERNAL_WIDTH, 144))
        
        # Gerobak wood borders
        pygame.draw.rect(canvas, COLOR_GEROBAK_DARK, (0, 34, INTERNAL_WIDTH, 4))
        pygame.draw.rect(canvas, COLOR_GEROBAK_WOOD, (30, 34, 6, 146))
        pygame.draw.rect(canvas, COLOR_GEROBAK_WOOD, (INTERNAL_WIDTH - 36, 34, 6, 146))

        # Title Banner with bounce
        bounce_y = int(math.sin(self.time * 2.5) * 2)
        title_y = 10 + bounce_y

        title_surf = assets.render_text_with_shadow(
            "BAKSO BULAT BOLA PING PONG",
            color=COLOR_GOLD,
            shadow_color=(30, 20, 10),
            offset=(1, 1),
            scale=1
        )
        canvas.blit(title_surf, (INTERNAL_WIDTH // 2 - title_surf.get_width() // 2, title_y))

        sub_surf = assets.render_text("Simulasi Gerobak Bakso Kaki Lima", color=(65, 45, 30))
        canvas.blit(sub_surf, (INTERNAL_WIDTH // 2 - sub_surf.get_width() // 2, 22))

        # Decorative Bowl & Meatballs in center with sprite-shaped shadows
        bowl_spr = assets.get_sprite("mangkok")
        bowl_shadow = assets.get_shadow_sprite("mangkok", alpha=70)
        bakso_spr = assets.get_sprite("bakso")
        bakso_shadow = assets.get_shadow_sprite("bakso", alpha=60)
        urat_spr = assets.get_sprite("bakso_urat")
        urat_shadow = assets.get_shadow_sprite("bakso_urat", alpha=60)

        bowl_x = INTERNAL_WIDTH // 2 - (bowl_spr.get_width() // 2 if bowl_spr else 12)
        bowl_y = 48
        if bowl_spr:
            if bowl_shadow:
                canvas.blit(bowl_shadow, (bowl_x + 1, bowl_y + 2))
            canvas.blit(bowl_spr, (bowl_x, bowl_y))
            if bakso_spr:
                if bakso_shadow:
                    canvas.blit(bakso_shadow, (bowl_x + 6, bowl_y + 4))
                    canvas.blit(bakso_shadow, (bowl_x + 14, bowl_y + 5))
                canvas.blit(bakso_spr, (bowl_x + 5, bowl_y + 3))
                canvas.blit(bakso_spr, (bowl_x + 13, bowl_y + 4))
            if urat_spr:
                if urat_shadow:
                    canvas.blit(urat_shadow, (bowl_x + 9, bowl_y + 3))
                canvas.blit(urat_spr, (bowl_x + 8, bowl_y + 2))

        # Draw Auto-Layout Menu
        mouse_pos = self.manager.app.window_to_canvas_pos(pygame.mouse.get_pos())
        if self.menu_layout:
            self.menu_layout.draw(canvas, mouse_pos)

        # Version tag
        ver_surf = assets.render_text("v0.2 - pygame-ce", color=(130, 110, 90))
        canvas.blit(ver_surf, (INTERNAL_WIDTH - ver_surf.get_width() - 4, INTERNAL_HEIGHT - 12))
