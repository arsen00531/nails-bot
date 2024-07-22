import aiohttp
from bot import config


async def get_company_records(company_id, year, month, day) -> dict:
    async with aiohttp.ClientSession() as open_session:
        url = f"https://api.yclients.com/api/v1/records/{company_id}?page=1&count=500&start_date={year}-{month}-{day}"
        async with open_session.get(
                url, headers=config.YCLIENTS_HEADERS,
        ) as r:
            response = await r.json()
    return response
