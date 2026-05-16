import flet as ft
from dataclasses import dataclass


@dataclass
class Anime:
    id: int
    title: str
    type: str
    episodes: int
    status: str
    season: str
    year: int
    score: float
    poster: str
    session: str


@dataclass
class Episode:
    id: int
    anime_id: int
    episode: int
    title: str
    snapshot: str
    disc: str
    audio: str
    duration: str
    session: str
    filler: bool


@dataclass
class Source:
    url: str
    resolution: int
    audio: str
    fansub: str


@ft.observable
class AppState:
    is_loading: bool = False
    search_query: str = ""
    search_results: list[Anime] = []
    search_has_more: bool = True
    episodes: list[Episode] = []
    episodes_has_more: bool = True
    selected_source: Source | None = None
    m3u8_url: str | None = None
    player_error: str | None = None

    def __init__(self):
        self.search_results = []
        self.episodes = []


state = AppState()
