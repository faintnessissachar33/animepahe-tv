import flet as ft
import asyncio
import base64
import urllib.parse

from core.theme import AppTheme, AppColors
from core.state import state
from core.focus_manager import FocusManager
from services.animepahe import AnimePaheScraper
from services.cache import Cache
from views.splash import build_splash_view
from views.search import build_search_view
from views.anime_detail import build_anime_detail_view
from views.player import build_player_view


async def main(page: ft.Page):
    page.title = "AnimePahe TV"
    page.favicon = "icon.png"
    page.padding = 0
    page.spacing = 0

    def global_error_handler(e):
        page.snack_bar = ft.SnackBar(
            ft.Text("Network error or stream unavailable."),
            bgcolor=AppColors.ERROR,
        )
        page.snack_bar.open = True
        page.update()

    page.on_error = global_error_handler

    page.fonts = {
        "Outfit": "https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap"
    }
    page.theme = AppTheme.get_dark_theme()
    page.theme.font_family = "Outfit"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = AppColors.DARK_BG

    scraper = AnimePaheScraper()
    cache = Cache()

    FocusManager(page)

    state.scraper = scraper
    state.cache = cache

    async def navigate(route: str):
        await page.push_route(route)

    async def load_search(query: str):
        state.is_loading = True
        state.search_query = query
        page.update()

        results, has_more = scraper.search(query, 1)
        state.search_results = results
        state.search_has_more = has_more
        state.is_loading = False
        page.update()

    async def load_episodes(anime_session: str):
        state.is_loading = True
        page.update()

        episodes, has_more = scraper.episodes(anime_session, 1)
        state.episodes = episodes
        state.episodes_has_more = has_more
        state.is_loading = False
        page.update()

    async def play_episode(anime_session: str, episode_session: str):
        sources = scraper.sources(anime_session, episode_session)
        if not sources:
            page.snack_bar = ft.SnackBar(ft.Text("No sources found."), bgcolor=AppColors.ERROR)
            page.snack_bar.open = True
            page.update()
            return

        best = max(sources, key=lambda s: s.resolution)
        state.selected_source = best

        encoded_url = base64.urlsafe_b64encode(
            f"{anime_session}|{episode_session}".encode()
        ).decode()
        page.snack_bar = ft.SnackBar(ft.Text("Resolving stream..."), bgcolor=AppColors.SUCCESS)
        page.snack_bar.open = True
        page.update()

        await navigate(f"/play?src={encoded_url}")

    async def splash_complete():
        await asyncio.sleep(1.5)
        await navigate("/search")

    async def route_change(e: ft.RouteChangeEvent | None = None):
        route = page.route
        parsed = urllib.parse.urlparse(route)

        if parsed.path in ["/", "/search"]:
            page.views.clear()

        if parsed.path == "/":
            page.views.append(build_splash_view())
            page.run_task(splash_complete)

        elif parsed.path == "/search":
            page.views.append(
                build_search_view(
                    page_obj=page,
                    on_search=load_search,
                    on_select_anime=lambda a: page.run_task(
                        lambda: navigate(f"/anime?session={a.session}")
                    ),
                )
            )

        elif parsed.path == "/anime":
            params = urllib.parse.parse_qs(parsed.query)
            session = params.get("session", [None])[0]
            if session:
                page.views.append(
                    build_anime_detail_view(
                        page_obj=page,
                        anime_session=session,
                        on_load_episodes=load_episodes,
                        on_play=play_episode,
                    )
                )
                page.run_task(load_episodes, session)

        elif parsed.path == "/play":
            params = urllib.parse.parse_qs(parsed.query)
            encoded = params.get("src", [None])[0]
            if encoded:
                try:
                    padding = "=" * (-len(encoded) % 4)
                    decoded = base64.urlsafe_b64decode(encoded + padding).decode()
                    anime_session, ep_session = decoded.split("|", 1)
                    page.views.append(
                        build_player_view(
                            page_obj=page,
                            anime_session=anime_session,
                            episode_session=ep_session,
                            scraper=scraper,
                        )
                    )
                except Exception:
                    await navigate("/search")

        page.update()

    def view_pop(e: ft.ViewPopEvent):
        if len(page.views) > 1:
            page.views.pop()
            page.update()

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    await route_change()


if __name__ == "__main__":
    ft.run(main)
