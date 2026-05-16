# AnimePahe TV

[![Python](https://img.shields.io/badge/python-3.13%2B-blue)](https://www.python.org/)
[![Flet](https://img.shields.io/badge/flet-0.85.0-blue)](https://flet.dev/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A lightweight, client-side Android TV / mobile / desktop app for browsing and streaming anime from AnimePahe. Zero server infrastructure — runs entirely on-device using Flet (Flutter under the hood).

> **Philosophy**: No server. No proxy. No cloudscraper. No WebView. Pure client-side Python, with waterflow fallback chains at every layer so the app adapts when upstream changes.

---

## Table of Contents

- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Waterflow Fallback System](#waterflow-fallback-system)
- [Component Deep-Dive](#component-deep-dive)
  - [DDoS-Guard Solver](#1-ddos-guard-solver)
  - [AnimePahe Scraper](#2-animepahe-scraper)
  - [Kwik M3U8 Resolver](#3-kwik-m3u8-resolver)
  - [Fallback Manager](#4-fallback-manager)
  - [Caching Layer](#5-caching-layer)
  - [State Management](#6-state-management)
  - [Focus Manager (D-Pad)](#7-focus-manager-d-pad)
  - [Player (flet-video)](#8-player-flet-video)
- [Views](#views)
  - [Splash](#splash)
  - [Search / Browse](#search--browse)
  - [Anime Detail](#anime-detail)
  - [Player](#player)
- [Platform-Specific Notes](#platform-specific-notes)
  - [Android TV](#android-tv)
  - [Android Phone / Tablet](#android-phone--tablet)
  - [Windows](#windows)
- [Build & Deploy](#build--deploy)
- [Development](#development)
- [FAQ / Troubleshooting](#faq--troubleshooting)

---

## Features

- **Search** anime by title (keyword search via AnimePahe API)
- **Browse** paginated results
- **Episode grid** with snapshot previews
- **Multi-quality** playback: 360p / 720p / 1080p (when available)
- **Audio track selection** (Japanese / English)
- **D-Pad navigation** for Android TV remotes (ported from KTV Player)
- **Responsive layout** — adapts to TV, phone, tablet, and desktop
- **Waterflow fallbacks** — auto-healing at every layer when upstream changes
- **Caching** — episode lists and resolved M3U8 URLs cached locally (aiosqlite)
- **No ads** — clean, minimal UI

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    Views Layer                       │
│  Splash → Search → AnimeDetail → Player             │
└──────────────┬──────────────────────────┬───────────┘
               │                          │
               ▼                          ▼
┌──────────────────────┐    ┌─────────────────────────┐
│   State Management    │    │    Focus Manager         │
│   (Listenable/Mutable)│    │    (D-Pad navigation)    │
└──────────┬───────────┘    └─────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│                  Services Layer                       │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐                 │
│  │  DDoSSolver  │  │  KwikResolver │                 │
│  └──────┬───────┘  └──────┬───────┘                 │
│         │                 │                          │
│         ▼                 ▼                          │
│  ┌──────────────────────────────────┐               │
│  │       AnimePahe Scraper          │               │
│  │  (search / episodes / sources)   │               │
│  └──────────────┬───────────────────┘               │
│                 │                                    │
│                 ▼                                    │
│  ┌──────────────────────────────────┐               │
│  │       Fallback Manager           │               │
│  │  (tries alternatives on failure) │               │
│  └──────────────┬───────────────────┘               │
│                 │                                    │
│                 ▼                                    │
│  ┌──────────────────────────────────┐               │
│  │       Cache Layer (aiosqlite)    │               │
│  └──────────────────────────────────┘               │
└──────────────────────────────────────────────────────┘
```

### Data Flow

```
Search query → Scraper.search() → FallbackManager tries API → Cache lookup → Return results
Select anime → Scraper.episodes() → FallbackManager tries API/HTML → Cache → Return episode list
Select episode → Scraper.sources() → Parse play page → Extract Kwik URLs → Cache
Play episode → KwikResolver.resolve() → Fetch Kwik page → Unpack JS → Extract M3U8 → Play in flet-video
```

---

## Waterflow Fallback System

Every operation has a **fallback chain**. If the primary strategy fails (HTTP error, parsing error, empty result), the next strategy is tried automatically. This makes the app resilient to upstream changes.

### Fallback Chaining Pattern

```
Result = try Strategy A (primary)
       │ failure? → try Strategy B
       │ failure? → try Strategy C
       │ failure? → raise FallbackExhausted(error_log)
       └ success  → return Result + cache it
```

### Each Layer's Fallback Chain

#### 1. Domain Resolution
```
primary:   animepahe.pw
fallback:  animepahe.si
fallback:  animepahe.com
fallback:  api.animepahe.pw
trigger:   DNS failure or HTTP 404/5xx
```

#### 2. DDoS-Guard Bypass
```
primary:   GET "/" → extract __ddgid_ → GET "/.well-known/ddos-guard/id/{id}" → cookie set
fallback:  Retry #1 with fresh headers (rotate User-Agent)
fallback:  Retry #2 after 2s delay
fallback:  Retry #3 with different Accept header
trigger:   HTTP 403 response
timeout:   15s per attempt, 3 attempts max
```

#### 3. Search
```
primary:   GET /api?m=search&q={query} → parse JSON
fallback:  GET /?search={query} → parse HTML result page
fallback:  GET /anime?q={query} → alternative search endpoint
trigger:   Non-200 or empty data array
```

#### 4. Episodes List
```
primary:   GET /api?m=release&id={anime_session}&page={n} → parse JSON
fallback:  Extract embedded JSON from anime page HTML
fallback:  Parse HTML episode table directly
trigger:   Non-200 or empty data array
```

#### 5. Sources (Play Page)
```
primary:   GET /play/{anime_session}/{episode_session} → extract Kwik URLs from data-src
fallback:  Regex scrape Kwik URLs from entire page HTML
fallback:  Try alternative URL patterns (kwik.cx, kwik.si, etc.)
trigger:   Empty source list
```

#### 6. Kwik M3U8 Resolution
```
primary:   Dean Edwards JS unpacker → extract M3U8 from unpacked code
fallback:  Direct M3U8 regex scan on Kwik page (for pages that embed URL directly)
fallback:  Regex scan for variable assignments containing M3U8
fallback:  Try alternative kwik domain mirror
trigger:   No M3U8 extracted or M3U8 returns 403/404
```

#### 7. M3U8 Streaming
```
primary:   flet-video with Referer header via mpv_properties (http-header-fields)
fallback:  flet-video with no custom headers but same UA
fallback:  flet-video with Origin header set
trigger:   Video fails to load (player.on_error)
```

### Error Logging & Diagnostics

Each fallback chain logs:
- Which strategy was attempted
- HTTP status code (if applicable)
- Error type (parse error, network error, empty result)
- Response size (to detect redirects vs actual content)
- Full error details in debug mode

This log is available in the app's debug overlay (triple-tap on TV remote or shake on phone).

---

## Component Deep-Dive

### 1. DDoS-Guard Solver

**File**: `src/services/ddos_solver.py`

AnimePahe uses **DDoS-Guard** (not Cloudflare). The challenge is a 2-step HTTP handshake:

1. **GET** `https://animepahe.pw/` → receives `__ddgid_{uuid}` cookie, `__ddg1_{challenge}` cookie
2. **GET** `https://animepahe.pw/.well-known/ddos-guard/id/{__ddgid_}` → server returns a 1×1 PNG, sets `__ddg2_{answer}` cookie
3. **Retry** original request → `__ddg2_` cookie verifies client as human, request succeeds

**No JavaScript execution needed.** The "challenge" appears to be a simple image-based test (returning a tiny PNG). The `__ddg2_` cookie value is the response to the challenge ID — and it's simply set by the server, no client computation required.

```python
class DDoSSolver:
    def __init__(self):
        self.client = httpx.Client(timeout=15.0, follow_redirects=True)
        self._solved = False

    def solve(self):
        resp = self.client.get(f"{BASE}/")
        ddgid = self.client.cookies.get("__ddgid_")
        if ddgid:
            self.client.get(f"{BASE}/.well-known/ddos-guard/id/{ddgid}")
            self._solved = True
```

**Why it works on Android**: Pure httpx, no WebView, no JS engine, no cloudscraper. Compatible with `httpx` on Android via Flet's Python runtime.

**Fallback**: If `__ddgid_` is missing (unusual challenge variant), retry with different User-Agent and Accept headers.

### 2. AnimePahe Scraper

**File**: `src/services/animepahe.py`

Core scraper implementing all API interactions. Uses `httpx.AsyncClient` for non-blocking I/O.

#### Methods

| Method | Input | Output | Endpoint |
|--------|-------|--------|----------|
| `search(query, page)` | `query: str`, `page: int` | `SearchResult[]` | `GET /api?m=search&q={q}&page={p}` |
| `episodes(anime_id, page)` | `anime_id: str` (session) | `Episode[]` | `GET /api?m=release&id={id}&page={p}&sort=episode_asc` |
| `sources(anime_id, episode_id)` | both session IDs | `Source[]` | `GET /play/{anime_id}/{episode_id}` |
| `anime_info(anime_id)` | session ID | `AnimeDetail` | `GET /anime/{session}` |

#### Data Models

```python
@dataclass
class Anime:
    id: int
    title: str
    type: str           # "TV", "Movie", "OVA", "Special"
    episodes: int
    status: str
    season: str
    year: int
    score: float
    poster: str
    session: str        # UUID (primary identifier)

@dataclass
class Episode:
    id: int
    anime_id: int
    episode: int
    title: str
    snapshot: str       # thumbnail URL
    disc: str           # "BD" or "WEB"
    audio: str          # "jpn", "eng"
    duration: str
    session: str        # UUID
    filler: bool

@dataclass  
class Source:
    url: str            # Kwik URL
    resolution: int     # 360, 720, 800, 1080
    audio: str          # "jpn", "eng"
    fansub: str         # fansub group name
```

### 3. Kwik M3U8 Resolver

**File**: `src/services/kwik_resolver.py`

Extracts M3U8 video URLs from Kwik's JS-packed pages. Kwik uses **Dean Edwards P.A.C.K.E.R.** (not JavaScript obfuscation — it's a string compression scheme).

```python
class KwikResolver:
    async def resolve(self, kwik_url: str, referer: str = None) -> str | None:
        """Fetch Kwik page, unpack Dean Edwards JS, extract M3U8 URL."""
        
    def _dean_unpack(self, source: str) -> list[str]:
        """Unpack all Dean Edwards scripts in HTML and return M3U8 URLs."""
```

#### Unpacking Algorithm

```
Input: HTML page containing:
  eval(function(p,a,c,k,e,d){e=function(c){...}})
  ('base62_payload',62,112,'symtab|entries|...'.split('|'),0,{})

Step 1: Extract via regex:
  → payload   = "j q='1N://1M...' ..." (base62 encoded word references)
  → radix     = 62
  → count     = 112
  → symtab    = ["m3u8", "uwu", "b92a...", ..., "vault", "https"]

Step 2: Replace each base62-encoded word in payload with symtab entry:
  1N → "https"  (1N in base62 = 1049 → symtab[1049 % 112])
  1M → "vault"  (...
  "j q='" + https + "://" + vault + "-" + ... + ".m3u8" + "';"

Step 3: Extract M3U8 URL via regex from unpacked JS:
  https?://[^'"\s<>]+\.m3u8

Step 4: Verify M3U8 is accessible (HEAD request with Referer)
```

#### Why Custom Unpacker?

The `jsbeautifier.unpackers.packer` module sometimes fails with "list index out of range" because it expects exactly `count` entries in the symtab, but some variants have slightly different structure. Our custom implementation is:
- More lenient (ignores count mismatch)
- Extracts ALL eval blocks (not just first)
- Returns ALL M3U8 URLs found
- Pure Python, no subprocess, no Node.js, no npm

### 4. Fallback Manager

**File**: `src/services/fallback_manager.py`

Orchestrates the fallback chains. Uses a generic `FallbackChain` class:

```python
class FallbackChain:
    def __init__(self, name: str, strategies: list[Callable], 
                 validator: Callable[[Any], bool] | None = None):
        ...
    
    async def execute(self, *args, **kwargs) -> tuple[Any, int]:
        """
        Try each strategy in sequence.
        Returns (result, strategy_index).
        strategy_index = -1 means all failed.
        """

class FallbackManager:
    def __init__(self, ddos_solver: DDoSSolver, scraper: AnimePaheScraper, 
                 kwik_resolver: KwikResolver, cache: Cache):
        self.chains = {
            'search': FallbackChain('search', [
                self._search_api,
                self._search_html_page,
            ]),
            'episodes': FallbackChain('episodes', [
                self._episodes_api,
                self._episodes_from_anime_page,
            ]),
            'sources': FallbackChain('sources', [
                self._sources_play_page,
            ]),
            'kwik_resolve': FallbackChain('kwik_resolve', [
                self._kwik_dean_unpack,
                self._kwik_direct_m3u8,
            ]),
        }
    
    async def execute(self, chain_name: str, *args, **kwargs):
        """Execute a named fallback chain."""
```

### 5. Caching Layer

**File**: `src/services/cache.py`

Uses `aiosqlite` (same as KTV Player). Caches:

| Cache Key | Value | TTL |
|-----------|-------|-----|
| `search:{query}:{page}` | JSON response | 1 hour |
| `episodes:{anime_id}:{page}` | Episode list | 1 hour |
| `sources:{anime_id}:{ep_id}` | Source list | 6 hours |
| `kwik:{kwik_url}` | M3U8 URL | 12 hours |
| `anime:{anime_id}` | Anime info | 24 hours |

```python
class Cache:
    def __init__(self, db_path: str = "animepahe.db"):
        self.db_path = db_path
    
    async def get(self, key: str) -> Any | None: ...
    async def set(self, key: str, value: Any, ttl: int = 3600): ...
    async def invalidate(self, pattern: str): ...
    async def clear(self): ...
```

### 6. State Management

**File**: `src/core/state.py`

Port of KTV Player's state pattern. Uses `flet.Listenable` and mutable state objects.

```python
class AppState:
    def __init__(self):
        self.search_query = MutableState("")
        self.search_results = MutableState([])
        self.search_page = MutableState(1)
        self.selected_anime = MutableState[Anime | None](None)
        self.episodes = MutableState([])
        self.episodes_page = MutableState(1)
        self.selected_episode = MutableState[Episode | None](None)
        self.sources = MutableState([])
        self.selected_source = MutableState[Source | None](None)
        self.m3u8_url = MutableState[str | None](None)
        self.player_state = MutableState("idle")  # idle/loading/playing/paused/error
        self.error_message = MutableState[str | None](None)
        self.navigation_stack = MutableState([])
```

### 7. Focus Manager (D-Pad)

**File**: `src/core/focus_manager.py`

Direct port from KTV Player. Enables full D-Pad navigation on Android TV:

```
Directional keys (↑↓←→) → move focus to adjacent control
OK/Enter → activate selected control
Back → navigate back
Media keys → play/pause/seek/volume
```

Works via `page.on_keyboard_event`. Focus indicators use animated scaling + border glow on focused element. Implements focus trapping within modal overlays.

### 8. Player (flet-video)

**File**: `src/components/player/player_view.py` / `src/views/player.py`

Uses `flet_video.Video` with these configurations:

```python
Video(
    source=m3u8_url,
    autoplay=True,
    aspect_ratio=16/9,
    player_config=VideoConfiguration(
        mpv_properties={
            "http-header-fields": f"Referer: {kwik_url}",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
    ),
    on_error=handle_error,
    on_ended=handle_ended,
    on_time_update=handle_time_update,
)
```

**Why no proxy needed**: M3U8 URLs from Kwik are directly accessible as long as the `Referer` header is set to the Kwik page URL. flet-video (via libmpv) supports custom HTTP headers through `mpv_properties`.

**Controls**: Time slider, play/pause, skip forward/back, quality switcher, audio track switcher (if available), fullscreen toggle.

---

## Views

### Splash

- **File**: `src/views/splash.py`
- Shows app logo + loading indicator
- Pre-warms DDoS-Guard session in background
- Auto-transitions to Search after session ready (or user can tap to skip)
- If DDoS-Guard fails → shows retry button with error message
- Timer: max 10s wait, then show "Tap to retry"

### Search / Browse

- **File**: `src/views/search.py`
- **TV layout**: Full-width search bar at top, results as horizontal scrollable rows
- **Mobile layout**: Search bar at top, results as vertical scrollable cards
- Each result card: poster image + title + year + type + score
- Focus highlight on currently selected card
- Page navigation (next/previous)
- Pull-to-refresh on mobile
- Predictive caching: pre-fetch next page of results

### Anime Detail

- **File**: `src/views/anime_detail.py`
- **TV layout**: Large poster left, info right (title, year, season, score, status, type), episode grid below
- **Mobile layout**: Poster as hero image, info overlay, episode list
- Episode cards show: episode number, title, snapshot thumbnail, duration
- Focus/D-pad navigation on episode grid
- Paginated episode list with "Load more"
- Filler episodes marked with distinct styling

### Player

- **File**: `src/views/player.py`
- Full-screen video playback
- **TV**: Overlay controls accessible via D-pad (play/pause, seek, quality/audio selector)
- **Mobile**: Touch overlay controls
- Quality selector (if multiple sources available)
- Audio language selector
- Show/hide controls on tap (touch) or any key (TV)
- Remember last playback position per episode

---

## Platform-Specific Notes

### Android TV

- **Leanback support**: `android.software.leanback = true`, `android.hardware.touchscreen = false` in manifest
- **D-Pad navigation**: Focus manager handles all directional input
- **Overscan**: Safe margins for TV screens
- **Wake lock**: `WAKE_LOCK` permission to prevent sleep during playback
- **Keyboard shortcuts**: Media keys (play/pause/ffwd/rwd/stop) mapped
- **Recommendations**: Channels/Recommendations via Android TV API (future)

### Android Phone / Tablet

- **Touch interface**: Tap to play, tap to show controls
- **Responsive layout**: Portrait = vertical scroll, Landscape = horizontal grid
- **Back gesture**: Back button navigates view stack
- **Picture-in-Picture**: flet-video supports PiP (via `page.picture_in_picture_allowed`)
- **Rotation lock**: Landscape locked during playback

### Windows

- **Keyboard shortcuts**: Space=play/pause, ←→=seek, ↑↓=volume, F=fullscreen
- **Window management**: Remembers window size/position
- **DirectPlay**: Uses system codecs via libmpv

---

## Build & Deploy

### Prerequisites

- Python 3.13+
- `uv` (package manager) — `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Flet SDK: `uv tool install flet`

### Local Development

```bash
# Clone & setup
git clone https://github.com/yourusername/animepahe-tv.git
cd animepahe-tv
uv sync

# Run desktop version
flet run src/main.py

# Run in browser
flet run --web src/main.py
```

### Build APK for Android

```bash
flet build apk
```

This produces `build/apk/animepahe_tv.apk`. The `pyproject.toml` configures:
- Bundle ID: `com.animepahe.tv`
- Leanback feature (Android TV)
- Touchscreen optional
- Internet permission
- Wake lock permission

### Build AAB for Play Store

```bash
flet build aab
```

### Build Windows

```bash
flet build windows
```

---

## Development

### Setup with uv

```bash
uv sync
uv run flet run src/main.py
```

### Project Dependencies

```
flet==0.85.0
flet-video==0.85.0
httpx>=0.28.1
beautifulsoup4>=4.12.0
aiosqlite>=0.22.1
```

All pure Python with no native dependencies (except flet-video which bundles libmpv).

### Testing

```bash
# Unit tests
uv run pytest tests/

# Test specific fallback chain
uv run pytest tests/test_kwik_resolver.py -v

# End-to-end test
uv run pytest tests/test_e2e.py -v
```

### Code Style

- Type hints everywhere
- `@dataclass` for data models
- `async`/`await` for all I/O
- Follow KTV Player conventions for UI/focus/state patterns

---

## FAQ / Troubleshooting

**Q: Will this get my IP blocked?**  
A: The app makes the same requests as any browser. DDoS-Guard bypass uses the standard challenge-response flow. No aggressive scraping (cached results, paginated requests, rate limiting respected).

**Q: What if AnimePahe changes their API?**  
A: The waterflow fallback system is designed for this. If the API endpoint changes, the HTML parser fallback kicks in. If Kwik changes their packer, the direct M3U8 scan fallback triggers. The app will degrade gracefully rather than break.

**Q: Why flet-video instead of just a WebView?**  
A: WebView on Android TV is problematic (no hardware decoding, poor D-pad support). flet-video uses libmpv which provides hardware-accelerated playback on all platforms.

**Q: Can I add custom sources?**  
A: The architecture supports adding new source resolvers by implementing the `SourceResolver` protocol and registering in `FallbackManager`.

**Q: Does this work on iOS?**  
A: Flet supports iOS, but this app is primarily designed for Android TV and Android mobile. iOS support could be added but is not a priority.

---

## License

MIT

## Disclaimer

This project is for educational purposes only. The developers are not affiliated with AnimePahe or any content providers. Users are responsible for complying with applicable laws and terms of service.
