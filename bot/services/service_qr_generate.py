import aiohttp

async def service_qr_generate(service_qr_url, data: str) -> bytes:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{service_qr_url}/generate", params={"data": data}) as resp:
            return await resp.read()