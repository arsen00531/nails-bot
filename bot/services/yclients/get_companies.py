import aiohttp
from bot import config


async def get_companies() -> dict:
    async with aiohttp.ClientSession() as open_session:
        url = f"https://api.yclients.com/api/v1/companies?my=1&showBookforms=1&count=100"
        async with open_session.get(
                url, headers=config.YCLIENTS_HEADERS,
        ) as r:
            response = await r.json()
    return response
