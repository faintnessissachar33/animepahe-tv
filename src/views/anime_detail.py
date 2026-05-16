import flet as ft
from core.theme import AppColors
from core.state import state, Anime


def build_anime_detail_view(
    page_obj: ft.Page,
    anime_session: str,
    on_load_episodes: callable,
    on_play: callable,
) -> ft.View:
    anime = next((a for a in state.search_results if a.session == anime_session), None)

    title_text = ft.Text(
        anime.title if anime else "Loading...",
        size=22,
        weight=ft.FontWeight.BOLD,
        color=AppColors.DARK_TEXT,
    )

    info_text = ft.Text(
        "",
        size=12,
        color=AppColors.DARK_TEXT_DIM,
    )

    if anime:
        info_text.value = f"{anime.year} \u00b7 {anime.type} \u00b7 {anime.status} \u00b7 {anime.episodes} eps \u00b7 {anime.score:.1f}"

    episode_grid = ft.GridView(
        expand=True,
        runs_count=4,
        max_extent=180,
        child_aspect_ratio=1.6,
        spacing=8,
        run_spacing=8,
    )

    def refresh_episodes():
        episode_grid.controls.clear()
        for ep in state.episodes:
            card = _build_episode_card(
                ep,
                lambda e, a=anime_session, es=ep.session: page_obj.run_task(on_play, a, es),
            )
            episode_grid.controls.append(card)
        page_obj.update()

    page_obj.refresh_episodes = refresh_episodes

    poster = ft.Container(
        width=100,
        height=150,
        border_radius=8,
        content=(
            ft.Image(src=anime.poster, fit=ft.ImageFit.COVER, border_radius=8)
            if anime and anime.poster
            else ft.Icon(ft.Icons.MOVIE, size=40, color=AppColors.DARK_TEXT_MUTED)
        ),
    )

    loading = ft.ProgressRing(width=20, height=20, color=AppColors.PRIMARY)

    content = ft.Column(
        [
            ft.Container(
                padding=ft.Padding(20, 20, 20, 0),
                content=ft.Row(
                    [
                        poster,
                        ft.Container(width=16),
                        ft.Column(
                            expand=True,
                            controls=[
                                title_text,
                                ft.Container(height=4),
                                info_text,
                                ft.Container(height=4),
                                loading,
                            ],
                        ),
                    ],
                ),
            ),
            ft.Container(
                padding=ft.Padding(20, 16, 20, 0),
                content=ft.Text(
                    "Episodes",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=AppColors.DARK_TEXT,
                ),
            ),
            ft.Container(
                expand=True,
                padding=ft.Padding(20, 4, 20, 20),
                content=episode_grid,
            ),
        ],
        spacing=0,
        expand=True,
    )

    return ft.View(
        route=f"/anime?session={anime_session}",
        controls=[
            ft.SafeArea(
                ft.Container(content=content, expand=True, bgcolor=AppColors.DARK_BG),
                expand=True,
            ),
        ],
        padding=0,
    )


def _build_episode_card(ep, on_click: callable) -> ft.Container:
    return ft.Container(
        bgcolor=AppColors.DARK_SURFACE,
        border_radius=8,
        ink=True,
        on_click=on_click,
        content=ft.Column(
            spacing=2,
            controls=[
                ft.Container(
                    height=80,
                    bgcolor=AppColors.DARK_SURFACE_VARIANT,
                    border_radius=ft.border_vertical(top=8),
                    alignment=ft.Alignment(0, 0),
                    content=(
                        ft.Image(src=ep.snapshot, fit=ft.ImageFit.COVER)
                        if ep.snapshot
                        else ft.Icon(ft.Icons.PLAY_CIRCLE_OUTLINE, size=32, color=AppColors.DARK_TEXT_MUTED)
                    ),
                ),
                ft.Container(
                    padding=ft.Padding(8, 4, 8, 8),
                    content=ft.Column(
                        spacing=1,
                        controls=[
                            ft.Text(
                                f"Episode {ep.episode}",
                                size=13,
                                color=AppColors.DARK_TEXT,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                ep.duration,
                                size=11,
                                color=AppColors.DARK_TEXT_MUTED,
                            ),
                        ],
                    ),
                ),
            ],
        ),
    )
