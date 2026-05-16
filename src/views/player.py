import flet as ft
import flet_video as fv
from core.theme import AppColors
from core.state import state
from services.kwik_resolver import KwikResolver


def build_player_view(
    page_obj: ft.Page,
    anime_session: str,
    episode_session: str,
    scraper,
) -> ft.View:
    kwik = KwikResolver()
    video = fv.Video(
        autoplay=True,
        expand=True,
        aspect_ratio=16 / 9,
        show_controls=True,
        wakelock=True,
        filter_quality=ft.FilterQuality.MEDIUM,
        pause_upon_entering_background_mode=True,
        resume_upon_entering_foreground_mode=True,
        on_error=lambda e: _on_error(e, page_obj),
        on_ended=lambda e: _on_ended(page_obj),
    )

    status_text = ft.Text(
        "Resolving stream...",
        size=14,
        color=AppColors.DARK_TEXT_DIM,
        text_align=ft.TextAlign.CENTER,
    )

    loading = ft.ProgressRing(width=20, height=20, color=AppColors.PRIMARY)

    overlay = ft.Container(
        expand=True,
        bgcolor=ft.Colors.BLACK,
        alignment=ft.Alignment(0, 0),
        content=ft.Column(
            [
                status_text,
                ft.Container(height=12),
                loading,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
    )

    back_btn = ft.Container(
        left=12,
        top=40,
        content=ft.IconButton(
            icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED,
            icon_color=ft.Colors.WHITE,
            icon_size=20,
            bgcolor=ft.Colors.BLACK45,
            on_click=lambda _: page_obj.page.views.pop() if len(page_obj.page.views) > 1 else None,
        ),
    )

    sources = scraper.sources(anime_session, episode_session)
    if sources:
        best = max(sources, key=lambda s: s.resolution)
        m3u8 = kwik.resolve(best.url)
        if m3u8:
            video.playlist = [fv.VideoMedia(m3u8, http_headers={"Referer": best.url})]
            video.autoplay = True
            overlay.visible = False
        else:
            status_text.value = "Failed to resolve stream"
            loading.visible = False
    else:
        status_text.value = "No sources found"
        loading.visible = False

    return ft.View(
        route=f"/play?src={anime_session}|{episode_session}",
        controls=[
            ft.Stack(
                [
                    ft.Container(expand=True, bgcolor=ft.Colors.BLACK),
                    video,
                    overlay,
                    back_btn,
                ],
                expand=True,
            ),
        ],
        padding=0,
    )


def _on_error(e, page_obj: ft.Page):
    state.player_error = e.data
    try:
        page_obj.snack_bar = ft.SnackBar(
            ft.Text(f"Playback error"), bgcolor=AppColors.ERROR,
        )
        page_obj.snack_bar.open = True
        page_obj.update()
    except Exception:
        pass


def _on_ended(page_obj: ft.Page):
    try:
        page_obj.snack_bar = ft.SnackBar(
            ft.Text("Playback ended"), bgcolor=AppColors.SUCCESS,
        )
        page_obj.snack_bar.open = True
        page_obj.update()
    except Exception:
        pass
