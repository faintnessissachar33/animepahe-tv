import flet as ft
from core.theme import AppColors


def build_splash_view() -> ft.View:
    return ft.View(
        route="/",
        controls=[
            ft.Container(
                expand=True,
                alignment=ft.Alignment(0, 0),
                bgcolor=AppColors.SPLASH_BG,
                content=ft.Column(
                    [
                        ft.Container(
                            width=80,
                            height=80,
                            border_radius=20,
                            bgcolor=AppColors.PRIMARY,
                            alignment=ft.Alignment(0, 0),
                            content=ft.Icon(
                                ft.Icons.PLAY_CIRCLE_FILL_ROUNDED,
                                size=48,
                                color=ft.Colors.WHITE,
                            ),
                        ),
                        ft.Container(height=16),
                        ft.Text(
                            "AnimePahe TV",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "Stream anime. No server needed.",
                            size=13,
                            color=AppColors.DARK_TEXT_DIM,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=32),
                        ft.ProgressRing(
                            width=24,
                            height=24,
                            stroke_width=3,
                            color=AppColors.PRIMARY,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=0,
                ),
            )
        ],
        padding=0,
    )
