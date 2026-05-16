import httpx

BASE = "https://animepahe.pw"

FALLBACK_DOMAINS = [
    "https://animepahe.pw",
    "https://animepahe.si",
    "https://animepahe.com",
]


class DDoSSolver:
    def __init__(self, timeout: int = 15):
        self.client = httpx.Client(timeout=timeout, follow_redirects=True)
        self._solved = False
        self._domain = BASE
        self._attempts = 0
        self._max_attempts = 3

    def solve(self) -> bool:
        if self._solved:
            return True
        for domain in FALLBACK_DOMAINS:
            self._domain = domain
            for attempt in range(self._max_attempts):
                try:
                    resp = self.client.get(
                        f"{domain}/",
                        headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                                          "Chrome/120.0.0.0 Safari/537.36",
                            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                        },
                    )
                    ddgid = self.client.cookies.get("__ddgid_")
                    if ddgid:
                        self.client.get(
                            f"{domain}/.well-known/ddos-guard/id/{ddgid}",
                            headers={
                                "User-Agent": self.client.headers["User-Agent"],
                                "Referer": f"{domain}/",
                                "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
                            },
                        )
                        self._solved = True
                        return True
                except httpx.RequestError:
                    continue
        return False

    @property
    def domain(self) -> str:
        return self._domain

    def get(self, url: str, headers: dict | None = None) -> httpx.Response:
        if not self._solved:
            self.solve()
        merged = dict(self.client.headers)
        if headers:
            merged.update(headers)
        return self.client.get(url, headers=merged)

    def close(self):
        self.client.close()
