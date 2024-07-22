import aiohttp
from bot import config


async def get_company(company_id, show_bookforms: bool = False) -> dict:
    async with aiohttp.ClientSession() as open_session:
        if show_bookforms:
            url = f"https://api.yclients.com/api/v1/company/{company_id}?showBookforms=1"
        else:
            url = f"https://api.yclients.com/api/v1/company/{company_id}"
        async with open_session.get(
                url, headers=config.YCLIENTS_HEADERS,
        ) as r:
            response = await r.json()
    return response
