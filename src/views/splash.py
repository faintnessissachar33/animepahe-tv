import flet as ft
from core.theme import AppTheme


class SplashView:
    def __init__(self, app):
        self.app = app
        self.theme = AppTheme()
        self._connecting = True

    def build(self) -> ft.View:
        return ft.View(
            bgcolor=self.theme.bg_primary,
            controls=[
                ft.Container(
                    expand=True,
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20,
                        controls=[
                            ft.Text(
                                "AnimePahe TV",
                                size=36,
                                weight=ft.FontWeight.BOLD,
                                color=self.theme.accent,
                            ),
                            ft.ProgressRing(
                                width=32,
                                height=32,
                                color=self.theme.accent,
                            ),
                            ft.Text(
                                "Connecting...",
                                size=14,
                                color=self.theme.text_secondary,
                            ),
                        ],
                    ),
                ),
            ],
        )

    def on_ready(self):
        if self._connecting:
            self._connecting = False
            self.app.show_search()
