import httpx
from nominatim import geocode

API_KEY = "5ae2e3f221c38a28845f05b6f23d3b1c9197241a5eb30e0e1bc34661"

async def get_opentripmap_info(attraction_name: str) -> str:
    """OpenTripMap API를 사용하여 관광지의 추가 정보를 가져옵니다."""
    # 1. 지오코딩으로 좌표 획득 (Nominatim 활용)
    lat, lon = await geocode(attraction_name)
    if lat == 0.0 and lon == 0.0:
        return ""

    # 2. OpenTripMap autosuggest API로 장소의 xid 획득
    autosuggest_url = "https://api.opentripmap.com/0.1/en/places/autosuggest"
    params = {
        "name": attraction_name,
        "radius": 50000,
        "lon": lon,
        "lat": lat,
        "limit": 1,
        "apikey": API_KEY
    }

    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            resp = await client.get(autosuggest_url, params=params, timeout=8.0)
            if resp.status_code == 200:
                data = resp.json()
                features = data.get("features", [])
                if not features:
                    return ""
                
                xid = features[0]["properties"]["xid"]
                
                # 3. xid로 상세 정보 획득
                detail_url = f"https://api.opentripmap.com/0.1/en/places/xid/{xid}"
                detail_resp = await client.get(detail_url, params={"apikey": API_KEY}, timeout=8.0)
                
                if detail_resp.status_code == 200:
                    detail_data = detail_resp.json()
                    info_parts = []
                    
                    # 설명 추출 (위키백과 추출본 또는 자체 info 사용)
                    extracts = detail_data.get("wikipedia_extracts", {})
                    if extracts.get("text"):
                        info_parts.append(extracts["text"])
                    elif detail_data.get("info", {}).get("descr"):
                        info_parts.append(detail_data["info"]["descr"])
                        
                    # 주소 및 위치 추출
                    if "address" in detail_data:
                        addr = detail_data["address"]
                        addr_str = " ".join([str(v) for k, v in addr.items() if k in ["country", "city", "road", "house", "suburb"]])
                        if addr_str:
                            info_parts.append(f"📍 주소: {addr_str}")
                            
                    if info_parts:
                        return "\n\n".join(info_parts)
                        
    except Exception as e:
        print(f"OpenTripMap API error for {attraction_name}: {e}")
        
    return ""
