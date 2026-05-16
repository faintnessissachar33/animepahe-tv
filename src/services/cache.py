import json
import time
import aiosqlite


class Cache:
    def __init__(self, db_path: str = "animepahe.db"):
        self.db_path = db_path

    async def _ensure_table(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    expires INTEGER
                )
            """)
            await db.commit()

    async def get(self, key: str) -> str | None:
        await self._ensure_table()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT value, expires FROM cache WHERE key = ?", (key,)
            )
            row = await cursor.fetchone()
            if row:
                value, expires = row
                if expires > time.time():
                    return value
                await db.execute("DELETE FROM cache WHERE key = ?", (key,))
                await db.commit()
            return None

    async def set(self, key: str, value: str, ttl: int = 3600):
        await self._ensure_table()
        expires = int(time.time()) + ttl
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO cache (key, value, expires) VALUES (?, ?, ?)",
                (key, value, expires),
            )
            await db.commit()

    async def set_json(self, key: str, value, ttl: int = 3600):
        await self.set(key, json.dumps(value, default=str), ttl)

    async def get_json(self, key: str):
        raw = await self.get(key)
        if raw:
            return json.loads(raw)
        return None

    async def invalidate(self, key: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM cache WHERE key = ?", (key,))
            await db.commit()

    async def invalidate_pattern(self, pattern: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM cache WHERE key LIKE ?", (f"%{pattern}%",)
            )
            await db.commit()

    async def clear(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM cache")
            await db.commit()
