import aiohttp
from config import INSHORT_URL, INSHORT_API, GPLINKS_URL, GPLINKS_API
from database.database import db


async def _call_shortener(domain: str, api_key: str, long_url: str):
    if not domain or not api_key or "YOUR_" in api_key:
        return None

    clean_domain = domain.replace("https://", "").replace("http://", "").strip("/")
    endpoint = f"https://{clean_domain}/api"
    params = {
        "api": api_key,
        "url": long_url,
        "format": "text",
    }

    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(endpoint, params=params) as resp:
                if resp.status != 200:
                    return None
                raw_text = (await resp.text()).strip()

                if raw_text.startswith("{"):
                    data = await resp.json(content_type=None)
                    short_link = (
                        data.get("shortenedUrl")
                        or data.get("shortlink")
                        or data.get("url")
                    )
                    return short_link.strip() if isinstance(short_link, str) else None

                if raw_text.startswith("http"):
                    return raw_text.splitlines()[0].strip()
                return None
    except Exception as e:
        print(f"[SHORTENER ERROR - {clean_domain}]: {e}")
        return None


async def get_rotated_short_link(user_id: int, long_url: str):
    count = await db.get_short_count(user_id)

    inshort_provider = ("inshort", INSHORT_URL, INSHORT_API)
    gplinks_provider = ("gplinks", GPLINKS_URL, GPLINKS_API)

    if count % 2 == 0:
        providers = [inshort_provider, gplinks_provider]
    else:
        providers = [gplinks_provider, inshort_provider]

    for name, domain, api_key in providers:
        short_url = await _call_shortener(domain, api_key, long_url)
        if short_url:
            await db.inc_short_count(user_id)
            return short_url, name

    return None, None
