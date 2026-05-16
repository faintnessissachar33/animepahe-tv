import flet as ft
from core.theme import AppColors
from core.state import state


def build_anime_detail_view(
    page_obj: ft.Page,
    anime_session: str,
    on_load_episodes: callable,
    on_play: callable,
) -> ft.View:
    # Try to find anime in search results or latest releases
    anime = next((a for a in state.search_results if a.session == anime_session), None)
    if not anime:
        # Fallback to latest_releases if we navigated from Home
        lr = next((a for a in state.latest_releases if a.anime_session == anime_session), None)
        if lr:
            # Create a mock anime object from latest release
            from core.state import Anime
            anime = Anime(
                id=lr.anime_id,
                title=lr.anime_title,
                type="",
                episodes=0,
                status="",
                season="",
                year=0,
                score=0.0,
                poster=lr.snapshot, # Use snapshot as poster fallback
                session=lr.anime_session,
            )

    def on_back(e):
        if len(page_obj.views) > 1:
            page_obj.views.pop()
            page_obj.update()

    # Blurred background
    bg_image_url = anime.poster if anime and anime.poster else ""

    bg_container = ft.Stack(
        expand=True,
        controls=[
            ft.Image(
                src=bg_image_url,
                fit="cover",
                expand=True,
                opacity=0.3,
            ),
            ft.Container(
                expand=True,
                bgcolor=ft.Colors.with_opacity(0.85, ft.Colors.SURFACE),
            ),
        ],
    )

    bg_overlay = ft.Container(expand=True, bgcolor=ft.Colors.TRANSPARENT)

    title_text = ft.Text(
        anime.title if anime else "Loading...",
        size=36,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.ON_SURFACE,
        max_lines=2,
        overflow=ft.TextOverflow.ELLIPSIS,
    )

    info_text = ft.Text(
        "",
        size=14,
        color=ft.Colors.ON_SURFACE_VARIANT,
        weight=ft.FontWeight.W_500,
    )

    if anime:
        parts = []
        if anime.year:
            parts.append(str(anime.year))
        if anime.type:
            parts.append(anime.type)
        if anime.status:
            parts.append(anime.status)
        if anime.episodes:
            parts.append(f"{anime.episodes} Episodes")
        if anime.score:
            parts.append(f"\u2605 {anime.score:.1f}")
        info_text.value = " \u2022 ".join(parts)

    episode_grid = ft.GridView(
        expand=True,
        runs_count=3,
        max_extent=250,
        child_aspect_ratio=1.6,
        spacing=16,
        run_spacing=16,
    )

    loading_indicator = ft.Container(
        alignment=ft.Alignment.CENTER,
        content=ft.ProgressRing(color=AppColors.PRIMARY, stroke_width=4),
        visible=False,
    )

    def on_hover_ep(e, container, icon):
        if e.data == "true":
            container.bgcolor = ft.Colors.with_opacity(0.2, AppColors.PRIMARY)
            container.scale = 1.02
            icon.color = AppColors.PRIMARY
        else:
            container.bgcolor = AppColors.get_glass_bg(page_obj)
            container.scale = 1.0
            icon.color = ft.Colors.WHITE
        container.update()
        icon.update()

    def _build_episode_card(ep) -> ft.Container:
        play_icon = ft.Icon(ft.Icons.PLAY_CIRCLE_FILL_ROUNDED, size=40, color=ft.Colors.WHITE)
        
        img = ft.Image(
            src=ep.snapshot if ep.snapshot else "",
            fit="cover",
            expand=True,
        )

        gradient = ft.Container(
            gradient=ft.LinearGradient(
                begin=ft.Alignment.CENTER_LEFT,
                end=ft.Alignment.CENTER_RIGHT,
                colors=[
                    ft.Colors.with_opacity(0.8, ft.Colors.BLACK),
                    ft.Colors.TRANSPARENT,
                ],
            ),
            expand=True,
        )

        ep_text = ft.Text(
            f"Episode {ep.episode}",
            color=ft.Colors.WHITE,
            weight=ft.FontWeight.BOLD,
            size=16,
        )

        duration_text = ft.Text(
            ep.duration if ep.duration else "24m",
            color=ft.Colors.WHITE_70,
            size=12,
        )

        content = ft.Stack(
            controls=[
                img,
                gradient,
                ft.Container(
                    padding=16,
                    alignment=ft.Alignment.CENTER_LEFT,
                    content=ft.Column(
                        [ep_text, duration_text],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=4,
                    )
                ),
                ft.Container(
                    alignment=ft.Alignment.CENTER_RIGHT,
                    padding=16,
                    content=play_icon,
                )
            ],
            expand=True,
        )

        card_container = ft.Container(
            content=content,
            border_radius=12,
            clip_behavior="antiAlias",
            bgcolor=AppColors.get_glass_bg(page_obj),
            animate_scale=300,
            animate=300,
            on_click=lambda _, a=anime_session, es=ep.session: page_obj.run_task(on_play, a, es),
            on_hover=lambda e: on_hover_ep(e, card_container, play_icon),
        )
        return card_container

    def refresh_episodes():
        episode_grid.controls.clear()
        if state.is_loading:
            loading_indicator.visible = True
        else:
            loading_indicator.visible = False
            for ep in state.episodes:
                episode_grid.controls.append(_build_episode_card(ep))
        page_obj.update()

    page_obj.refresh_episodes = refresh_episodes

    poster = ft.Container(
        width=200,
        height=300,
        border_radius=16,
        shadow=ft.BoxShadow(
            spread_radius=2,
            blur_radius=20,
            color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
            offset=ft.Offset(0, 10),
        ),
        content=(
            ft.Image(src=anime.poster, fit="cover", border_radius=16)
            if anime and anime.poster
            else ft.Container(
                content=ft.Icon(ft.Icons.MOVIE_ROUNDED, size=64, color=ft.Colors.ON_SURFACE_VARIANT),
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE),
                border_radius=16,
                alignment=ft.Alignment.CENTER,
            )
        ),
    )

    header = ft.Container(
        padding=ft.Padding.all(32),
        content=ft.Row(
            [
                poster,
                ft.Container(width=32),
                ft.Column(
                    expand=True,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED,
                            icon_color=ft.Colors.ON_SURFACE,
                            on_click=on_back,
                            tooltip="Back",
                        ),
                        ft.Container(height=16),
                        title_text,
                        ft.Container(height=8),
                        info_text,
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
    )

    content = ft.Stack(
        [
            bg_container,
            bg_overlay,
            ft.Column(
                [
                    header,
                    ft.Container(
                        padding=ft.Padding.only(left=32, right=32, bottom=16),
                        content=ft.Text(
                            "Episodes",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ON_SURFACE,
                        ),
                    ),
                    ft.Container(
                        expand=True,
                        padding=ft.Padding.only(left=32, right=32, bottom=32),
                        content=ft.Stack([episode_grid, loading_indicator]),
                    ),
                ],
                spacing=0,
                expand=True,
            ),
        ],
        expand=True,
    )

    view = ft.View(
        route=f"/anime?session={anime_session}",
        controls=[content],
        padding=0,
    )

    refresh_episodes()

    return view
