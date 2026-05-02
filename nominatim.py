import httpx
import asyncio

async def geocode(query: str) -> tuple[float, float]:
    """Nominatim 무료 지오코딩 API를 사용하여 텍스트를 좌표로 변환합니다."""
    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "YeyeTour/1.0 (sdsclass)"}
    params = {"q": query, "format": "json", "limit": 1}
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, headers=headers, timeout=10.0)
            resp.raise_for_status()
            data = resp.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print(f"Geocoding error for {query}: {e}")
    
    return 0.0, 0.0