import flet as ft
from flet_video import Video, VideoConfiguration
from core.theme import AppTheme
from services.kwik_resolver import KwikResolver


class PlayerView:
    def __init__(self, app):
        self.app = app
        self.theme = AppTheme()
        self.kwik = KwikResolver()
        self._video: Video | None = None
        self._status_text: ft.Text | None = None

    def build(self) -> ft.View:
        self._status_text = ft.Text("Loading...", color=self.theme.text_secondary)
        self._video = Video(
            autoplay=True,
            aspect_ratio=16 / 9,
            on_error=self._on_error,
            on_ended=self._on_ended,
        )

        return ft.View(
            bgcolor="#000000",
            controls=[
                ft.Container(
                    expand=True,
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            self._video,
                            self._status_text,
                        ],
                    ),
                ),
            ],
        )

    def load_sources(self):
        anime = self.app.state.selected_anime.get()
        episode = self.app.state.selected_episode.get()
        if not anime or not episode:
            self._status_text.value = "Error: No episode selected"
            self.app.page.update()
            return

        sources = self.app.scraper.sources(anime.session, episode.session)
        self.app.state.sources.set(sources)

        if not sources:
            self._status_text.value = "No sources found"
            self.app.page.update()
            return

        self._status_text.value = "Resolving stream..."
        self.app.page.update()

        best = sources[0]
        for s in sources:
            if s.resolution > best.resolution:
                best = s

        self.app.state.selected_source.set(best)
        m3u8 = self.kwik.resolve(best.url)

        if m3u8:
            self.app.state.m3u8_url.set(m3u8)
            self._video.source = m3u8
            self._video.player_config = VideoConfiguration(
                mpv_properties={
                    "http-header-fields": f"Referer: {best.url}",
                },
            )
            self._status_text.value = f"Playing {best.resolution}p"
        else:
            self._status_text.value = "Failed to resolve stream"

        self.app.page.update()

    def _on_error(self, e):
        self._status_text.value = f"Playback error: {e.data}"
        self.app.page.update()

    def _on_ended(self, e):
        self._status_text.value = "Playback ended"
        self.app.page.update()
