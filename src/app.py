import flet as ft
from core.theme import AppTheme
from core.state import AppState
from core.focus_manager import FocusManager
from services.animepahe import AnimePaheScraper
from services.fallback_manager import FallbackManager
from services.cache import Cache
from views.splash import SplashView
from views.search import SearchView
from views.anime_detail import AnimeDetailView
from views.player import PlayerView


class AnimePaheTV:
    def __init__(self, page: ft.Page):
        self.page = page
        self.state = AppState()
        self.theme = AppTheme()
        self.focus = FocusManager(page)
        self.cache = Cache()
        self.scraper = AnimePaheScraper()
        self.fallback = FallbackManager(self.scraper, self.cache)
        self._configure_page()
        self._init_views()
        self._show_splash()

    def _configure_page(self):
        self.page.title = "AnimePahe TV"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.spacing = 0
        self.page.bgcolor = self.theme.bg_primary
        self.page.on_keyboard_event = self.focus.handle_key

    def _init_views(self):
        self.splash_view = SplashView(self)
        self.search_view = SearchView(self)
        self.detail_view = AnimeDetailView(self)
        self.player_view = PlayerView(self)

    def _show_splash(self):
        self.page.controls.clear()
        self.page.add(self.splash_view.build())

    def show_search(self):
        self.page.controls.clear()
        self.page.add(self.search_view.build())

    def show_detail(self, anime):
        self.state.selected_anime.set(anime)
        self.page.controls.clear()
        self.page.add(self.detail_view.build())
        self.detail_view.load_episodes()

    def show_player(self, episode):
        self.state.selected_episode.set(episode)
        self.page.controls.clear()
        self.page.add(self.player_view.build())
        self.player_view.load_sources()
