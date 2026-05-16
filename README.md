# AnimePahe TV

Lightweight client-side Android TV / mobile / desktop app for browsing and streaming anime from AnimePahe. Zero server infrastructure — pure client-side Python with Flet.

## Features

- **Search** anime by keyword
- **Episode grid** with snapshot previews, pagination
- **Multi-quality** playback (360p / 720p / 800p+ where available)
- **D-Pad navigation** for Android TV remotes
- **Responsive layout** — adapts to TV, phone, tablet, desktop
- **Waterflow fallbacks** — each step has a backup method if primary fails
- **Fast** — lightweight httpx-based scraper, no browser/WebView overhead

## How It Works

AnimePahe TV talks directly to AnimePahe's API and pages — no proxy, no server, no cloudscraper.

```
animepahe.com ──redirect──► animepahe.pw (or .si, etc.) ──DDoS-Guard handshake──► API
```

### Domain Resolution
Uses `https://animepahe.com` with `follow_redirects=True`. The server issues a 302 redirect to whichever domain is live (`.pw`, `.si`, etc.). No domain list needed.

### DDoS-Guard Bypass
Pure httpx — no WebView, no JS engine, no cloudscraper:
1. GET `/` → receives `__ddgid_` cookie
2. GET `/.well-known/ddos-guard/id/{id}` → server sends 1×1 PNG, sets `__ddg2_` cookie
3. Retry original request → verified

### Fallback Methods (Tested)

| Step | Primary | Backup |
|------|---------|--------|
| Search | `/api?m=search&q=` JSON | Parse search results HTML |
| Episodes | `/api?m=release&id=` JSON | Parse anime page HTML |
| Sources | `[data-src]` attributes | Regex Kwik URL scrape |
| Kwik M3U8 | Dean Edwards JS unpack | Direct `.m3u8` regex scan |

### Kwik M3U8 Resolution
Custom Dean Edwards P.A.C.K.E.R. unpacker. Pure Python, no subprocess/Node.js:
1. Extract all `eval(function(p,a,c,k,e,d){...})` blocks from page HTML
2. For each: extract base62-encoded payload, radix, count, and symtab array
3. Replace each base62 word with its symtab entry
4. Regex for `https://...m3u8` in unpacked JS

### Playback
M3U8 URLs served from `uwucdn.top` require `Referer: https://kwik.cx/` header. flet-video (libmpv) sends this via `VideoMedia.http_headers`. No proxy needed.

## Project Structure

```
src/
├── main.py                   # App entry, routing, orchestration
├── core/
│   ├── theme.py              # Dark theme (AppColors, AppTheme)
│   ├── state.py              # @ft.observable AppState + dataclasses
│   └── focus_manager.py      # D-pad navigation (ported from KTV Player)
├── services/
│   ├── ddos_solver.py        # DDoS-Guard 2-step httpx solver
│   ├── animepahe.py          # Scraper with fallback methods
│   ├── kwik_resolver.py      # Dean Edwards unpacker + M3U8 resolver
│   └── cache.py              # aiosqlite cache with TTL
├── views/
│   ├── splash.py             # Logo + loading spinner → auto-navigate
│   ├── search.py             # Search bar + results grid
│   ├── anime_detail.py       # Info panel + episode grid
│   └── player.py             # flet-video playback
└── components/
    ├── ui/glass_container.py  # Focusable container (ported from KTV)
    └── player/immersive_player.py  # Full-screen video player
```

## Development

```bash
git clone https://github.com/Nwokike/animepahe-tv.git
cd animepahe-tv
uv sync
uv run flet run src/main.py
```

## Building

```bash
# Desktop
uv run flet build windows
uv run flet build linux
uv run flet build macos

# Android (sideload only — not for Play Store)
uv run flet build apk

# Web
uv run flet build web
```

GitHub Actions builds all platforms automatically on push (see `.github/workflows/build-all.yml`). Download artifacts from the Actions tab.

## Distribution

- **Play Store**: Not supported (policy prohibits streaming apps that access copyrighted content without authorization)
- **AdMob**: Not supported (same policy restriction)
- **Sideload**: Build APK with `flet build apk` or download from GitHub Releases / Actions artifacts

## Dependencies

```
flet==0.85.0
flet-video==0.85.0
httpx>=0.28.1
beautifulsoup4>=4.12.0
aiosqlite>=0.22.1
```

All pure Python (except flet-video which bundles libmpv for playback).

## Credits

Built with [Flet](https://flet.dev). D-pad navigation patterns from [KTV Player](https://github.com/Nwokike/ktv-player).
