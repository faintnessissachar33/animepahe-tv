import flet as ft
from core.theme import AppTheme


class SearchView:
    def __init__(self, app):
        self.app = app
        self.theme = AppTheme()
        self._search_field: ft.TextField | None = None
        self._results_row: ft.Row | None = None

    def build(self) -> ft.View:
        self._search_field = ft.TextField(
            hint_text="Search anime...",
            color=self.theme.text_primary,
            bgcolor=self.theme.bg_card,
            border_color=self.theme.text_muted,
            border_radius=8,
            on_submit=self._on_search,
        )
        self._results_row = ft.Row(wrap=True, spacing=12, run_spacing=12)
        return ft.View(
            bgcolor=self.theme.bg_primary,
            controls=[
                ft.Container(
                    padding=20,
                    content=ft.Column(
                        controls=[
                            self._search_field,
                            ft.Container(height=20),
                            ft.Text("Results", size=18, color=self.theme.text_secondary),
                            ft.Container(
                                expand=True,
                                content=ft.ListView(
                                    controls=[self._results_row],
                                    auto_scroll=False,
                                ),
                            ),
                        ],
                    ),
                ),
            ],
        )

    def _on_search(self, e):
        query = self._search_field.value.strip()
        if query:
            self.app.state.search_query.set(query)
            results, has_more = self.app.scraper.search(query)
            self.app.state.search_results.set(results)
            self.app.state.search_has_more.set(has_more)
            self._display_results(results)

    def _display_results(self, results):
        self._results_row.controls.clear()
        for anime in results:
            card = self._build_card(anime)
            self._results_row.controls.append(card)
        self.app.page.update()

    def _build_card(self, anime) -> ft.Container:
        return ft.Container(
            width=160,
            height=280,
            bgcolor=self.theme.bg_card,
            border_radius=8,
            ink=True,
            on_click=lambda _, a=anime: self.app.show_detail(a),
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Container(
                        height=200,
                        bgcolor=self.theme.bg_secondary,
                        border_radius=ft.border_vertical(top=8),
                        content=(
                            ft.Image(src=anime.poster, fit=ft.ImageFit.COVER, border_radius=8)
                            if anime.poster
                            else ft.Text("No Poster", color=self.theme.text_muted)
                        ),
                    ),
                    ft.Text(anime.title, size=12, color=self.theme.text_primary,
                            weight=ft.FontWeight.BOLD, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Text(str(anime.year), size=11, color=self.theme.text_muted),
                            ft.Text(anime.type, size=11, color=self.theme.text_muted),
                            ft.Text(f"{anime.score:.1f}", size=11, color=self.theme.accent),
                        ],
                    ),
                ],
            ),
        )
