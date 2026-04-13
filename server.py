
import os
import json
import requests
from typing import List, Dict, Any, Literal
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta
import uvicorn

# --- Configuration ---
# 모든 API가 무료이므로, 더 이상 API 키가 필요 없습니다.
NOMINATIM_API_URL = "https://nominatim.openstreetmap.org/search"
OSRM_API_URL = "http://router.project-osrm.org/trip/v1/driving/"

# --- Data Models (Pydantic) ---
# 이전과 동일한 정교한 데이터 모델을 사용합니다.

class TravelSegment(BaseModel):
    mode: Literal["walk", "transit", "drive", "train", "flight"]
    duration_minutes: int = Field(..., description="예상 이동 시간(분)")
    distance_km: float = Field(..., description="예상 이동 거리(km)")
    instructions: str = Field(..., description="간단한 이동 안내")

class Attraction(BaseModel):
    name: str = Field(..., description="장소 또는 이벤트의 이름")
    type: Literal["attraction", "restaurant", "hotel", "custom_event"] = Field("attraction", description="장소 유형")
    location_query: str = Field(..., description="주소 또는 검색 가능한 위치명")
    coordinates: str | None = Field(None, description="위도,경도 (예: 41.8902,12.4922)")
    description: str | None = None
    details: Dict[str, Any] = Field(default_factory=dict, description="[Wiki] 역사, 꿀팁, 운영 시간 등 상세 정보")

class DailyEvent(BaseModel):
    sequence_id: int
    start_time: str
    event_type: Literal["attraction", "travel", "custom"]
    event_details: Attraction
    travel_to_next: TravelSegment | None = None

class DailyPlan(BaseModel):
    day: int
    date: str
    city: str
    title: str
    summary: str
    events: List[DailyEvent]
    openstreetmap_url: str | None = Field(None, description="하루 동선 전체를 볼 수 있는 OpenStreetMap 다중 목적지 지도 URL")

# --- External API Call Implementation ---

def _get_coordinates_for_attraction(attraction: Attraction) -> str:
    """Nominatim API를 사용하여 주소/장소명을 좌표로 변환합니다."""
    params = {'q': attraction.location_query, 'format': 'json', 'limit': 1}
    try:
        response = requests.get(NOMINATIM_API_URL, params=params, headers={'User-Agent': 'TravelMCP/1.0'})
        response.raise_for_status()
        data = response.json()
        if data:
            lat, lon = data[0]["lat"], data[0]["lon"]
            print(f"INFO: [Nominatim] '{attraction.name}' -> ({lat}, {lon})")
            return f"{lon},{lat}" # OSRM은 경도,위도 순서
    except requests.RequestException as e:
        print(f"ERROR: [Nominatim] API 호출 실패: {e}")
    return None

def _simulate_brave_search_for_wiki(attraction_name: str) -> Dict[str, Any]:
    """[Placeholder] Brave Search API를 호출하여 '전문 잡지' 수준의 정보를 생성합니다."""
    print(f"INFO: [Brave Search] '{attraction_name}' 상세 정보 검색 시뮬레이션...")
    mock_data = {
        "콜로세움": {
            "history": "고대 로마 제국의 가장 상징적인 건축물...",
            "opening_hours": "매일 09:00 - 19:15",
            "tips": ["온라인 예매 필수", "통합권 구매 추천"],
            "recommended_duration_hours": 2.5
        },
        "바티칸 미술관": {
            "history": "카톨릭 교회의 심장이자, 역대 교황들이 수집한 방대한 예술품 컬렉션...",
            "opening_hours": "월-토 09:00 - 18:00",
            "tips": ["복장 규정 주의", "무료 입장일은 피하는 것이 좋음"],
            "recommended_duration_hours": 4
        }
    }
    return mock_data.get(attraction_name, {"error": f"'{attraction_name}'에 대한 정보를 찾을 수 없습니다."})

# --- MCP Tool Implementation ---

mcp_app = FastAPI(
    title="Travel Master Control Program (Open-Source Edition)",
    description="Google API 대신 OpenStreetMap과 OSRM을 사용하는 무료 여행 플래너 서버입니다.",
    version="1.1.0",
)

@mcp_app.post("/plan_daily_trip", response_model=DailyPlan, summary="[Tool] 하루 여행 계획 생성 (무료 API 기반)")
def plan_daily_trip(city: str, date: str, attractions: List[str] = Field(..., example=["콜로세움", "바티칸 미술관"])):
    """도시와 방문 희망 장소 목록으로 최적화된 하루 계획을 무료로 생성합니다."""
    print(f"MCP-TOOL: plan_daily_trip(city='{city}', date='{date}') 실행")
    
    attraction_objects = [Attraction(name=name, location_query=f"{name}, {city}") for name in attractions]

    # 1. 좌표 변환 및 위키 정보 가져오기
    for att in attraction_objects:
        att.coordinates = _get_coordinates_for_attraction(att)
        att.details = get_attraction_wiki(attraction_name=att.name)
    
    # 좌표 변환에 실패한 장소는 제외
    valid_attractions = [att for att in attraction_objects if att.coordinates]
    if not valid_attractions:
        raise HTTPException(status_code=400, detail="모든 장소의 좌표를 찾을 수 없습니다. 장소 이름을 확인해주세요.")

    # 2. 경로 최적화 (MCP Tool: optimize_daily_route_opensource)
    optimized_result = optimize_daily_route_opensource(valid_attractions)
    ordered_attractions = optimized_result["attractions"]
    segments = optimized_result["segments"]
    
    # 3. 지도 링크 생성 (MCP Tool: generate_map_links_opensource)
    map_url = generate_map_links_opensource(ordered_attractions)

    # 4. 최종 DailyPlan 객체 구성
    events = []
    current_time = datetime.strptime("09:00", "%H:%M")
    for i, att in enumerate(ordered_attractions):
        event = DailyEvent(
            sequence_id=i,
            start_time=current_time.strftime("%H:%M"),
            event_type="attraction",
            event_details=att,
            travel_to_next=segments[i] if i < len(segments) else None
        )
        events.append(event)
        
        duration_hours = att.details.get("recommended_duration_hours", 1.5)
        current_time += timedelta(hours=duration_hours)
        if event.travel_to_next:
            current_time += timedelta(minutes=event.travel_to_next.duration_minutes)

    return DailyPlan(
        day=1, date=date, city=city,
        title=f"{city} 핵심 탐방 (Open-Source)",
        summary=f"{', '.join([att.name for att in ordered_attractions])} 등을 둘러보는 하루",
        events=events,
        openstreetmap_url=map_url
    )

# --- MCP Sub-Tools (내부 호출용 함수, 오픈소스 기반) ---

def get_attraction_wiki(attraction_name: str) -> Dict[str, Any]:
    return _simulate_brave_search_for_wiki(attraction_name)

def optimize_daily_route_opensource(attractions: List[Attraction]) -> Dict[str, Any]:
    """[Sub-Tool] OSRM API를 사용하여 경로를 최적화하고 이동 정보를 계산합니다."""
    coords_str = ";".join([att.coordinates for att in attractions])
    url = f"{OSRM_API_URL}{coords_str}?overview=false&roundtrip=false&source=first&destination=last"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data['code'] != 'Ok':
            raise HTTPException(status_code=500, detail=f"OSRM API Error: {data.get('message')}")

        print(f"INFO: [OSRM] 경로 최적화 성공. Waypoints: {len(data['waypoints'])}")

        # OSRM 결과(waypoints)는 최적화된 순서를 담고 있습니다.
        waypoint_order = [wp['waypoint_index'] for wp in data['waypoints']]
        ordered_attractions = [attractions[i] for i in waypoint_order]
        
        segments = []
        for leg in data['trips'][0]['legs']:
            segments.append(TravelSegment(
                mode="drive", # OSRM 데모는 주로 driving 기준
                duration_minutes=round(leg['duration'] / 60),
                distance_km=round(leg['distance'] / 1000, 2),
                instructions=f"약 {round(leg['duration'] / 60)}분, {round(leg['distance'] / 1000, 2)}km 이동"
            ))
        # 마지막 장소에서 다음으로 가는 이동 정보는 없으므로 하나를 제거해야 할 수 있습니다.
        # OSRM은 각 leg를 연결하므로 trip의 leg 개수는 waypoint 개수 - 1 입니다.

        return {"attractions": ordered_attractions, "segments": segments}
    
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"OSRM API 호출 실패: {e}")

def generate_map_links_opensource(optimized_attractions: List[Attraction]) -> str:
    """[Sub-Tool] 최적화된 경로의 OpenStreetMap 다중 목적지 URL을 생성합니다."""
    if not optimized_attractions: return ""
    
    base_url = "https://www.openstreetmap.org/directions?engine=osrm_car"
    # Nominatim에서 받은 lat,lon 순서(쉼표 구분)를 사용합니다.
    coords_for_url = [f"{att.coordinates.split(',')[1]},{att.coordinates.split(',')[0]}" for att in optimized_attractions]
    waypoints = "&".join([f"route={coord}" for coord in coords_for_url])
    
    return f"{base_url}&{waypoints}"


# --- Main Application Runner ---
if __name__ == "__main__":
    print("--- Travel Master Control Program Server (Open-Source Edition) ---")
    print("API 문서는 서버 시작 후 http://127.0.0.1:8000/docs 에서 확인하세요.")
    print("\n테스트용 cURL 명령어:")
    print("curl -X POST \"
          " http://127.0.0.1:8000/plan_daily_trip \"
          " -H 'Content-Type: application/json' \"
          " -d '{ "city": "로마", "date": "2024-10-26", "attractions": ["콜로세움", "바티칸 미술관"] }'")
    
    uvicorn.run("server:mcp_app", host="0.0.0.0", port=8000, reload=True)

