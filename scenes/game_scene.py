import pygame

from assets_loader import assets
from bowl import Bowl
from customer import Customer
from ingredient import DraggedItem, IngredientTray
from trash_can import TrashCan
from save_manager import save_manager
from scene_manager import BaseScene
from settings import (
    COLOR_BG_SKY,
    COLOR_BUTTON,
    COLOR_BUTTON_HOVER,
    COLOR_COUNTER_BORDER,
    COLOR_COUNTER_TOP,
    COLOR_GEROBAK_DARK,
    COLOR_GEROBAK_WOOD,
    COLOR_GOLD,
    COLOR_WARUNG_WALL,
    COLOR_WHITE,
    DAY_LENGTH_SECONDS,
    INITIAL_MONEY,
    INITIAL_REPUTATION,
    INTERNAL_HEIGHT,
    INTERNAL_WIDTH,
    ITEM_BAKSO,
    ITEM_BAKSO_URAT,
    ITEM_MI_KUNING,
    PRICE_BAKSO,
    PRICE_BAKSO_URAT,
    PRICE_MI_KUNING,
    REPUTATION_GAIN,
    REPUTATION_LOSS,
)


class GameScene(BaseScene):
    def __init__(self, save_data: dict = None):
        super().__init__()
        # Load progress or default
        if save_data:
            self.day = save_data.get("day", 1)
            self.money = save_data.get("money", INITIAL_MONEY)
            self.reputation = save_data.get("reputation", INITIAL_REPUTATION)
        else:
            self.day = 1
            self.money = INITIAL_MONEY
            self.reputation = INITIAL_REPUTATION
            # If starting a brand new game, write fresh save
            self.persist_save()

        self.state = "PLAYING"  # "PLAYING", "DAY_SUMMARY", "GAME_OVER"
        self.day_timer = DAY_LENGTH_SECONDS

        self.day_earnings = 0
        self.customers_served = 0
        self.customers_failed = 0

        # Entities
        self.bowl = Bowl(x=120, y=118)
        self.trash_can = TrashCan(x=18, y=112, width=34, height=46)

        self.tray_mie = IngredientTray(
            x=185, y=105, width=40, height=28, item_type=ITEM_MI_KUNING, label="Mie"
        )
        self.tray_bakso = IngredientTray(
            x=229, y=105, width=40, height=28, item_type=ITEM_BAKSO, label="B. Halus"
        )
        self.tray_urat = IngredientTray(
            x=273, y=105, width=40, height=28, item_type=ITEM_BAKSO_URAT, label="B. Urat"
        )
        self.trays = [self.tray_mie, self.tray_bakso, self.tray_urat]

        self.current_customer: Customer | None = Customer(x=160, y=42)
        self.customer_spawn_timer = 0.0

        # UI & Buttons
        self.dragged_item: DraggedItem | None = None
        self.pause_btn_rect = pygame.Rect(INTERNAL_WIDTH - 20, 1, 16, 14)
        self.next_day_btn_rect = pygame.Rect(110, 126, 100, 18)
        self.restart_btn_rect = pygame.Rect(110, 116, 100, 18)

        # Mapped Key Actions
        self.key_actions = {
            pygame.K_ESCAPE: self.open_pause_menu,
            pygame.K_p: self.open_pause_menu,
            pygame.K_SPACE: self.serve_current_bowl,
            pygame.K_RETURN: self.serve_current_bowl,
            pygame.K_c: self.bowl.clear,
            pygame.K_BACKSPACE: self.bowl.clear,
            pygame.K_1: lambda: self.bowl.add_ingredient(ITEM_MI_KUNING),
            pygame.K_2: lambda: self.bowl.add_ingredient(ITEM_BAKSO),
            pygame.K_3: lambda: self.bowl.add_ingredient(ITEM_BAKSO_URAT),
        }

    def persist_save(self):
        save_manager.save_game(
            {"day": self.day, "money": self.money, "reputation": self.reputation}
        )

    def handle_event(
        self, event: pygame.event.Event, mouse_canvas_pos: tuple[int, int]
    ):
        if event.type == pygame.KEYDOWN and event.key in self.key_actions:
            self.key_actions[event.key]()
            return

        if self.state == "PLAYING":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 1. Check Pause button
                if self.pause_btn_rect.collidepoint(mouse_canvas_pos):
                    self.open_pause_menu()
                    return

                # 2. Check Trays (Pickup ingredient)
                tray_clicked = False
                for tray in self.trays:
                    drag = tray.handle_mouse_down(mouse_canvas_pos)
                    if drag:
                        self.dragged_item = drag
                        tray_clicked = True
                        break

                # 3. If no tray clicked, check clicking on Bowl (Drag bowl)
                if not tray_clicked and self.bowl.contains_point(mouse_canvas_pos):
                    self.bowl.start_drag(mouse_canvas_pos)

            elif event.type == pygame.MOUSEMOTION:
                # Updating dragged ingredient
                if self.dragged_item:
                    self.dragged_item.update(mouse_canvas_pos)

                # Updating dragged bowl
                if self.bowl.is_dragging:
                    self.bowl.update_drag(mouse_canvas_pos)
                    bowl_center = (
                        self.bowl.x + self.bowl.width // 2,
                        self.bowl.y + self.bowl.height // 2,
                    )
                    self.trash_can.is_hovered = self.trash_can.contains_point(bowl_center)

                # Tray hover states
                for tray in self.trays:
                    tray.update_hover(mouse_canvas_pos)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                # Releasing dragged ingredient
                if self.dragged_item:
                    if self.bowl.contains_point(mouse_canvas_pos):
                        self.bowl.add_ingredient(
                            self.dragged_item.item_type, drop_pos=mouse_canvas_pos
                        )
                    self.dragged_item = None

                # Releasing dragged bowl
                if self.bowl.is_dragging:
                    bowl_center = (
                        self.bowl.x + self.bowl.width // 2,
                        self.bowl.y + self.bowl.height // 2,
                    )

                    # 1. Dropped on Trash Can -> Clear bowl
                    if self.trash_can.contains_point(bowl_center):
                        self.bowl.clear()
                    # 2. Dropped on Customer -> Serve bowl
                    elif self.current_customer and self.current_customer.contains_point(bowl_center):
                        self.serve_current_bowl()

                    # Snap bowl back to prep cutting board
                    self.bowl.reset_position()
                    self.trash_can.is_hovered = False

        elif self.state == "DAY_SUMMARY":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.next_day_btn_rect.collidepoint(mouse_canvas_pos):
                    self.start_next_day()

        elif self.state == "GAME_OVER":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.restart_btn_rect.collidepoint(mouse_canvas_pos):
                    self.restart_game()

    def open_pause_menu(self):
        from scenes.pause_scene import PauseScene

        self.dragged_item = None
        self.bowl.reset_position()
        self.trash_can.is_hovered = False
        self.manager.push_scene(PauseScene(game_scene=self))

    def serve_current_bowl(self):
        if not self.current_customer or self.current_customer.state != "waiting":
            return

        bowl_contents = self.bowl.get_ingredient_counts()
        is_correct, earned = self.current_customer.serve(bowl_contents)

        if is_correct:
            self.money += earned
            self.day_earnings += earned
            self.reputation = min(100, self.reputation + REPUTATION_GAIN)
            self.customers_served += 1
        else:
            self.reputation = max(0, self.reputation - REPUTATION_LOSS)
            self.customers_failed += 1
            if self.reputation <= 0:
                self.state = "GAME_OVER"
                save_manager.delete_save()

        self.bowl.clear()

    def update(self, dt: float):
        if self.state == "PLAYING":
            self.day_timer -= dt
            if self.day_timer <= 0:
                self.day_timer = 0
                self.state = "DAY_SUMMARY"
                self.persist_save()
                return

            if self.current_customer:
                self.current_customer.update(dt)
                if (
                    self.current_customer.state == "angry"
                    and self.current_customer.patience == 0
                    and self.current_customer.feedback_timer >= 1.95
                ):
                    self.reputation = max(0, self.reputation - REPUTATION_LOSS)
                    self.customers_failed += 1
                    if self.reputation <= 0:
                        self.state = "GAME_OVER"
                        save_manager.delete_save()
                        return

                if self.current_customer.state == "done":
                    self.current_customer = None
                    self.customer_spawn_timer = 1.0
            else:
                self.customer_spawn_timer -= dt
                if self.customer_spawn_timer <= 0:
                    self.current_customer = Customer(x=160, y=42)

    def start_next_day(self):
        self.day += 1
        self.day_timer = DAY_LENGTH_SECONDS
        self.day_earnings = 0
        self.customers_served = 0
        self.customers_failed = 0
        self.current_customer = Customer(x=160, y=42)
        self.bowl.clear()
        self.bowl.reset_position()
        self.dragged_item = None
        self.persist_save()
        self.state = "PLAYING"

    def restart_game(self):
        self.day = 1
        self.money = INITIAL_MONEY
        self.reputation = INITIAL_REPUTATION
        self.start_next_day()

    def draw_environment(self, canvas: pygame.Surface):
        canvas.fill(COLOR_BG_SKY)
        pygame.draw.rect(canvas, COLOR_WARUNG_WALL, (0, 16, INTERNAL_WIDTH, 68))
        pygame.draw.rect(canvas, COLOR_GEROBAK_DARK, (0, 16, INTERNAL_WIDTH, 4))
        pygame.draw.rect(canvas, COLOR_GEROBAK_WOOD, (85, 16, 6, 68))
        pygame.draw.rect(canvas, COLOR_GEROBAK_WOOD, (235, 16, 6, 68))

        pygame.draw.rect(canvas, COLOR_COUNTER_TOP, (0, 84, INTERNAL_WIDTH, 96))
        pygame.draw.line(canvas, (215, 175, 130), (0, 84), (INTERNAL_WIDTH, 84), 2)
        pygame.draw.line(canvas, COLOR_COUNTER_BORDER, (0, 86), (INTERNAL_WIDTH, 86), 1)

        # Cutting board / prep mat under bowl
        prep_mat = pygame.Rect(95, 105, 75, 42)
        pygame.draw.rect(canvas, (210, 190, 160), prep_mat)
        pygame.draw.rect(canvas, (160, 140, 110), prep_mat, 1)

    def draw_hud(self, canvas: pygame.Surface):
        pygame.draw.rect(canvas, (35, 25, 20), (0, 0, INTERNAL_WIDTH, 16))
        pygame.draw.line(canvas, COLOR_GOLD, (0, 15), (INTERNAL_WIDTH, 15), 1)

        mins = int(self.day_timer) // 60
        secs = int(self.day_timer) % 60
        hud_left = f"HARI {self.day} | JAM: {mins:02d}:{secs:02d}"
        surf_left = assets.render_text(hud_left, color=COLOR_WHITE)
        canvas.blit(surf_left, (6, 3))

        hud_right = f"Rp {self.money:,} | REP: {self.reputation}%"
        surf_right = assets.render_text(hud_right, color=COLOR_GOLD)
        canvas.blit(surf_right, (INTERNAL_WIDTH - surf_right.get_width() - 24, 3))

        # Pause Button [II]
        mouse_pos = self.manager.app.window_to_canvas_pos(pygame.mouse.get_pos())
        is_hover_pause = self.pause_btn_rect.collidepoint(mouse_pos)
        col_pause = (180, 140, 60) if is_hover_pause else (120, 90, 40)
        pygame.draw.rect(canvas, col_pause, self.pause_btn_rect)
        pygame.draw.rect(canvas, (60, 45, 20), self.pause_btn_rect, 1)
        txt_pause = assets.render_text("II", color=COLOR_WHITE)
        canvas.blit(
            txt_pause,
            (
                self.pause_btn_rect.centerx - txt_pause.get_width() // 2,
                self.pause_btn_rect.centery - txt_pause.get_height() // 2,
            ),
        )

    def draw_summary_overlay(self, canvas: pygame.Surface):
        overlay = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        canvas.blit(overlay, (0, 0))

        card = pygame.Rect(45, 20, 230, 140)
        pygame.draw.rect(canvas, (245, 240, 220), card)
        pygame.draw.rect(canvas, (120, 80, 40), card, 2)

        title = assets.render_text(f"HARI {self.day} SELESAI!", color=(50, 35, 20))
        canvas.blit(title, (card.centerx - title.get_width() // 2, card.top + 8))

        y = card.top + 26
        line1 = assets.render_text(
            f"Pendapatan Hari Ini: Rp{self.day_earnings:,}", color=(30, 120, 40)
        )
        line2 = assets.render_text(
            f"Pesanan Berhasil   : {self.customers_served}", color=(40, 40, 40)
        )
        line3 = assets.render_text(
            f"Pesanan Gagal/Kabur: {self.customers_failed}", color=(180, 40, 40)
        )
        line4 = assets.render_text(
            f"Total Kas Warung   : Rp{self.money:,}", color=(40, 40, 40)
        )

        canvas.blit(line1, (card.left + 12, y))
        canvas.blit(line2, (card.left + 12, y + 14))
        canvas.blit(line3, (card.left + 12, y + 28))
        canvas.blit(line4, (card.left + 12, y + 42))

        mouse_pos = self.manager.app.window_to_canvas_pos(pygame.mouse.get_pos())
        col = (
            COLOR_BUTTON_HOVER
            if self.next_day_btn_rect.collidepoint(mouse_pos)
            else COLOR_BUTTON
        )
        pygame.draw.rect(canvas, col, self.next_day_btn_rect)
        pygame.draw.rect(canvas, (100, 60, 20), self.next_day_btn_rect, 1)
        btn_txt = assets.render_text("LANJUT HARI", color=COLOR_WHITE)
        canvas.blit(
            btn_txt,
            (
                self.next_day_btn_rect.centerx - btn_txt.get_width() // 2,
                self.next_day_btn_rect.centery - btn_txt.get_height() // 2,
            ),
        )

    def draw_game_over(self, canvas: pygame.Surface):
        overlay = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((40, 10, 10, 210))
        canvas.blit(overlay, (0, 0))

        card = pygame.Rect(50, 30, 220, 120)
        pygame.draw.rect(canvas, (245, 220, 220), card)
        pygame.draw.rect(canvas, (180, 40, 40), card, 2)

        title = assets.render_text("WARUNG BANGKRUT!", color=(180, 30, 30))
        canvas.blit(title, (card.centerx - title.get_width() // 2, card.top + 10))

        msg = assets.render_text("Reputasi warung menyentuh 0%.", color=(50, 30, 30))
        canvas.blit(msg, (card.centerx - msg.get_width() // 2, card.top + 30))

        mouse_pos = self.manager.app.window_to_canvas_pos(pygame.mouse.get_pos())
        col = (
            (230, 80, 80)
            if self.restart_btn_rect.collidepoint(mouse_pos)
            else (190, 50, 50)
        )
        pygame.draw.rect(canvas, col, self.restart_btn_rect)
        pygame.draw.rect(canvas, (100, 20, 20), self.restart_btn_rect, 1)
        btn_txt = assets.render_text("MAIN LAGI", color=COLOR_WHITE)
        canvas.blit(
            btn_txt,
            (
                self.restart_btn_rect.centerx - btn_txt.get_width() // 2,
                self.restart_btn_rect.centery - btn_txt.get_height() // 2,
            ),
        )

    def draw(self, canvas: pygame.Surface):
        self.draw_environment(canvas)

        # Draw Customer (behind counter)
        if self.current_customer:
            self.current_customer.draw(canvas)
            if self.current_customer.state == "waiting":
                self.current_customer.order.draw_ticket(
                    canvas, x=10, y=24, width=68, height=56
                )

        # Draw Trash Can
        self.trash_can.draw(canvas)

        # Draw Trays
        for tray in self.trays:
            tray.draw(canvas)

        # Draw Bowl (with its contents)
        self.bowl.draw(canvas)

        # Draw Dragged Ingredient (if dragging an ingredient from tray)
        if self.dragged_item:
            self.dragged_item.draw(canvas)

        # Draw HUD (Always on top)
        self.draw_hud(canvas)

        # Overlays
        if self.state == "DAY_SUMMARY":
            self.draw_summary_overlay(canvas)
        elif self.state == "GAME_OVER":
            self.draw_game_over(canvas)
