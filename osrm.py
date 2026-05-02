import httpx

async def get_route_duration(lon1: float, lat1: float, lon2: float, lat2: float, profile: str = "driving") -> float:
    """OSRM 무료 라우팅 API를 사용하여 차량/도보 이동 시간을 계산합니다 (분 단위 반환)."""
    # OSRM expects {longitude},{latitude}
    url = f"https://router.project-osrm.org/route/v1/{profile}/{lon1},{lat1};{lon2},{lat2}"
    params = {"overview": "false"}
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, timeout=10.0)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("routes"):
                    # duration in seconds -> return minutes
                    return data["routes"][0]["duration"] / 60.0
    except Exception as e:
        print(f"OSRM API error: {e}")
    return -1.0