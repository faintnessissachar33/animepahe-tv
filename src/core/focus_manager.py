import flet as ft


class FocusManager:
    def __init__(self, page: ft.Page):
        self.page = page
        self.focused_index = 0
        self.focusable: list[ft.Control] = []

    def register(self, controls: list[ft.Control]):
        self.focusable = controls
        if self.focusable:
            self._apply_focus(self.focusable[0])

    def handle_key(self, e: ft.KeyboardEvent):
        if e.key == "ArrowDown":
            self._move_focus(1)
        elif e.key == "ArrowUp":
            self._move_focus(-1)
        elif e.key == "ArrowRight":
            self._move_focus(1)
        elif e.key == "ArrowLeft":
            self._move_focus(-1)
        elif e.key == "Enter" or e.key == " ":
            self._activate_focus()

    def _move_focus(self, direction: int):
        if not self.focusable:
            return
        self._remove_focus(self.focusable[self.focused_index])
        self.focused_index = (self.focused_index + direction) % len(self.focusable)
        self._apply_focus(self.focusable[self.focused_index])
        self.page.update()

    def _apply_focus(self, control: ft.Control):
        control.scale = ft.transform.Scale(1.05)
        control.opacity = 1.0

    def _remove_focus(self, control: ft.Control):
        control.scale = ft.transform.Scale(1.0)
        control.opacity = 0.8

    def _activate_focus(self):
        if self.focusable and self.focusable[self.focused_index]:
            control = self.focusable[self.focused_index]
            if hasattr(control, "on_click") and control.on_click:
                control.on_click(None)
