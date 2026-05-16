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
  <br>
  <img src="https://img.shields.io/badge/Built%20with-Flet%200.85-00B0FF?style=flat-square" alt="Built with Flet" />
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
---

## Screenshots

*Coming soon.*

---

## Features

- **Browse & Search** — Find any anime by keyword with paginated results.
- **Episode Grid** — Snapshot previews, pagination, filler indicators.
- **Multi-Quality** — Choose between available resolutions (360p, 720p, 800p+).
- **TV Remote Ready** — D-pad navigation with visible focus highlights. Built for Android TV and Fire Stick.
- **Waterflow Fallbacks** — Each scraper method has multiple tested backup strategies. If the server changes an endpoint, the next method takes over.

## Architecture

| Layer | Technology |
|-------|-----------|
| Frontend | Flet (Python → Flutter) |
| Video | `flet-video` (libmpv) |
| Network | `httpx` (async, connection pooling) |
| Cache | `aiosqlite` (WAL-mode SQLite with TTL) |
| Scraper | Pure Python (Dean Edwards JS unpack, regex, HTML parse) |

## Legal Disclaimer

AnimePahe TV is a media player and network utility. It does not host, store, or distribute any copyrighted content. The app interfaces with publicly available APIs and web pages. Users are solely responsible for ensuring compliance with applicable laws and terms of service in their jurisdiction.
