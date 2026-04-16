# YeyeTour MCP Server 개발 정리

## 개요

`YeyeTour`는 `fastmcp` 기반의 Python MCP 서버 1차 버전입니다.  
사용자가 도시와 날짜를 입력하면 여행 일정 초안, 일별 동선 최적화, 관광지 상세 설명, 무료 지도 링크 데이터를 JSON 형태로 반환하도록 설계했습니다.

핵심 목표는 다음과 같습니다.

- 도시/날짜 기반 전체 일정 자동 생성
- 일별 방문지 순서 최적화
- 관광지별 풍부한 설명 제공
- 디지털 가이드북(HTML/JS)에서 즉시 사용 가능한 JSON 응답
- Synology NAS에서도 바로 띄울 수 있는 Docker 구성

## 구현 파일

- [server.py](/home/sdsclass/YeyeTour/server.py): MCP 서버 본체와 모든 비즈니스 로직
- [requirements.txt](/home/sdsclass/YeyeTour/requirements.txt): Python 의존성
- [Dockerfile](/home/sdsclass/YeyeTour/Dockerfile): 컨테이너 이미지 빌드 설정
- [docker-compose.yml](/home/sdsclass/YeyeTour/docker-compose.yml): 실행 설정
- [README.md](/home/sdsclass/YeyeTour/README.md): 기본 사용법 및 예시 입력

## 구현된 MCP Tools

### `plan_trip`

입력받은 여행 기간과 도시 목록을 바탕으로 전체 일정 뼈대를 생성합니다.

주요 특징:

- 장기 일정 대응 가능
- `nights`, `days`, `start_date`, `end_date` 조합 처리
- 도시별 체류 일수 자동 배분
- `must_visit`, `secondary_visit`, `theme`, `meal_hint`, `hotel_area` 반영
- `fixed_legs`로 사용자 고정 이동 이력 반영 가능
- 예: 로마 출발 시칠리아행 야간열차 같은 사용자 실제 이동 시나리오 반영

반환 핵심 구조:

- `summary`
- `city_segments`
- `transport_plan`
- `daily_plan`
- `meta`

### `optimize_daily_route`

특정 도시 안에서 방문지 목록을 받아 가장 효율적인 순서로 정렬합니다.

주요 특징:

- 좌표 기반 nearest-neighbor 방식 경로 정렬
- 방문지 간 거리 계산
- 도보/대중교통/택시 추정
- 각 구간 이동 시간 계산
- 방문 도착/출발 시각 자동 계산
- 출발지와 도착지 별도 지정 가능

반환 핵심 구조:

- `optimized_route`
- `final_leg`
- `totals`
- `map_links`

### `get_attraction_wiki`

관광지별 상세 설명을 디지털 가이드북 수준으로 제공합니다.

주요 특징:

- 역사
- 문화적 배경
- 운영 시간 메모
- 추천 방문 시간
- 실전 팁
- Brave Search API 키가 있으면 최신 정보 스니펫 추가

반환 핵심 구조:

- `attraction`
- `editorial`
- `live_updates`
- `map_links`

### `generate_map_links`

최적화된 경로나 방문지 목록을 바탕으로 무료 지도 링크와 프론트엔드용 좌표 데이터를 생성합니다.

주요 특징:

- OpenStreetMap 개요 링크 생성
- 구간별 OSM directions 링크 생성
- `geo:` URI 생성
- 지도 컴포넌트에서 바로 사용 가능한 `GeoJSON` 생성

반환 핵심 구조:

- `links.openstreetmap_overview`
- `links.openstreetmap_leg_directions`
- `links.openstreetmap_place_links`
- `links.geo_uris`
- `links.geojson`

## 데이터 설계 특징

### 1. 유연한 입력 구조

입력 JSON은 단순 도시 리스트만이 아니라 아래와 같은 실제 여행 문맥을 담을 수 있게 만들었습니다.

- 도시별 `arrival`
- 도시별 `departure`
- 도시별 `notes`
- 도시별 `must_visit`
- 전체 일정의 `traveler_profile`
- 도시 간 `fixed_legs`

이 구조 덕분에 사용자의 실제 여행 이력과 선호를 일정에 반영하기 쉽습니다.

### 2. 프론트엔드 친화적 JSON

결과는 HTML/JS 가이드북에서 바로 렌더링할 수 있도록 구성했습니다.

- 일자별 배열 중심 구조
- 좌표 포함
- 지도 링크 포함
- UI 카드에 넣기 쉬운 `summary`, `narrative`, `theme` 포함
- GeoJSON 제공

### 3. 외부 API 없이도 동작하는 기본 엔진

1차 버전은 외부 API 키가 없어도 동작하도록 설계했습니다.

- 내장 관광지 카탈로그 사용
- 도시 중심 좌표 fallback 제공
- 도시 간 이동은 휴리스틱 추정
- 관광지 설명은 내장 데이터 기반

즉, 네트워크 연동이 없어도 데모와 초기 제품화가 가능합니다.

## 무료 지도 스택으로 변경한 내용

초기 설계에서 Google Maps 계열 링크가 포함되어 있었지만, 이후 무료 스택으로 전환했습니다.

현재 사용 방식:

- `OpenStreetMap` 장소 링크
- `OpenStreetMap` 구간별 directions 링크
- `geo:` URI
- `GeoJSON` 경로 데이터

제거한 내용:

- Google Maps API 의존성
- `GOOGLE_MAPS_API_KEY` 환경 변수
- Google Maps URL 생성 로직

이 변경으로 별도 유료 API 없이도 지도 기능을 계속 사용할 수 있습니다.

## 내장 관광지 카탈로그

현재 내장 데이터가 포함된 도시:

- Rome
- Florence
- Venice
- Milan
- Naples
- Palermo
- Catania
- Valletta

각 관광지 데이터에는 다음 정보가 포함됩니다.

- 이름
- 좌표
- 카테고리
- 추천 체류 시간
- 지역
- 요약 설명
- 역사 정보
- 문화적 해설
- 운영 시간 메모
- 팁

## Docker 구성

Synology NAS 등에서 바로 구동할 수 있도록 Docker 구성을 추가했습니다.

### `Dockerfile`

- Python 3.12 slim 이미지 사용
- `requirements.txt` 기반 패키지 설치
- `server.py` 실행
- 기본 포트 `8000` 노출

### `docker-compose.yml`

- 서비스명: `yeye-tour-mcp`
- 기본 `MCP_TRANSPORT=streamable-http`
- 기본 포트 매핑: `8000:8000`
- Brave Search 키 선택적 주입 가능
- `restart: unless-stopped` 설정

## 실행 방식

### 로컬 실행

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py
```

### Docker 실행

```bash
docker compose up --build
```

기본 MCP HTTP 엔드포인트:

```text
http://localhost:8000/mcp
```

## 현재 아키텍처 특징

- 단일 파일 `server.py`에 모든 로직 집중
- 함수 단위로 분리해 가독성 유지
- 확장 포인트 존재
- 외부 의존성 최소화
- 기본적으로 휴리스틱 엔진 기반

핵심 보조 함수 예시:

- 날짜 파싱
- 체류일 계산
- 도시 배분
- 거리 계산
- 이동 시간 추정
- 관광지 fallback 생성
- GeoJSON 생성

## 검증 상태

다음 검증을 완료했습니다.

- `python3 -m py_compile /home/sdsclass/YeyeTour/server.py` 통과
- Google Maps 참조 제거 확인
- `docker-compose.yml`에서 Google Maps 환경 변수 제거 확인

## 현재 한계

1차 버전 기준 한계도 분명합니다.

- 실시간 운영 시간 검증은 Brave Search가 없으면 제한적
- 실제 대중교통 timetable 연동 없음
- 도시 내 동선 최적화는 고급 TSP가 아니라 휴리스틱 기반
- 관광지 DB가 아직 일부 도시만 내장됨
- 호텔, 레스토랑, 항공권 같은 예약 도메인은 미포함

## 다음 확장 추천

- OSM/Nominatim 기반 장소 검색 강화
- OSRM 또는 GraphHopper 기반 실제 라우팅 연동
- 도시별 관광지 데이터셋 외부 파일 분리
- HTML 가이드북용 샘플 프론트 추가
- 일정 충돌 검증 로직 추가
- 레스토랑/카페 추천 툴 추가
- 날씨 반영 일정 보정 기능 추가

## 결론

현재 버전은 여행 일정 생성 MCP 서버의 실용적인 첫 번째 베이스라인입니다.

이미 가능한 것:

- 멀티시티 일정 생성
- 일별 동선 정렬
- 관광지 설명 생성
- 무료 지도 링크 및 GeoJSON 반환
- Docker 기반 배포

즉, 이 상태만으로도 디지털 여행 가이드북과 연결되는 기본 MCP 백엔드로 충분히 사용할 수 있습니다.
