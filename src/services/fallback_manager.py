import asyncio
import logging
from typing import Any, Callable, Awaitable

logger = logging.getLogger(__name__)


class FallbackExhausted(Exception):
    def __init__(self, chain_name: str, errors: list[tuple[str, str]]):
        self.chain_name = chain_name
        self.errors = errors
        detail = "; ".join(f"{name}: {err}" for name, err in errors)
        super().__init__(f"Fallback chain '{chain_name}' exhausted: {detail}")


StrategyFn = Callable[..., Awaitable[tuple[Any, bool]]]


class FallbackChain:
    def __init__(self, name: str, strategies: list[StrategyFn]):
        self.name = name
        self.strategies = strategies

    async def execute(self, *args, **kwargs) -> Any:
        errors: list[tuple[str, str]] = []
        for i, strategy in enumerate(self.strategies):
            strategy_name = getattr(strategy, "__name__", f"strategy_{i}")
            try:
                result, success = await strategy(*args, **kwargs)
                if success:
                    logger.info(f"FallbackChain '{self.name}': {strategy_name} succeeded")
                    return result
                errors.append((strategy_name, "returned failure"))
            except Exception as e:
                logger.warning(f"FallbackChain '{self.name}': {strategy_name} failed: {e}")
                errors.append((strategy_name, str(e)))
        raise FallbackExhausted(self.name, errors)


class FallbackManager:
    def __init__(self, scraper, cache):
        self.scraper = scraper
        self.cache = cache

    def _chain(self, name: str, strategies: list[StrategyFn]) -> FallbackChain:
        return FallbackChain(name, strategies)

    async def search(self, query: str, page: int = 1, **kwargs) -> Any:
        chain = self._chain("search", [
            self._search_api,
            self._search_html,
        ])
        return await chain.execute(query, page)

    async def episodes(self, anime_session: str, page: int = 1, **kwargs) -> Any:
        chain = self._chain("episodes", [
            self._episodes_api,
        ])
        return await chain.execute(anime_session, page)

    async def sources(self, anime_session: str, episode_session: str, **kwargs) -> Any:
        chain = self._chain("sources", [
            self._sources_play_page,
        ])
        return await chain.execute(anime_session, episode_session)

    async def _search_api(self, query: str, page: int) -> tuple[Any, bool]:
        results, has_more = self.scraper.search(query, page)
        return (results, has_more), bool(results)

    async def _search_html(self, query: str, page: int) -> tuple[Any, bool]:
        results, has_more = self.scraper._search_from_html(query, page)
        return (results, has_more), bool(results)

    async def _episodes_api(self, anime_session: str, page: int) -> tuple[Any, bool]:
        results, has_more = self.scraper.episodes(anime_session, page)
        return (results, has_more), bool(results)

    async def _sources_play_page(self, anime_session: str, episode_session: str) -> tuple[Any, bool]:
        results = self.scraper.sources(anime_session, episode_session)
        return results, bool(results)
