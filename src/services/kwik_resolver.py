import re
import httpx

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
KWIK_PATTERN = re.compile(
    r"\}\('(.*?)',\s*(\d+|\[.*?\])\s*,\s*(\d+)\s*,\s*'(.*?)'\.split\('\|'\)",
    re.DOTALL,
)
M3U8_PATTERN = re.compile(r"https?://[^\'\"\s<>]+\.m3u8[^\s\'\"\)<]*")


def _unbase(value: str, radix: int) -> int:
    result = 0
    for c in value:
        result = result * radix + ALPHABET.index(c)
    return result


def _dean_unpack(html_text: str) -> list[str]:
    urls = []
    for match in KWIK_PATTERN.finditer(html_text):
        payload, radix_str, count, symtab_raw = (
            match.group(1),
            match.group(2),
            int(match.group(3)),
            match.group(4),
        )
        symtab = symtab_raw.split("|")
        radix = 62 if radix_str.startswith("[") else int(radix_str)
        payload = payload.replace("\\\\", "\\").replace("\\'", "'")

        def _replace_word(m: re.Match) -> str:
            word = m.group(0)
            try:
                idx = _unbase(word, radix)
                if 0 <= idx < len(symtab):
                    return symtab[idx] or word
            except (ValueError, IndexError, KeyError):
                pass
            return word

        unpacked = re.sub(r"\b\w+\b", _replace_word, payload)
        urls.extend(M3U8_PATTERN.findall(unpacked))
    return urls


def _direct_m3u8_scan(html_text: str) -> list[str]:
    return M3U8_PATTERN.findall(html_text)


class KwikResolver:
    def __init__(self, timeout: int = 15):
        self.client = httpx.Client(timeout=timeout, follow_redirects=True)

    def resolve(self, kwik_url: str) -> str | None:
        resp = self.client.get(
            kwik_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/120.0.0.0 Safari/537.36",
                "Referer": kwik_url,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        if resp.status_code != 200:
            return None

        urls = _dean_unpack(resp.text)
        if urls:
            m3u8 = urls[0]
            if self._verify_m3u8(m3u8, kwik_url):
                return m3u8

        urls = _direct_m3u8_scan(resp.text)
        for url in urls:
            if self._verify_m3u8(url, kwik_url):
                return url

        return None

    def _verify_m3u8(self, url: str, referer: str) -> bool:
        try:
            resp = self.client.head(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Referer": referer,
                },
                timeout=5,
            )
            return resp.status_code == 200 and "mpegurl" in resp.headers.get("content-type", "")
        except httpx.RequestError:
            return False

    def close(self):
        self.client.close()
