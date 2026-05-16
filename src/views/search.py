import flet as ft
from core.theme import AppColors


def build_search_view(
    page_obj: ft.Page,
    on_search: callable,
    on_select_anime: callable,
) -> ft.View:
    search_field = ft.TextField(
        hint_text="Search anime...",
        color=AppColors.DARK_TEXT,
        bgcolor=AppColors.DARK_SURFACE,
        border_color=AppColors.DARK_TEXT_MUTED,
        border_radius=10,
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        on_submit=lambda e: page_obj.run_task(on_search, e.data.strip()),
    )

    results_grid = ft.GridView(
        expand=True,
        runs_count=4,
        max_extent=180,
        child_aspect_ratio=0.55,
        spacing=12,
        run_spacing=12,
    )

    def refresh_results():
        from core.state import state
        results_grid.controls.clear()
        for anime in state.search_results:
            card = _build_card(anime, page_obj, on_select_anime)
            results_grid.controls.append(card)
        page_obj.update()

    page_obj.refresh_search_results = refresh_results

    content = ft.Column(
        [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Container(
                                    width=36,
                                    height=36,
                                    border_radius=10,
                                    bgcolor=AppColors.PRIMARY,
                                    alignment=ft.Alignment(0, 0),
                                    content=ft.Icon(
                                        ft.Icons.PLAY_CIRCLE_FILL_ROUNDED,
                                        size=20,
                                        color=ft.Colors.WHITE,
                                    ),
                                ),
                                ft.Text(
                                    "AnimePahe TV",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=AppColors.DARK_TEXT,
                                ),
                            ],
                            spacing=10,
                        ),
                        ft.Container(height=16),
                        search_field,
                    ],
                    spacing=0,
                ),
                padding=ft.Padding(20, 20, 20, 0),
            ),
            ft.Container(
                expand=True,
                padding=ft.Padding(20, 10, 20, 20),
                content=results_grid,
            ),
        ],
        spacing=0,
        expand=True,
    )

    return ft.View(
        route="/search",
        controls=[
            ft.SafeArea(
                ft.Container(
                    content=content,
                    expand=True,
                    bgcolor=AppColors.DARK_BG,
                ),
                expand=True,
            ),
        ],
        padding=0,
    )


def _build_card(anime, page_obj: ft.Page, on_select_anime: callable) -> ft.Container:
    return ft.Container(
        width=180,
        height=320,
        bgcolor=AppColors.DARK_SURFACE,
        border_radius=12,
        ink=True,
        on_click=lambda _: on_select_anime(anime),
        content=ft.Column(
            spacing=4,
            controls=[
                ft.Container(
                    height=200,
                    bgcolor=AppColors.DARK_SURFACE_VARIANT,
                    border_radius=ft.border_vertical(top=12),
                    content=(
                        ft.Image(src=anime.poster, fit=ft.ImageFit.COVER,
                                 border_radius=ft.border_vertical(top=12))
                        if anime.poster
                        else ft.Icon(ft.Icons.MOVIE, size=40, color=AppColors.DARK_TEXT_MUTED)
                    ),
                ),
                ft.Container(
                    padding=ft.Padding(8, 4, 8, 8),
                    content=ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(
                                anime.title,
                                size=12,
                                color=AppColors.DARK_TEXT,
                                weight=ft.FontWeight.BOLD,
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Row(
                                spacing=6,
                                controls=[
                                    ft.Text(str(anime.year), size=10, color=AppColors.DARK_TEXT_MUTED),
                                    ft.Text(anime.type, size=10, color=AppColors.DARK_TEXT_MUTED),
                                    ft.Container(expand=True),
                                    ft.Text(
                                        f"{anime.score:.1f}",
                                        size=11,
                                        color=AppColors.PRIMARY,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
            ],
        ),
    )
