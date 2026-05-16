import flet as ft
from core.theme import AppColors
from core.state import state


def build_search_view(
    page_obj: ft.Page,
    on_search: callable,
    on_select_anime: callable,
    on_back: callable,
) -> ft.View:
    search_field = ft.TextField(
        hint_text="Search for anime...",
        color=ft.Colors.ON_SURFACE,
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.ON_SURFACE),
        border_color=ft.Colors.TRANSPARENT,
        border_radius=16,
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        content_padding=20,
        text_size=16,
        on_submit=lambda e: page_obj.run_task(on_search, e.data.strip()),
        focused_border_color=AppColors.PRIMARY,
        focused_bgcolor=ft.Colors.with_opacity(0.1, AppColors.PRIMARY),
    )

    results_grid = ft.GridView(
        expand=True,
        runs_count=4,
        max_extent=180,
        child_aspect_ratio=0.6,
        spacing=16,
        run_spacing=16,
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

    def _build_card(anime) -> ft.Container:
        img = ft.Image(
            src=anime.poster if anime.poster else "",
            fit="cover",
            expand=True,
        )
        if not anime.poster:
            img = ft.Container(
                content=ft.Icon(ft.Icons.MOVIE_ROUNDED, size=48, color=ft.Colors.ON_SURFACE_VARIANT),
                expand=True,
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE),
                alignment=ft.Alignment.CENTER,
            )

        gradient = ft.Container(
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,
                end=ft.Alignment.BOTTOM_CENTER,
                colors=[
                    ft.Colors.TRANSPARENT,
                    ft.Colors.with_opacity(0.9, ft.Colors.BLACK),
                ],
            ),
            expand=True,
        )

        title_text = ft.Text(
            anime.title,
            color=ft.Colors.WHITE,
            weight=ft.FontWeight.BOLD,
            size=14,
            max_lines=2,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

        year_text = ft.Text(
            str(anime.year) if anime.year else "",
            size=12,
            color=ft.Colors.WHITE_70,
        )
        
        type_text = ft.Text(
            anime.type,
            size=12,
            color=ft.Colors.WHITE_70,
        )

        score_text = ft.Text(
            f"{anime.score:.1f}",
            size=12,
            weight=ft.FontWeight.BOLD,
            color=AppColors.SUCCESS if anime.score >= 7.5 else AppColors.WARNING,
        )

        content = ft.Stack(
            controls=[
                img,
                gradient,
                ft.Container(
                    padding=12,
                    alignment=ft.Alignment.BOTTOM_LEFT,
                    content=ft.Column(
                        [
                            title_text,
                            ft.Row([year_text, ft.Container(expand=True), type_text, score_text], spacing=4),
                        ],
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
            animate_scale=300,
            animate=300,
            on_click=lambda _: on_select_anime(anime),
            on_hover=lambda e: on_hover_card(e, card_container, img),
        )
        return card_container

    def refresh_results():
        results_grid.controls.clear()
        if state.is_loading:
            loading_indicator.visible = True
            empty_state.visible = False
        elif not state.search_results and state.search_query:
            loading_indicator.visible = False
            empty_state.visible = True
            empty_state.controls[1].value = f"No results found for '{state.search_query}'"
        else:
            loading_indicator.visible = False
            empty_state.visible = False
            for anime in state.search_results:
                results_grid.controls.append(_build_card(anime))
        page_obj.update()

    page_obj.refresh_search_results = refresh_results

    loading_indicator = ft.Container(
        expand=True,
        alignment=ft.Alignment.CENTER,
        content=ft.ProgressRing(color=AppColors.PRIMARY, stroke_width=4),
        visible=False,
    )

    empty_state = ft.Column(
        [
            ft.Icon(ft.Icons.SEARCH_OFF_ROUNDED, size=64, color=ft.Colors.ON_SURFACE_VARIANT),
            ft.Text("Search for an anime to get started.", size=16, color=ft.Colors.ON_SURFACE_VARIANT),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        expand=True,
    )

    header = ft.Container(
        padding=ft.Padding.only(left=24, right=24, top=24, bottom=16),
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED,
                            icon_color=ft.Colors.ON_SURFACE,
                            on_click=lambda _: on_back(),
                            tooltip="Back",
                        ),
                        ft.Container(
                            width=36,
                            height=36,
                            border_radius=10,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Image(
                                src="icon.png",
                                width=24,
                                height=24,
                                fit="contain"
                            ),
                        ),
                        ft.Text("Search", size=24, weight=ft.FontWeight.BOLD),
                    ],
                    spacing=12,
                ),
                ft.Container(height=8),
                search_field,
            ],
            spacing=0,
        )
    )

    content = ft.Column(
        [
            header,
            ft.Container(
                expand=True,
                padding=ft.Padding.only(left=24, right=24, bottom=24),
                content=ft.Stack([results_grid, loading_indicator, empty_state]),
            ),
        ],
        spacing=0,
        expand=True,
    )

    view = ft.View(
        route="/search",
        controls=[content],
        padding=0,
        bgcolor=ft.Colors.SURFACE,
    )

    # Initial load trigger
    refresh_results()

    return view
