# YeyeTour MCP Server

`YeyeTour`는 도시와 날짜만으로 여행 일정을 생성하고, 도시별 동선을 최적화하며, 관광지 설명과 무료 지도 링크를 JSON으로 반환하는 `fastmcp` 기반 Python MCP 서버입니다.

## 제공 도구

- `plan_trip`: 여러 도시와 날짜를 받아 전체 일정의 뼈대를 생성
- `optimize_daily_route`: 특정 도시 내 방문지 순서를 동선 기준으로 최적화
- `get_attraction_wiki`: 관광지의 역사, 문화, 운영 정보, 팁을 풍부한 JSON으로 반환
- `generate_map_links`: 최적화된 경로로 OpenStreetMap 링크, `geo:` URI, GeoJSON 경로 데이터 생성

## 빠른 실행

```bash
docker compose up --build
```

기본 MCP HTTP 엔드포인트:

- `http://localhost:8000/mcp`
- 브라우저 안내 페이지: `http://localhost:8000/`
- 헬스 체크: `http://localhost:8000/health`

## 환경 변수

- `MCP_TRANSPORT`: `streamable-http` 또는 `stdio` (`streamable-http` 기본값)
- `HOST`: HTTP 바인드 주소, 기본 `0.0.0.0`
- `PORT`: HTTP 포트, 기본 `8000`
- `BRAVE_API_KEY`: Brave Search 연동용
- `DEFAULT_COUNTRY_CODE`: 기본 지역 힌트, 기본 `it`

## 설치

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py
```

## 테스트 클라이언트

로컬 서버 스모크 테스트:

```bash
source .venv/bin/activate
python test_mcp_client.py
```

배포 서버 테스트:

```bash
source .venv/bin/activate
python test_mcp_client.py --url https://travelmcp.yejeelee.synology.me/mcp
```

전체 툴 호출 테스트:

```bash
source .venv/bin/activate
python test_mcp_client.py --full
```

## 예시 입력

`plan_trip` 예시:

```json
{
  "trip_name": "Italy and Malta Grand Tour",
  "start_date": "2026-10-01",
  "end_date": "2026-10-19",
  "cities": [
    {
      "name": "Rome",
      "nights": 4,
      "must_visit": ["Colosseum", "Pantheon"],
      "notes": "초반은 고대 로마 중심"
    },
    {
      "name": "Palermo",
      "nights": 3,
      "arrival": {
        "mode": "night_train",
        "from": "Rome",
        "notes": "로마 발 시칠리아행 야간열차"
      }
    },
    {
      "name": "Valletta",
      "nights": 2
    }
  ],
  "traveler_profile": {
    "pace": "balanced",
    "interests": ["history", "food", "architecture"]
  }
}
```

## 구현 메모

- 외부 API 키가 없어도 로컬 휴리스틱과 내장 관광지 데이터로 동작합니다.
- Brave Search 키가 있으면 `get_attraction_wiki`가 최신 스니펫과 출처를 덧붙입니다.
- 지도 결과는 OpenStreetMap, `geo:` URI, GeoJSON 기반이라 무료로 바로 사용할 수 있습니다.
