import flet as ft
from core.state import state, LatestRelease
from core.theme import AppColors


def build_home_view(
    page_obj: ft.Page,
    on_load_latest,
    on_select_anime,
    on_search_click
) -> ft.View:

    latest_grid = ft.GridView(
        expand=True,
        runs_count=5,
        max_extent=200,
        child_aspect_ratio=0.65,
        spacing=16,
        run_spacing=16,
        padding=24,
    )

    def on_hover_card(e, container, image):
        if e.data == "true":
            container.scale = 1.05
            container.shadow = ft.BoxShadow(
                spread_radius=2,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.3, AppColors.PRIMARY),
                offset=ft.Offset(0, 8),
            )
        else:
            container.scale = 1.0
            container.shadow = None
        container.update()

    def build_card(release: LatestRelease):
        # We don't have the anime ID directly as a session sometimes, 
        # but the state allows navigating by anime_session.
        # Latest releases usually have an anime_session.
        
        img = ft.Image(
            src=release.snapshot,
            fit="cover",
            expand=True,
        )
        
        gradient = ft.Container(
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,
                end=ft.Alignment.BOTTOM_CENTER,
                colors=[
                    ft.Colors.TRANSPARENT,
                    ft.Colors.with_opacity(0.8, ft.Colors.BLACK),
                ],
            ),
            expand=True,
        )

        title_text = ft.Text(
            release.anime_title,
            color=ft.Colors.WHITE,
            weight=ft.FontWeight.BOLD,
            size=14,
            max_lines=2,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

        ep_text = ft.Text(
            f"Ep {release.episode}",
            color=AppColors.PRIMARY,
            weight=ft.FontWeight.BOLD,
            size=12,
        )

        content = ft.Stack(
            controls=[
                img,
                gradient,
                ft.Container(
                    padding=12,
                    alignment=ft.Alignment.BOTTOM_LEFT,
                    content=ft.Column(
                        [title_text, ep_text],
                        alignment=ft.MainAxisAlignment.END,
                        spacing=4,
                    )
                )
            ],
            expand=True,
        )

        card_container = ft.Container(
            content=content,
            border_radius=12,
            clip_behavior="antiAlias",
            animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            on_click=lambda _: on_select_anime(release.anime_session),
            on_hover=lambda e: on_hover_card(e, card_container, img),
        )

        return card_container

    def update_grid():
        latest_grid.controls.clear()
        for r in state.latest_releases:
            latest_grid.controls.append(build_card(r))
        
        # Check if loading
        if state.is_loading and not state.latest_releases:
            content.controls = [
                header,
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                    content=ft.ProgressRing(color=AppColors.PRIMARY, stroke_width=4)
                )
            ]
        else:
            content.controls = [header, latest_grid]
        
        page_obj.update()

    def handle_theme_toggle(e):
        page_obj.theme_mode = ft.ThemeMode.LIGHT if page_obj.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        page_obj.update()

    header = ft.Container(
        padding=ft.Padding.only(left=24, right=24, top=24, bottom=8),
        content=ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Image(src="icon.png", width=32, height=32, fit="contain"),
                        ft.Text("AnimePahe TV", size=24, weight=ft.FontWeight.BOLD),
                    ],
                    spacing=12,
                ),
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.SEARCH_ROUNDED,
                            icon_color=ft.Colors.ON_SURFACE,
                            on_click=lambda _: on_search_click(),
                            tooltip="Search Anime",
                        ),
                        ft.IconButton(
                            icon=ft.Icons.LIGHT_MODE_ROUNDED if page_obj.theme_mode == ft.ThemeMode.DARK else ft.Icons.DARK_MODE_ROUNDED,
                            icon_color=ft.Colors.ON_SURFACE,
                            on_click=handle_theme_toggle,
                            tooltip="Toggle Theme",
                        ),
                    ],
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
    )

    content = ft.Column(
        controls=[header, latest_grid],
        expand=True,
        spacing=0,
    )

    view = ft.View(
        route="/home",
        controls=[content],
        padding=0,
        bgcolor=ft.Colors.SURFACE,
    )

    # Initial load trigger (run once)
    if not state.latest_releases and not state.is_loading:
        page_obj.run_task(on_load_latest)

    page_obj.update_home_grid = update_grid
    update_grid()

    return view
