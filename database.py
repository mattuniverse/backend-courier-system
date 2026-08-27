import os
import socket
import asyncpg
from urllib.parse import urlparse, urlunparse
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/courier_system")
_pool: asyncpg.Pool | None = None


def _force_ipv4(url: str) -> str:
    parsed = urlparse(url)
    try:
        infos = socket.getaddrinfo(parsed.hostname, None, socket.AF_INET)
        if infos:
            ipv4 = infos[0][4][0]
            return urlunparse(parsed._replace(netloc=parsed.netloc.replace(parsed.hostname, ipv4)))
    except Exception:
        pass
    return url


DATABASE_URL = _force_ipv4(DATABASE_URL)

_is_local = "localhost" in DATABASE_URL or "127.0.0.1" in DATABASE_URL
_url_has_sslmode = "sslmode=" in DATABASE_URL
_statement_cache_size = 0 if not _is_local else 100


async def create_pool():
    global _pool
    kwargs = dict(min_size=1, max_size=10, statement_cache_size=_statement_cache_size)
    if not _is_local and not _url_has_sslmode:
        kwargs["ssl"] = "require"
    _pool = await asyncpg.create_pool(DATABASE_URL, **kwargs)


async def close_pool():
    if _pool:
        await _pool.close()


async def get_conn():
    pool = _pool
    async with pool.acquire() as conn:
        yield conn
