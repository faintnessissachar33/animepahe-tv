import re
import httpx
from bs4 import BeautifulSoup
from core.state import Anime, Episode, Source
from services.ddos_solver import DDoSSolver


class AnimePaheScraper:
    def __init__(self):
        self.ddos = DDoSSolver()

    @property
    def base(self) -> str:
        return self.ddos.domain

    def _json_get(self, path: str, params: dict | None = None) -> dict | None:
        url = f"{self.base}{path}"
        if params:
            qs = "&".join(f"{k}={v}" for k, v in params.items())
            url = f"{url}?{qs}"
        resp = self.ddos.get(url)
        if resp.status_code != 200:
            return None
        try:
            return resp.json()
        except (ValueError, httpx.DecodingError):
            return None

    def search(self, query: str, page: int = 1) -> tuple[list[Anime], bool]:
        data = self._json_get("/api", {"m": "search", "q": query, "page": page})
        if not data or "data" not in data:
            return self._search_from_html(query, page)
        results = []
        for item in data.get("data", []):
            results.append(Anime(
                id=item.get("id", 0),
                title=item.get("title", ""),
                type=item.get("type", ""),
                episodes=item.get("episodes", 0),
                status=item.get("status", ""),
                season=item.get("season", ""),
                year=item.get("year", 0),
                score=item.get("score", 0.0),
                poster=item.get("poster", ""),
                session=item.get("session", ""),
            ))
        has_more = data.get("current_page", 1) < data.get("last_page", 1)
        return results, has_more

    def _search_from_html(self, query: str, page: int = 1) -> tuple[list[Anime], bool]:
        resp = self.ddos.get(f"{self.base}/?search={query}&page={page}")
        if resp.status_code != 200:
            return [], False
        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        for card in soup.select(".anime-card"):
            results.append(Anime(
                id=0,
                title=card.get("data-title", ""),
                type=card.get("data-type", ""),
                episodes=int(card.get("data-episodes", 0)),
                status=card.get("data-status", ""),
                season=card.get("data-season", ""),
                year=int(card.get("data-year", 0)),
                score=float(card.get("data-score", 0)),
                poster=card.get("data-poster", ""),
                session=card.get("data-session", ""),
            ))
        return results, bool(soup.select(".pagination .next"))

    def episodes(self, anime_session: str, page: int = 1) -> tuple[list[Episode], bool]:
        data = self._json_get("/api", {
            "m": "release",
            "id": anime_session,
            "page": page,
            "sort": "episode_asc",
        })
        if not data or "data" not in data:
            return [], False
        results = []
        for item in data.get("data", []):
            results.append(Episode(
                id=item.get("id", 0),
                anime_id=item.get("anime_id", 0),
                episode=item.get("episode", 0),
                title=item.get("title", ""),
                snapshot=item.get("snapshot", ""),
                disc=item.get("disc", ""),
                audio=item.get("audio", ""),
                duration=item.get("duration", ""),
                session=item.get("session", ""),
                filler=bool(item.get("filler", 0)),
            ))
        has_more = data.get("current_page", 1) < data.get("last_page", 1)
        return results, has_more

    def sources(self, anime_session: str, episode_session: str) -> list[Source]:
        resp = self.ddos.get(f"{self.base}/play/{anime_session}/{episode_session}")
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        sources = []
        for el in soup.select("[data-src]"):
            src = el.get("data-src", "").strip()
            if "kwik" in src.lower():
                sources.append(Source(
                    url=src,
                    resolution=int(el.get("data-resolution", 0) or el.get("data-res", 0) or 0),
                    audio=el.get("data-audio", "") or el.get("data-lang", "jpn"),
                    fansub=el.get("data-fansub", ""),
                ))
        if not sources:
            kwik_urls = re.findall(r'https?://kwik\.[a-z]+/(?:e|f|d)/[A-Za-z0-9_-]+', resp.text)
            for url in kwik_urls:
                sources.append(Source(url=url, resolution=0, audio="jpn", fansub=""))
        return sources

    def anime_info(self, session: str) -> Anime | None:
        data = self._json_get("/api", {"m": "anime", "id": session})
        if data:
            return Anime(
                id=data.get("id", 0),
                title=data.get("title", ""),
                type=data.get("type", ""),
                episodes=data.get("episodes", 0),
                status=data.get("status", ""),
                season=data.get("season", ""),
                year=data.get("year", 0),
                score=data.get("score", 0.0),
                poster=data.get("poster", ""),
                session=session,
            )
        return None

    def close(self):
        self.ddos.close()
