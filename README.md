<p align="center">
  <img src="src/assets/icon.png" alt="AnimePahe TV" width="140" />
</p>

<h1 align="center">AnimePahe TV</h1>

<p align="center">
  A lightweight, client-side streaming app for browsing and watching anime from AnimePahe. Built with Python and Flet.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Windows-0078D6?style=flat-square&logo=windows11&logoColor=white" alt="Windows" />
  <img src="https://img.shields.io/badge/Android-3DDC84?style=flat-square&logo=android&logoColor=white" alt="Android" />
  <img src="https://img.shields.io/badge/Android%20TV-E94560?style=flat-square&logo=android&logoColor=white" alt="Android TV" />
  <img src="https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black" alt="Linux" />
  <br>
  <img src="https://img.shields.io/badge/Built%20with-Flet%200.85-00B0FF?style=flat-square" alt="Built with Flet" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="MIT License" />
</p>

---

## Download

| Platform | Download | Notes |
|:--------:|:--------:|:------|
| 🤖 **Android (Universal)** | [**animepahe-tv.apk**](https://github.com/Nwokike/animepahe-tv/releases/latest/download/animepahe-tv.apk) | Works on all Android devices (ARM64, ARMv7, x86_64) |
| 🤖 **Android (ARM64)** | [**animepahe-tv-arm64-v8a.apk**](https://github.com/Nwokike/animepahe-tv/releases/latest/download/animepahe-tv-arm64-v8a.apk) | For modern 64-bit Android devices |
| 🤖 **Android (ARM32)** | [**animepahe-tv-armeabi-v7a.apk**](https://github.com/Nwokike/animepahe-tv/releases/latest/download/animepahe-tv-armeabi-v7a.apk) | For older 32-bit Android devices |
| 🤖 **Android (x86_64)** | [**animepahe-tv-x86_64.apk**](https://github.com/Nwokike/animepahe-tv/releases/latest/download/animepahe-tv-x86_64.apk) | For Android emulators / ChromeOS |
| 🪟 **Windows** | [**AnimePahe_TV_Setup.exe**](https://github.com/Nwokike/animepahe-tv/releases/latest/download/AnimePahe_TV_Setup.exe) | Windows 10/11 Installer (64-bit) |
| 🐧 **Linux** | [**linux-app.zip**](https://github.com/Nwokike/animepahe-tv/releases/latest/download/linux-app.zip) | x86_64, requires GTK 3 |

---

## Features

- **Browse & Search** — Find any anime by keyword with paginated results.
- **Episode Grid** — Snapshot previews, pagination, filler indicators.
- **Multi-Quality** — Choose between available resolutions (360p, 720p, 800p+).
- **Waterflow Fallbacks** — Each scraper step has a tested backup method. If one breaks, the next takes over.
- **TV Remote Ready** — D-pad navigation with focus highlights. Built for Android TV and Fire Stick.
- **Lightweight** — Pure httpx scraper. No browser, no WebView, no cloudscraper.

---

## How It Works

AnimePahe TV talks directly to AnimePahe's API and pages. No proxy, no server, no cloudscraper.

```text
animepahe.com ──302 redirect──► live domain ──DDoS-Guard handshake──► API
```

**Domain Resolution** — Uses `animepahe.com` with `follow_redirects=True`. The server issues a 302 redirect to whichever domain is live (`.pw`, `.si`, etc.). No hardcoded domain list.

**DDoS-Guard Bypass** — Pure httpx handshake:
1. GET `/` → receives `__ddgid_` cookie
2. GET `/.well-known/ddos-guard/id/{id}` → server sends 1×1 PNG, sets `__ddg2_` cookie
3. Retry original request → verified

**Fallback Methods**

| Step | Primary | Backup |
|------|---------|--------|
| Search | `/api?m=search&q=` JSON | Parse search results HTML |
| Episodes | `/api?m=release&id=` JSON | Parse anime page HTML |
| Sources | `[data-src]` attributes | Regex Kwik URL scrape |
| Kwik M3U8 | Dean Edwards JS unpack | Direct `.m3u8` regex scan |

**Kwik M3U8 Resolution** — Custom Dean Edwards P.A.C.K.E.R. unpacker. Pure Python, no subprocess, no Node.js. Extracts all `eval(function(p,a,c,k,e,d){...})` blocks from the Kwik page, decodes the base62 payload using the symtab array, then regex-extracts the M3U8 URL.

**Playback** — M3U8 URLs from `uwucdn.top` require a `Referer: https://kwik.cx/` header. flet-video (libmpv) sends this via `VideoMedia.http_headers`. No proxy needed.

---

## Architecture

| Layer | Technology | Purpose |
|:---|:---|:---|
| **Frontend** | Flet (Python → Flutter) | Reactive UI, cross-platform |
| **Video** | flet-video (libmpv) | Hardware-accelerated HLS playback |
| **Network** | httpx | Async HTTP with connection pooling |
| **Cache** | aiosqlite | WAL-mode SQLite with TTL |
| **Navigation** | D-pad FocusManager | TV remote support (ported from KTV Player) |

---

## Screenshots

*Coming soon.*

---

## Development

```bash
# Setup
git clone https://github.com/Nwokike/animepahe-tv.git
cd animepahe-tv
uv sync

# Run (desktop)
uv run flet run src/main.py

# Run (web)
uv run flet run --web src/main.py

# Lint
uv run ruff check src/
```

---

## Legal Disclaimer

AnimePahe TV is a media player and network utility. It does not host, store, or distribute any copyrighted content. The app interfaces with publicly available APIs and web pages. Users are solely responsible for ensuring compliance with applicable laws and terms of service in their jurisdiction.
