from dataclasses import dataclass, field
from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T")


class MutableState(Generic[T]):
    def __init__(self, default: T):
        self._value = default
        self._listeners: list[Callable[[T], None]] = []

    def get(self) -> T:
        return self._value

    def set(self, value: T):
        self._value = value
        for listener in self._listeners:
            listener(value)

    def listen(self, callback: Callable[[T], None]):
        self._listeners.append(callback)


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


class AppState:
    def __init__(self):
        self.search_query = MutableState("")
        self.search_results = MutableState[list[Anime]]([])
        self.search_page = MutableState(1)
        self.search_has_more = MutableState(True)
        self.selected_anime = MutableState[Anime | None](None)
        self.episodes = MutableState[list[Episode]]([])
        self.episodes_page = MutableState(1)
        self.episodes_has_more = MutableState(True)
        self.selected_episode = MutableState[Episode | None](None)
        self.sources = MutableState[list[Source]]([])
        self.selected_source = MutableState[Source | None](None)
        self.m3u8_url = MutableState[str | None](None)
        self.player_status = MutableState("idle")
        self.error = MutableState[str | None](None)
        self.navigation_stack = MutableState[list[str]]([])
