from typing import Callable
import pygame

class BaseScene:
    def __init__(self):
        self.manager: "SceneManager" = None
        self.is_overlay = False  # Set to True if this scene renders on top of previous scenes
        self.key_actions: dict[int, Callable[[], None]] = {}

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def bind_key(self, keys: int | list[int], action: Callable[[], None]):
        """Helper to bind a single key or multiple keys to a function action."""
        if isinstance(keys, int):
            self.key_actions[keys] = action
        else:
            for k in keys:
                self.key_actions[k] = action

    def handle_event(self, event: pygame.event.Event, mouse_canvas_pos: tuple[int, int]):
        if event.type == pygame.KEYDOWN:
            if event.key in self.key_actions:
                self.key_actions[event.key]()

    def update(self, dt: float):
        pass

    def draw(self, canvas: pygame.Surface):
        pass

class SceneManager:
    def __init__(self, app):
        self.app = app
        self.stack: list[BaseScene] = []

    @property
    def current_scene(self) -> BaseScene | None:
        if self.stack:
            return self.stack[-1]
        return None

    def push_scene(self, scene: BaseScene):
        scene.manager = self
        scene.on_enter()
        self.stack.append(scene)

    def pop_scene(self) -> BaseScene | None:
        if self.stack:
            popped = self.stack.pop()
            popped.on_exit()
            if self.stack:
                self.stack[-1].on_enter()
            return popped
        return None

    def change_scene(self, scene: BaseScene):
        while self.stack:
            popped = self.stack.pop()
            popped.on_exit()
        self.push_scene(scene)

    def handle_event(self, event: pygame.event.Event, mouse_canvas_pos: tuple[int, int]):
        if self.current_scene:
            self.current_scene.handle_event(event, mouse_canvas_pos)

    def update(self, dt: float):
        if self.current_scene:
            self.current_scene.update(dt)

    def draw(self, canvas: pygame.Surface):
        if not self.stack:
            return

        # Find first scene from top that is not an overlay
        start_idx = len(self.stack) - 1
        while start_idx > 0 and self.stack[start_idx].is_overlay:
            start_idx -= 1

        # Render from base scene up through active overlay
        for i in range(start_idx, len(self.stack)):
            self.stack[i].draw(canvas)
