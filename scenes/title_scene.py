import math
import sys
import pygame

from config import INTERNAL_HEIGHT, INTERNAL_WIDTH
from core import BaseScene, assets, save_manager
from items.registry import items_registry
from ui import Button, VBox

COLOR_BG_CYAN = (75, 205, 240)
COLOR_GOLD = (255, 205, 45)


class TitleScene(BaseScene):
    def __init__(self):
        super().__init__()
        self.time = 0.0
        self.menu_layout = None
        self.cached_bg: pygame.Surface | None = None
        self.rebuild_layout()

    def on_enter(self):
        self.rebuild_layout()

    def rebuild_layout(self):
        has_save = save_manager.has_save()
        btn_w = 280
        btn_h = 64
        btn_font = 28

        children = []
        if has_save:
            children.append(
                Button(
                    "CONTINUE",
                    width=btn_w,
                    height=btn_h,
                    font_size=btn_font,
                    on_click=self.continue_game,
                )
            )

        children.extend([
            Button(
                "NEW GAME",
                width=btn_w,
                height=btn_h,
                font_size=btn_font,
                on_click=self.new_game,
            ),
            Button(
                "SETTINGS",
                width=btn_w,
                height=btn_h,
                font_size=btn_font,
                on_click=self.open_settings,
            ),
            Button(
                "EXIT GAME",
                width=btn_w,
                height=btn_h,
                font_size=btn_font,
                on_click=self.quit_app,
            ),
        ])

        start_y = 520 if has_save else 560
        self.menu_layout = VBox(
            x=INTERNAL_WIDTH // 2 - btn_w // 2,
            y=start_y,
            gap=16,
            align="center",
            children=children,
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

    def handle_event(
        self, event: pygame.event.Event, mouse_canvas_pos: tuple[int, int]
    ):
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
        # 1. Background image (assets/sprites/game/background.jpg)
        bg_spr = assets.get_sprite("background")
        if bg_spr:
            if not hasattr(self, "cached_main_bg") or self.cached_main_bg is None:
                bw, bh = bg_spr.get_size()
                scale = max(INTERNAL_WIDTH / bw, INTERNAL_HEIGHT / bh)
                rw, rh = int(bw * scale), int(bh * scale)
                self.cached_main_bg = pygame.transform.smoothscale(bg_spr, (rw, rh))
            canvas.blit(
                self.cached_main_bg,
                ((INTERNAL_WIDTH - self.cached_main_bg.get_width()) // 2, 0),
            )
        else:
            canvas.fill(COLOR_BG_CYAN)

        gerobak_spr = assets.get_sprite("gerobak") or assets.get_sprite("main")
        if gerobak_spr:
            if self.cached_bg is None:
                gw, gh = gerobak_spr.get_size()
                scale = max(INTERNAL_WIDTH / gw, INTERNAL_HEIGHT / gh)
                rw, rh = int(gw * scale), int(gh * scale)
                self.cached_bg = pygame.transform.smoothscale(gerobak_spr, (rw, rh))
            canvas.blit(self.cached_bg, ((INTERNAL_WIDTH - self.cached_bg.get_width()) // 2, 0))

            # Darkening vignette for main menu
            dim_surf = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
            dim_surf.fill((0, 0, 0, 80))
            canvas.blit(dim_surf, (0, 0))

        # Title with bounce
        bounce_y = int(math.sin(self.time * 2.5) * 8)
        title_y = 60 + bounce_y

        title_surf = assets.render_text_with_shadow(
            "SO BAKSO",
            size=64,
            color=COLOR_GOLD,
            shadow_color=(40, 25, 10),
            offset=(3, 4),
        )
        canvas.blit(
            title_surf,
            (INTERNAL_WIDTH // 2 - title_surf.get_width() // 2, title_y),
        )

        sub_surf = assets.render_text_with_shadow(
            "Bakso Street Stall Simulation",
            size=32,
            color=(255, 240, 220),
            shadow_color=(30, 20, 10),
            offset=(2, 2),
        )
        canvas.blit(
            sub_surf, (INTERNAL_WIDTH // 2 - sub_surf.get_width() // 2, 140)
        )

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

        # Ingredients inside bowl
        mie_def = items_registry.get("mi_kuning")
        bihun_def = items_registry.get("mi_bihun")
        halus_def = items_registry.get("bakso_halus")
        gorengan_def = items_registry.get("gorengan_panjang")

        if mie_def and mie_def.sprite:
            canvas.blit(mie_def.sprite, (bowl_x + 60, bowl_y + 40))
        if bihun_def and bihun_def.sprite:
            canvas.blit(bihun_def.sprite, (bowl_x + 130, bowl_y + 45))
        if gorengan_def and gorengan_def.sprite:
            canvas.blit(gorengan_def.sprite, (bowl_x + 200, bowl_y + 30))
        if halus_def and halus_def.sprite:
            canvas.blit(halus_def.sprite, (bowl_x + 90, bowl_y + 70))
            canvas.blit(halus_def.sprite, (bowl_x + 170, bowl_y + 65))

        if bowl_front:
            canvas.blit(bowl_front, (bowl_x, bowl_y))

        mouse_pos = (
            self.manager.app.window_to_canvas_pos(pygame.mouse.get_pos())
            if (self.manager and hasattr(self.manager, "app") and self.manager.app)
            else (0, 0)
        )
        if self.menu_layout:
            self.menu_layout.draw(canvas, mouse_pos)

