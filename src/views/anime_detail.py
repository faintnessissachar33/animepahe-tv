import flet as ft
from core.theme import AppTheme


class AnimeDetailView:
    def __init__(self, app):
        self.app = app
        self.theme = AppTheme()
        self._episode_grid: ft.GridView | None = None

    def build(self) -> ft.View:
        anime = self.app.state.selected_anime.get()
        if not anime:
            return ft.View(bgcolor=self.theme.bg_primary, controls=[ft.Text("No anime selected")])

        self._episode_grid = ft.GridView(
            expand=True,
            runs_count=4,
            max_extent=180,
            child_aspect_ratio=1.6,
            spacing=10,
            run_spacing=10,
        )

        return ft.View(
            bgcolor=self.theme.bg_primary,
            controls=[
                ft.Container(
                    padding=20,
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        width=120,
                                        height=180,
                                        border_radius=8,
                                        content=(
                                            ft.Image(src=anime.poster, fit=ft.ImageFit.COVER)
                                            if anime.poster
                                            else ft.Container()
                                        ),
                                    ),
                                    ft.Column(
                                        expand=True,
                                        spacing=4,
                                        controls=[
                                            ft.Text(anime.title, size=24,
                                                    weight=ft.FontWeight.BOLD, color=self.theme.text_primary),
                                            ft.Row(spacing=12, controls=[
                                                ft.Text(f"{anime.year}", color=self.theme.text_muted),
                                                ft.Text(anime.type, color=self.theme.text_muted),
                                                ft.Text(anime.status, color=self.theme.text_muted),
                                                ft.Text(f"{anime.score:.1f}", color=self.theme.accent),
                                            ]),
                                            ft.Text(f"{anime.episodes} episodes",
                                                    color=self.theme.text_secondary),
                                        ],
                                    ),
                                ],
                            ),
                            ft.Container(height=20),
                            ft.Text("Episodes", size=18, color=self.theme.text_secondary),
                            ft.Container(
                                expand=True,
                                height=400,
                                content=self._episode_grid,
                            ),
                        ],
                    ),
                ),
            ],
        )

    def load_episodes(self):
        anime = self.app.state.selected_anime.get()
        if not anime:
            return
        episodes, has_more = self.app.scraper.episodes(anime.session)
        self.app.state.episodes.set(episodes)
        self.app.state.episodes_has_more.set(has_more)
        self._episode_grid.controls.clear()
        for ep in episodes:
            self._episode_grid.controls.append(self._build_episode_card(ep))
        self.app.page.update()

    def _build_episode_card(self, ep) -> ft.Container:
        return ft.Container(
            bgcolor=self.theme.bg_card,
            border_radius=8,
            ink=True,
            on_click=lambda _, e=ep: self.app.show_player(e),
            content=ft.Column(
                spacing=2,
                controls=[
                    ft.Container(
                        height=80,
                        bgcolor=self.theme.bg_secondary,
                        border_radius=ft.border_vertical(top=8),
                        content=(
                            ft.Image(src=ep.snapshot, fit=ft.ImageFit.COVER)
                            if ep.snapshot
                            else ft.Text("No Preview", color=self.theme.text_muted)
                        ),
                    ),
                    ft.Text(f"Ep {ep.episode}", size=13, color=self.theme.text_primary,
                            weight=ft.FontWeight.BOLD),
                    ft.Text(ep.duration, size=11, color=self.theme.text_muted),
                ],
            ),
        )
