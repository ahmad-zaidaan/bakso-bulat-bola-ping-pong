from abc import ABC, abstractmethod
import pygame


class BaseScene(ABC):
    def __init__(self):
        self.manager = None
        self.is_overlay = False

    def on_enter(self):
        """Called when this scene becomes the active scene."""
        pass

    def on_exit(self):
        """Called when this scene is popped or replaced."""
        pass

    def handle_event(
        self, event: pygame.event.Event, mouse_canvas_pos: tuple[int, int]
    ):
        """Handles Pygame input events."""
        pass

    def update(self, dt: float):
        """Updates game state (dt in seconds)."""
        pass

    @abstractmethod
    def draw(self, canvas: pygame.Surface):
        """Renders the scene content onto the low-res retro canvas."""
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

    def handle_event(
        self, event: pygame.event.Event, mouse_canvas_pos: tuple[int, int]
    ):
        if self.current_scene:
            self.current_scene.handle_event(event, mouse_canvas_pos)

    def update(self, dt: float):
        if self.current_scene:
            self.current_scene.update(dt)

    def draw(self, canvas: pygame.Surface):
        if not self.scene_stack:
            return

        # Find the lowest scene index that is NOT an overlay
        start_idx = len(self.scene_stack) - 1
        while start_idx > 0 and self.scene_stack[start_idx].is_overlay:
            start_idx -= 1

        for i in range(start_idx, len(self.scene_stack)):
            self.scene_stack[i].draw(canvas)
