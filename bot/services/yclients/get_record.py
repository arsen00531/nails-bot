import aiohttp
from bot import config


async def get_record(company_id, record_id) -> dict:
    async with aiohttp.ClientSession() as open_session:
        url = f"https://api.yclients.com/api/v1/record/{company_id}/{record_id}"
        async with open_session.get(
                url, headers=config.YCLIENTS_HEADERS,
        ) as r:
            response = await r.json()
    return response
