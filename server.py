import asyncio
import math
import os
from copy import deepcopy
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any
from urllib.parse import quote

import httpx
from mcp.server.fastmcp import FastMCP


@dataclass(frozen=True)
class AttractionSeed:
    name: str
    lat: float
    lng: float
    categories: list[str]
    visit_minutes: int
    best_for: list[str]
    area: str
    summary: str
    history: str
    cultural_note: str
    hours: str
    tips: list[str]


CATALOG: dict[str, list[AttractionSeed]] = {
    "rome": [
        AttractionSeed(
            name="Colosseum",
            lat=41.8902,
            lng=12.4922,
            categories=["history", "architecture"],
            visit_minutes=120,
            best_for=["first_time", "history"],
            area="Ancient Rome",
            summary="로마 제국의 상징인 거대한 원형 경기장으로 검투 경기와 공공 행사가 열렸던 곳입니다.",
            history="플라비우스 왕조 시기인 서기 1세기에 완공되었고, 제국 권력의 시각적 선언으로 기능했습니다.",
            cultural_note="현재는 고대 로마의 공학, 대중 오락, 정치 선전이 만나는 핵심 유적으로 해석됩니다.",
            hours="대체로 오전 입장 시작, 계절별 마감 시간 변동",
            tips=["오전 첫 타임 예약이 가장 효율적입니다.", "포로 로마노와 묶어 반나절로 계획하면 좋습니다."],
        ),
        AttractionSeed(
            name="Roman Forum",
            lat=41.8925,
            lng=12.4853,
            categories=["history", "archaeology"],
            visit_minutes=90,
            best_for=["history"],
            area="Ancient Rome",
            summary="고대 로마의 정치, 종교, 상업 중심지였던 유적 지대입니다.",
            history="공화정과 제정 로마를 거치며 개선식, 재판, 연설이 이루어지던 공적 무대였습니다.",
            cultural_note="폐허처럼 보이지만 로마 시민의 일상과 권력 구조를 읽을 수 있는 장소입니다.",
            hours="콜로세움 통합권과 연계되는 경우가 많음",
            tips=["햇볕이 강하니 물과 모자를 준비하세요.", "팔라티노 언덕과 연속 동선으로 묶으면 좋습니다."],
        ),
        AttractionSeed(
            name="Pantheon",
            lat=41.8986,
            lng=12.4769,
            categories=["architecture", "religion"],
            visit_minutes=60,
            best_for=["architecture", "rainy_day"],
            area="Historic Center",
            summary="로마에서 가장 완전하게 보존된 고대 신전이자 돔 건축의 걸작입니다.",
            history="하드리아누스 황제 시기 재건되어 오늘날까지 거의 원형을 유지합니다.",
            cultural_note="고대 로마 콘크리트 기술의 정점이자, 이후 르네상스 건축에 큰 영향을 준 건물입니다.",
            hours="입장 시간은 요일과 종교 행사에 따라 변동 가능",
            tips=["비 오는 날 오큘러스 아래 분위기가 특히 인상적입니다.", "주변 광장 카페와 함께 묶기 좋습니다."],
        ),
        AttractionSeed(
            name="Trevi Fountain",
            lat=41.9009,
            lng=12.4833,
            categories=["landmark", "photo_spot"],
            visit_minutes=30,
            best_for=["first_time", "night_view"],
            area="Trevi",
            summary="바로크 도시 연출의 대표작으로, 로마 여행의 상징 같은 분수입니다.",
            history="18세기 완성된 후기 바로크 공공 분수로 로마 수로 문화를 기념합니다.",
            cultural_note="동전 던지기 관습으로도 유명해 관광 의례가 된 공간입니다.",
            hours="상시 외부 관람 가능",
            tips=["이른 아침이나 늦은 밤이 비교적 한산합니다.", "계단과 주변 동선이 혼잡해 소매치기를 주의하세요."],
        ),
        AttractionSeed(
            name="Vatican Museums",
            lat=41.9065,
            lng=12.4536,
            categories=["art", "museum"],
            visit_minutes=180,
            best_for=["art", "rainy_day"],
            area="Vatican",
            summary="고전 조각에서 르네상스 회화까지 이어지는 세계적 수준의 교황청 컬렉션입니다.",
            history="수 세기에 걸쳐 축적된 교황청 소장품이 미술관군 형태로 정리되었습니다.",
            cultural_note="서양 미술사와 가톨릭 시각 문화의 축을 압축적으로 보여줍니다.",
            hours="요일별 운영 차이 큼, 사전 예약 권장",
            tips=["예약 시간 20~30분 전 도착이 안전합니다.", "시스티나 성당 이후 동선까지 감안해 체력을 배분하세요."],
        ),
    ],
    "florence": [
        AttractionSeed(
            name="Duomo di Firenze",
            lat=43.7731,
            lng=11.2560,
            categories=["architecture", "religion"],
            visit_minutes=90,
            best_for=["first_time", "architecture"],
            area="Centro Storico",
            summary="브루넬레스키의 돔으로 상징되는 피렌체의 도시 정체성 그 자체입니다.",
            history="중세 말부터 르네상스 초기에 걸쳐 완성된 대성당 복합체입니다.",
            cultural_note="도시 국가 피렌체의 경제력과 기술 혁신이 집약된 프로젝트였습니다.",
            hours="돔, 종탑, 성당 본당은 운영 시간이 서로 다름",
            tips=["돔 등반은 사전 예약이 사실상 필수입니다.", "세례당과 박물관을 함께 보면 이해도가 높아집니다."],
        ),
        AttractionSeed(
            name="Uffizi Gallery",
            lat=43.7687,
            lng=11.2550,
            categories=["art", "museum"],
            visit_minutes=150,
            best_for=["art"],
            area="Arno Riverside",
            summary="보티첼리, 레오나르도, 미켈란젤로 등 르네상스 걸작을 만나는 핵심 미술관입니다.",
            history="메디치 행정 건물에서 출발해 왕가 컬렉션이 대중 미술관으로 전환되었습니다.",
            cultural_note="르네상스 회화의 진화와 후원 체계를 한눈에 보여줍니다.",
            hours="월요일 휴관 가능성이 높아 사전 확인 권장",
            tips=["대표작 중심으로 보고 싶다면 사전 하이라이트 리스트를 준비하세요.", "오후 후반 입장은 동선 압축이 필요합니다."],
        ),
        AttractionSeed(
            name="Ponte Vecchio",
            lat=43.7679,
            lng=11.2531,
            categories=["landmark", "walk"],
            visit_minutes=30,
            best_for=["night_view", "photo_spot"],
            area="Arno Riverside",
            summary="중세의 상업 구조가 남아 있는 피렌체의 상징적 다리입니다.",
            history="오랜 재건과 개조를 거치며 현재의 독특한 점포형 다리 풍경이 자리 잡았습니다.",
            cultural_note="도시 상업과 장인 문화가 건축에 결합된 피렌체다운 장소입니다.",
            hours="상시 외부 관람 가능",
            tips=["일몰 시간대 아르노 강변 산책과 함께 넣기 좋습니다.", "성수기에는 다리 자체보다 주변 강변 뷰가 더 쾌적합니다."],
        ),
    ],
    "venice": [
        AttractionSeed(
            name="St. Mark's Basilica",
            lat=45.4340,
            lng=12.3393,
            categories=["architecture", "religion"],
            visit_minutes=75,
            best_for=["first_time", "architecture"],
            area="San Marco",
            summary="베네치아 공화국의 정치적 상징성과 동방 취향이 응축된 대성당입니다.",
            history="비잔틴 영향과 해상 교역의 부가 겹겹이 쌓인 종교 건축입니다.",
            cultural_note="금빛 모자이크와 장식은 베네치아의 국제성을 드러냅니다.",
            hours="예배 및 관광 시간 분리 운영 가능",
            tips=["배낭 규정을 사전에 확인하세요.", "산 마르코 광장은 이른 아침이 가장 아름답습니다."],
        ),
        AttractionSeed(
            name="Doge's Palace",
            lat=45.4337,
            lng=12.3404,
            categories=["history", "museum"],
            visit_minutes=120,
            best_for=["history"],
            area="San Marco",
            summary="베네치아 공화국의 행정, 사법, 외교가 교차하던 권력의 궁전입니다.",
            history="고딕 양식의 궁전으로 국가 권력의 무대이자 감옥과 연결된 상징적 구조를 가집니다.",
            cultural_note="자유로운 해상 공화국이라는 이미지 뒤편의 제도적 엄격함을 보여줍니다.",
            hours="대체로 오전부터 저녁까지 운영",
            tips=["탄식의 다리와 연결되는 내부 서사를 놓치지 마세요.", "산 마르코 대성당과 반일 코스로 엮기 좋습니다."],
        ),
        AttractionSeed(
            name="Rialto Bridge",
            lat=45.4380,
            lng=12.3359,
            categories=["landmark", "walk"],
            visit_minutes=25,
            best_for=["photo_spot", "food"],
            area="Rialto",
            summary="대운하와 시장 문화가 만나는 베네치아의 대표 다리입니다.",
            history="상업 중심지 리알토의 흐름을 잇는 교량으로 도시 경제의 핵심이었습니다.",
            cultural_note="관광 엽서 이미지이면서도 실제 생활권의 밀도를 느낄 수 있습니다.",
            hours="상시 외부 관람 가능",
            tips=["리알토 시장 운영 시간과 맞추면 더 풍성합니다.", "점심 직전이 가장 활기찹니다."],
        ),
    ],
    "milan": [
        AttractionSeed(
            name="Duomo di Milano",
            lat=45.4642,
            lng=9.1916,
            categories=["architecture", "religion"],
            visit_minutes=90,
            best_for=["first_time", "architecture"],
            area="Centro",
            summary="수백 년에 걸쳐 완성된 밀라노의 고딕 대성당입니다.",
            history="도시의 정치적 위상과 장인 기술이 오랜 세월 축적된 건축 프로젝트입니다.",
            cultural_note="옥상 테라스 경험이 특히 강렬해 도시 스카이라인 이해에 좋습니다.",
            hours="성당 내부와 옥상 운영 시간이 다를 수 있음",
            tips=["옥상 입장을 함께 예약하면 만족도가 높습니다.", "아침 시간대가 비교적 쾌적합니다."],
        ),
        AttractionSeed(
            name="Galleria Vittorio Emanuele II",
            lat=45.4659,
            lng=9.1900,
            categories=["shopping", "architecture"],
            visit_minutes=30,
            best_for=["design", "rainy_day"],
            area="Centro",
            summary="19세기 유리 아케이드의 우아함을 보여주는 밀라노의 도시 실내 광장입니다.",
            history="이탈리아 통일 이후 근대 도시 미학을 상징하는 상업 공간으로 계획되었습니다.",
            cultural_note="럭셔리 상업과 공공 산책이 공존하는 밀라노식 도시 장면입니다.",
            hours="상시 통행 가능, 개별 상점 시간 상이",
            tips=["두오모와 자연스럽게 연결됩니다.", "바닥 모자이크 구경 포인트를 놓치지 마세요."],
        ),
    ],
    "naples": [
        AttractionSeed(
            name="Naples National Archaeological Museum",
            lat=40.8530,
            lng=14.2505,
            categories=["museum", "archaeology"],
            visit_minutes=150,
            best_for=["history", "rainy_day"],
            area="Centro Storico",
            summary="폼페이와 헤르쿨라네움 유물 이해를 위해 매우 중요한 박물관입니다.",
            history="부르봉 시대 컬렉션이 중심이 된 남이탈리아 고고학의 보고입니다.",
            cultural_note="로마 유적 현장을 보기 전후로 연결하면 이해가 크게 깊어집니다.",
            hours="주중 일부 휴관 가능",
            tips=["폼페이 방문 전 예습 코스로도 좋습니다.", "소장품이 방대하니 섹션을 정해 보세요."],
        ),
        AttractionSeed(
            name="Spaccanapoli",
            lat=40.8478,
            lng=14.2553,
            categories=["walk", "food"],
            visit_minutes=75,
            best_for=["food", "street_life"],
            area="Centro Storico",
            summary="나폴리의 역사 중심부를 가르는 길로, 도시의 밀도와 리듬을 체험하기 좋습니다.",
            history="그리스-로마 도시 구조의 흔적이 오늘날까지 이어진 생활 축입니다.",
            cultural_note="종교, 시장, 음식, 소음이 뒤엉킨 나폴리의 본질적인 경험이 가능합니다.",
            hours="상시 도보 가능",
            tips=["저녁 전 산책과 간식 투어를 결합하기 좋습니다.", "골목이 복잡하니 주요 성당을 랜드마크로 삼으세요."],
        ),
    ],
    "palermo": [
        AttractionSeed(
            name="Palermo Cathedral",
            lat=38.1054,
            lng=13.3523,
            categories=["architecture", "religion"],
            visit_minutes=60,
            best_for=["architecture", "history"],
            area="Centro Storico",
            summary="노르만, 아라브, 고딕, 바로크 층위가 겹친 팔레르모의 상징적 성당입니다.",
            history="시칠리아를 거친 다양한 지배 세력의 흔적이 건물 전반에 남아 있습니다.",
            cultural_note="섬 특유의 혼종성과 지중해 교차로의 정체성을 읽기 좋은 장소입니다.",
            hours="본당과 지붕, 왕릉 구역 시간 상이",
            tips=["지붕 입장이 가능하면 도시 전체 맥락을 보기 좋습니다.", "주변 노르만 궁전과 연계해 보세요."],
        ),
        AttractionSeed(
            name="Ballaro Market",
            lat=38.1124,
            lng=13.3625,
            categories=["food", "market"],
            visit_minutes=60,
            best_for=["food", "street_life"],
            area="Albergheria",
            summary="팔레르모의 다층적 음식 문화가 살아 있는 재래시장입니다.",
            history="중세 이후 상업 중심지로 기능하며 다양한 지중해 식재료가 유통되었습니다.",
            cultural_note="시칠리아의 일상성과 이주 문화의 흔적을 체감하기 좋은 현장입니다.",
            hours="주로 오전부터 이른 오후까지 활발",
            tips=["늦은 오후보다 오전 방문이 좋습니다.", "현금과 위생용 티슈를 챙기면 편합니다."],
        ),
    ],
    "catania": [
        AttractionSeed(
            name="Piazza del Duomo",
            lat=37.5025,
            lng=15.0873,
            categories=["landmark", "walk"],
            visit_minutes=30,
            best_for=["first_time", "photo_spot"],
            area="Historic Center",
            summary="카타니아의 바로크 도심과 상징 분수, 대성당이 모이는 중심 광장입니다.",
            history="1693년 대지진 이후 바로크 재건 도시의 중심으로 정비되었습니다.",
            cultural_note="검은 용암석 도시라는 카타니아의 질감을 가장 잘 느낄 수 있습니다.",
            hours="상시 외부 관람 가능",
            tips=["아침 광장 산책 후 시장으로 넘어가기 좋습니다.", "해 질 무렵 조명도 좋습니다."],
        ),
        AttractionSeed(
            name="La Pescheria",
            lat=37.5018,
            lng=15.0867,
            categories=["market", "food"],
            visit_minutes=45,
            best_for=["food", "street_life"],
            area="Historic Center",
            summary="시칠리아 동부 항구 도시의 식재료 감각을 보여주는 활기찬 어시장입니다.",
            history="항구와 도시 생활이 직접 맞닿은 전통 시장 공간입니다.",
            cultural_note="소리, 냄새, 방언이 뒤섞인 현장감이 강합니다.",
            hours="대체로 오전 방문 추천",
            tips=["비수기에도 신발은 미끄럽지 않은 것이 좋습니다.", "시장 후 해산물 점심으로 이어가기 좋습니다."],
        ),
    ],
    "valletta": [
        AttractionSeed(
            name="St. John's Co-Cathedral",
            lat=35.8989,
            lng=14.5125,
            categories=["art", "religion"],
            visit_minutes=75,
            best_for=["art", "history"],
            area="Valletta Core",
            summary="기사단의 권위와 바로크 미학이 응축된 몰타 최고의 실내 명소입니다.",
            history="성 요한 기사단 시대에 건립되었고, 카라바조 작품으로도 유명합니다.",
            cultural_note="소박한 외관과 대조되는 화려한 내부 장식이 강한 인상을 남깁니다.",
            hours="일요일 및 종교 행사 시 관광 제한 가능",
            tips=["오디오 가이드를 활용하면 만족도가 높습니다.", "복장 규정을 확인하세요."],
        ),
        AttractionSeed(
            name="Upper Barrakka Gardens",
            lat=35.8978,
            lng=14.5111,
            categories=["viewpoint", "walk"],
            visit_minutes=30,
            best_for=["night_view", "photo_spot"],
            area="Valletta Core",
            summary="그랜드 하버를 내려다보는 발레타 최고의 전망 포인트입니다.",
            history="기사단의 여가 정원에서 출발해 현재는 대표 공공 전망 공간이 되었습니다.",
            cultural_note="몰타가 군사 요새 도시였다는 점을 직관적으로 보여줍니다.",
            hours="상시 접근 가능, 포성 행사 시간은 별도 확인",
            tips=["정오 포성 시연 시간을 맞추면 재미있습니다.", "햇빛이 강해 오후 늦게가 쾌적합니다."],
        ),
    ],
}


DEFAULT_CITY_CENTER = {
    "rome": (41.9028, 12.4964),
    "florence": (43.7696, 11.2558),
    "venice": (45.4408, 12.3155),
    "milan": (45.4642, 9.19),
    "naples": (40.8518, 14.2681),
    "palermo": (38.1157, 13.3615),
    "catania": (37.5079, 15.0830),
    "valletta": (35.8989, 14.5146),
}


PACE_ACTIVITY_TARGET = {
    "relaxed": 2,
    "balanced": 3,
    "intensive": 4,
}


CITY_TRAVEL_HINTS = {
    ("rome", "palermo"): {"mode": "night_train", "duration_minutes": 720},
    ("rome", "catania"): {"mode": "night_train", "duration_minutes": 750},
    ("palermo", "valletta"): {"mode": "flight_or_ferry_combo", "duration_minutes": 300},
    ("catania", "valletta"): {"mode": "flight", "duration_minutes": 120},
    ("rome", "florence"): {"mode": "high_speed_train", "duration_minutes": 95},
    ("florence", "venice"): {"mode": "high_speed_train", "duration_minutes": 135},
    ("venice", "milan"): {"mode": "high_speed_train", "duration_minutes": 150},
    ("milan", "naples"): {"mode": "high_speed_train", "duration_minutes": 280},
}


def slugify_city(value: str) -> str:
    return value.strip().lower().replace(".", "").replace("'", "")


def title_case_city(value: str) -> str:
    return value.strip().title()


def parse_iso_date(value: str | None) -> date | None:
    if not value:
        return None
    return datetime.fromisoformat(value).date()


def parse_clock(value: str) -> datetime:
    return datetime.strptime(value, "%H:%M")


def add_minutes(time_value: str, minutes: int) -> str:
    base = parse_clock(time_value)
    return (base + timedelta(minutes=minutes)).strftime("%H:%M")


def duration_label(minutes: int) -> str:
    hours, mins = divmod(minutes, 60)
    if hours and mins:
        return f"{hours}h {mins}m"
    if hours:
        return f"{hours}h"
    return f"{mins}m"


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    radius_km = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lng / 2) ** 2
    )
    return 2 * radius_km * math.asin(math.sqrt(a))


def infer_local_mode(distance_km: float, preference: str) -> str:
    if distance_km <= 1.2:
        return "walk"
    if distance_km <= 4.5:
        return "walk" if preference == "walk" else "metro_or_taxi"
    return "metro_or_taxi"


def estimate_leg_minutes(distance_km: float, mode: str) -> int:
    speeds = {
        "walk": 4.5,
        "metro_or_taxi": 18.0,
        "bike": 12.0,
        "car": 25.0,
    }
    speed = speeds.get(mode, 18.0)
    rolling = max(5, round(distance_km / speed * 60))
    buffer = 3 if mode == "walk" else 8
    return rolling + buffer


def get_city_catalog(city: str) -> list[AttractionSeed]:
    return CATALOG.get(slugify_city(city), [])


def city_center(city: str) -> tuple[float, float]:
    return DEFAULT_CITY_CENTER.get(slugify_city(city), (41.9028, 12.4964))


def search_catalog_attraction(city: str, attraction_name: str) -> AttractionSeed | None:
    city_items = get_city_catalog(city)
    normalized = attraction_name.strip().lower()
    for item in city_items:
        if item.name.lower() == normalized:
            return item
    for item in city_items:
        if normalized in item.name.lower() or item.name.lower() in normalized:
            return item
    return None


def fallback_attraction(city: str, attraction_name: str) -> AttractionSeed:
    lat, lng = city_center(city)
    return AttractionSeed(
        name=attraction_name,
        lat=lat,
        lng=lng,
        categories=["landmark"],
        visit_minutes=60,
        best_for=["general"],
        area=f"{title_case_city(city)} center",
        summary=f"{attraction_name}은(는) {title_case_city(city)} 일정에 넣기 좋은 대표 방문지입니다.",
        history="세부 데이터가 내장 카탈로그에 없어서 일반 설명 템플릿으로 생성되었습니다.",
        cultural_note="도시 맥락과 현장 분위기를 기준으로 방문 시간을 조절하는 것이 좋습니다.",
        hours="공식 사이트 확인 권장",
        tips=["최신 운영 시간과 휴관일은 공식 채널에서 재확인하세요."],
    )


def pick_daily_attractions(
    city: str,
    requested: list[str] | None,
    interests: list[str],
    pace: str,
    day_index: int,
) -> list[dict[str, Any]]:
    items = get_city_catalog(city)
    requested = requested or []
    chosen: list[AttractionSeed] = []
    seen: set[str] = set()

    for name in requested:
        found = search_catalog_attraction(city, name)
        if found and found.name not in seen:
            chosen.append(found)
            seen.add(found.name)

    target = PACE_ACTIVITY_TARGET.get(pace, 3)
    scored = []
    for item in items:
        if item.name in seen:
            continue
        score = 0
        for interest in interests:
            if interest in item.categories or interest in item.best_for:
                score += 3
        score += 2 if "first_time" in item.best_for and day_index == 1 else 0
        score += 1 if any(cat in ("landmark", "history", "art") for cat in item.categories) else 0
        scored.append((score, item))

    scored.sort(key=lambda entry: (-entry[0], entry[1].name))
    for _, item in scored[: max(0, target - len(chosen))]:
        chosen.append(item)
        seen.add(item.name)

    return [attraction_to_dict(item) for item in chosen]


def attraction_to_dict(item: AttractionSeed) -> dict[str, Any]:
    return {
        "name": item.name,
        "coordinates": {"lat": item.lat, "lng": item.lng},
        "categories": item.categories,
        "recommended_visit_minutes": item.visit_minutes,
        "area": item.area,
        "summary": item.summary,
    }


def split_days_across_cities(
    cities: list[dict[str, Any]],
    total_days: int | None,
) -> list[int]:
    explicit_days = [city.get("days") or city.get("nights") for city in cities]
    if total_days is None:
        total_days = sum(day for day in explicit_days if isinstance(day, int)) or len(cities)

    allocations = []
    remaining = total_days
    unspecified_indexes = []
    for idx, city in enumerate(cities):
        value = city.get("days")
        if value is None:
            nights = city.get("nights")
            value = nights + 1 if isinstance(nights, int) and nights > 0 else None
        if isinstance(value, int) and value > 0:
            allocations.append(value)
            remaining -= value
        else:
            allocations.append(None)
            unspecified_indexes.append(idx)

    if unspecified_indexes:
        even = max(1, remaining // len(unspecified_indexes)) if remaining > 0 else 1
        for idx in unspecified_indexes:
            allocations[idx] = even
        leftover = total_days - sum(int(x) for x in allocations if x is not None)
        cursor = 0
        while leftover > 0:
            allocations[unspecified_indexes[cursor % len(unspecified_indexes)]] += 1
            leftover -= 1
            cursor += 1

    return [int(value or 1) for value in allocations]


def compute_total_days(request: dict[str, Any]) -> int:
    start = parse_iso_date(request.get("start_date"))
    end = parse_iso_date(request.get("end_date"))
    if start and end:
        return (end - start).days + 1
    if isinstance(request.get("days"), int):
        return int(request["days"])
    if isinstance(request.get("nights"), int):
        return int(request["nights"]) + 1
    return max(1, len(request.get("cities", [])))


def build_transport_leg(origin: str, destination: str, fixed_legs: list[dict[str, Any]]) -> dict[str, Any]:
    for leg in fixed_legs:
        if slugify_city(leg.get("from", "")) == slugify_city(origin) and slugify_city(leg.get("to", "")) == slugify_city(destination):
            mode = leg.get("mode", "custom")
            minutes = int(leg.get("duration_minutes", CITY_TRAVEL_HINTS.get((slugify_city(origin), slugify_city(destination)), {}).get("duration_minutes", 180)))
            return {
                "from": title_case_city(origin),
                "to": title_case_city(destination),
                "mode": mode,
                "duration_minutes": minutes,
                "duration_label": duration_label(minutes),
                "notes": leg.get("notes", ""),
                "source": "user_fixed_leg",
            }

    hint = CITY_TRAVEL_HINTS.get((slugify_city(origin), slugify_city(destination)))
    if hint:
        return {
            "from": title_case_city(origin),
            "to": title_case_city(destination),
            "mode": hint["mode"],
            "duration_minutes": hint["duration_minutes"],
            "duration_label": duration_label(hint["duration_minutes"]),
            "notes": "내장 교통 휴리스틱",
            "source": "heuristic",
        }

    return {
        "from": title_case_city(origin),
        "to": title_case_city(destination),
        "mode": "train_or_flight",
        "duration_minutes": 180,
        "duration_label": duration_label(180),
        "notes": "실시간 교통 데이터 미연동 상태의 기본 추정치",
        "source": "fallback",
    }


def build_city_summary(city: str, day_count: int, interests: list[str]) -> str:
    interests_text = ", ".join(interests) if interests else "핵심 랜드마크"
    return f"{title_case_city(city)}에서 {day_count}일 동안 {interests_text} 중심으로 무리 없는 흐름을 잡은 일정입니다."


async def brave_search(query: str, count: int = 3) -> list[dict[str, str]]:
    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        return []

    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": api_key,
    }
    params = {
        "q": query,
        "count": count,
        "search_lang": "en",
        "country": "us",
        "spellcheck": 1,
    }
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
    except Exception:
        return []

    results = []
    for item in data.get("web", {}).get("results", [])[:count]:
        results.append(
            {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "description": item.get("description", ""),
            }
        )
    return results


def build_osm_link(stops: list[dict[str, Any]]) -> str:
    if not stops:
        return ""
    markers = []
    for stop in stops:
        coord = stop.get("coordinates") or {}
        if "lat" in coord and "lng" in coord:
            markers.append(f"marker={coord['lat']}%2C{coord['lng']}")
    if not markers:
        return ""
    return "https://www.openstreetmap.org/?" + "&".join(markers)


def build_osm_place_link(stop: dict[str, Any], zoom: int = 17) -> str:
    coord = stop.get("coordinates") or {}
    if "lat" not in coord or "lng" not in coord:
        return ""
    lat = coord["lat"]
    lng = coord["lng"]
    return f"https://www.openstreetmap.org/?mlat={lat}&mlon={lng}#map={zoom}/{lat}/{lng}"


def build_osm_direction_links(stops: list[dict[str, Any]], travel_mode: str) -> list[dict[str, Any]]:
    engine_map = {
        "walking": "fossgis_osrm_foot",
        "walk": "fossgis_osrm_foot",
        "driving": "fossgis_osrm_car",
        "car": "fossgis_osrm_car",
        "cycling": "fossgis_osrm_bike",
        "bike": "fossgis_osrm_bike",
    }
    engine = engine_map.get(travel_mode, "fossgis_osrm_foot")
    links = []
    for idx in range(len(stops) - 1):
        start = stops[idx]
        end = stops[idx + 1]
        s = start["coordinates"]
        e = end["coordinates"]
        links.append(
            {
                "from": start["name"],
                "to": end["name"],
                "url": (
                    "https://www.openstreetmap.org/directions?"
                    f"engine={engine}&route={s['lat']},{s['lng']};{e['lat']},{e['lng']}"
                ),
            }
        )
    return links


def build_geo_uri(stop: dict[str, Any]) -> str:
    coord = stop.get("coordinates") or {}
    if "lat" not in coord or "lng" not in coord:
        return ""
    label = quote(stop.get("name", "stop"))
    return f"geo:{coord['lat']},{coord['lng']}?q={coord['lat']},{coord['lng']}({label})"


def build_route_geojson(city: str, stops: list[dict[str, Any]]) -> dict[str, Any]:
    features = []
    line_coordinates = []
    for index, stop in enumerate(stops, start=1):
        coord = stop["coordinates"]
        line_coordinates.append([coord["lng"], coord["lat"]])
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "city": title_case_city(city),
                    "sequence": index,
                    "name": stop["name"],
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [coord["lng"], coord["lat"]],
                },
            }
        )

    if line_coordinates:
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "city": title_case_city(city),
                    "feature_type": "route_line",
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": line_coordinates,
                },
            }
        )

    return {
        "type": "FeatureCollection",
        "features": features,
    }


def build_day_narrative(city: str, attractions: list[dict[str, Any]], pace: str) -> str:
    names = ", ".join(item["name"] for item in attractions[:3])
    return f"{title_case_city(city)}의 하루를 {pace}한 리듬으로 구성했고, 핵심 축은 {names}입니다."


mcp = FastMCP(
    "yeye-tour-mcp",
    instructions="Create rich travel plans, optimize routes, and return frontend-ready JSON for a digital guidebook.",
    stateless_http=True,
    json_response=True,
)


@mcp.tool()
async def plan_trip(request: dict[str, Any]) -> dict[str, Any]:
    """도시 목록과 날짜를 받아 장기 일정까지 대응 가능한 여행 뼈대 일정을 JSON으로 생성합니다."""
    cities = request.get("cities", [])
    if not cities:
        return {
            "ok": False,
            "error": "At least one city is required.",
            "input_echo": request,
        }

    start_date = parse_iso_date(request.get("start_date"))
    total_days = compute_total_days(request)
    traveler_profile = request.get("traveler_profile", {})
    pace = traveler_profile.get("pace", "balanced")
    interests = traveler_profile.get("interests", ["history", "food", "architecture"])
    fixed_legs = request.get("fixed_legs", [])
    allocations = split_days_across_cities(cities, total_days)

    current_date = start_date
    city_segments = []
    daily_plan = []
    transport_plan = []

    for city_index, city in enumerate(cities):
        city_name = city["name"]
        allocated_days = allocations[city_index]
        segment_start = current_date
        segment_end = current_date + timedelta(days=allocated_days - 1) if current_date else None
        if city_index > 0:
            leg = build_transport_leg(cities[city_index - 1]["name"], city_name, fixed_legs)
            transport_plan.append(leg)

        city_segments.append(
            {
                "city": title_case_city(city_name),
                "days": allocated_days,
                "nights": max(allocated_days - 1, city.get("nights", 0)),
                "start_date": segment_start.isoformat() if segment_start else None,
                "end_date": segment_end.isoformat() if segment_end else None,
                "summary": build_city_summary(city_name, allocated_days, interests),
                "arrival": city.get("arrival", {}),
                "departure": city.get("departure", {}),
                "notes": city.get("notes", ""),
            }
        )

        for local_day in range(allocated_days):
            day_date = current_date.isoformat() if current_date else None
            requested = city.get("must_visit") if local_day == 0 else city.get("secondary_visit")
            attractions = pick_daily_attractions(
                city=city_name,
                requested=requested,
                interests=interests,
                pace=pace,
                day_index=local_day + 1,
            )
            daily_plan.append(
                {
                    "day_number": len(daily_plan) + 1,
                    "date": day_date,
                    "city": title_case_city(city_name),
                    "theme": city.get("theme") or f"{title_case_city(city_name)} highlights",
                    "narrative": build_day_narrative(city_name, attractions, pace),
                    "pace": pace,
                    "morning": attractions[:1],
                    "afternoon": attractions[1:3],
                    "evening": attractions[3:4],
                    "meal_hint": city.get("meal_hint", f"{title_case_city(city_name)} local classics"),
                    "hotel_area": city.get("hotel_area", "central"),
                    "custom_notes": city.get("notes", ""),
                }
            )
            if current_date:
                current_date += timedelta(days=1)

    return {
        "ok": True,
        "trip_name": request.get("trip_name", "Custom Trip"),
        "summary": {
            "start_date": request.get("start_date"),
            "end_date": request.get("end_date"),
            "days": total_days,
            "city_count": len(cities),
            "pace": pace,
            "interests": interests,
        },
        "traveler_profile": traveler_profile,
        "city_segments": city_segments,
        "transport_plan": transport_plan,
        "daily_plan": daily_plan,
        "input_echo": request,
        "meta": {
            "engine": "heuristic-v1",
            "supports_fixed_legs": True,
            "frontend_ready": True,
        },
    }


@mcp.tool()
async def optimize_daily_route(
    city: str,
    stops: list[dict[str, Any]],
    start_time: str = "09:00",
    start_location: dict[str, Any] | None = None,
    end_location: dict[str, Any] | None = None,
    travel_mode_preference: str = "walk",
) -> dict[str, Any]:
    """특정 도시 내 방문지 목록을 동선상 가장 효율적인 순서로 정렬하고 이동 시간을 계산합니다."""
    if not stops:
        return {"ok": False, "error": "At least one stop is required.", "city": city}

    working = []
    for stop in stops:
        name = stop.get("name", "Unnamed stop")
        seed = search_catalog_attraction(city, name) or fallback_attraction(city, name)
        merged = attraction_to_dict(seed)
        merged.update(deepcopy(stop))
        if "coordinates" not in merged:
            merged["coordinates"] = {"lat": seed.lat, "lng": seed.lng}
        if "recommended_visit_minutes" not in merged:
            merged["recommended_visit_minutes"] = seed.visit_minutes
        working.append(merged)

    if start_location and start_location.get("coordinates"):
        current = start_location["coordinates"]
    else:
        lat, lng = city_center(city)
        current = {"lat": lat, "lng": lng}

    remaining = working[:]
    ordered = []
    while remaining:
        next_stop = min(
            remaining,
            key=lambda stop: haversine_km(
                current["lat"],
                current["lng"],
                stop["coordinates"]["lat"],
                stop["coordinates"]["lng"],
            ),
        )
        ordered.append(next_stop)
        current = next_stop["coordinates"]
        remaining.remove(next_stop)

    itinerary = []
    current_time = start_time
    previous_point = start_location or {
        "name": f"{title_case_city(city)} center",
        "coordinates": {"lat": city_center(city)[0], "lng": city_center(city)[1]},
    }
    total_transit_minutes = 0
    total_visit_minutes = 0

    for idx, stop in enumerate(ordered, start=1):
        distance = haversine_km(
            previous_point["coordinates"]["lat"],
            previous_point["coordinates"]["lng"],
            stop["coordinates"]["lat"],
            stop["coordinates"]["lng"],
        )
        mode = infer_local_mode(distance, travel_mode_preference)
        leg_minutes = estimate_leg_minutes(distance, mode)
        arrival_time = add_minutes(current_time, leg_minutes)
        visit_minutes = int(stop.get("recommended_visit_minutes", 60))
        depart_time = add_minutes(arrival_time, visit_minutes)
        itinerary.append(
            {
                "sequence": idx,
                "stop": stop["name"],
                "area": stop.get("area"),
                "coordinates": stop["coordinates"],
                "travel_from_previous": {
                    "from": previous_point["name"],
                    "mode": mode,
                    "distance_km": round(distance, 2),
                    "duration_minutes": leg_minutes,
                    "duration_label": duration_label(leg_minutes),
                },
                "arrival_time": arrival_time,
                "suggested_visit_minutes": visit_minutes,
                "departure_time": depart_time,
                "summary": stop.get("summary", ""),
            }
        )
        total_transit_minutes += leg_minutes
        total_visit_minutes += visit_minutes
        current_time = depart_time
        previous_point = {"name": stop["name"], "coordinates": stop["coordinates"]}

    final_leg = None
    if end_location and end_location.get("coordinates"):
        distance = haversine_km(
            previous_point["coordinates"]["lat"],
            previous_point["coordinates"]["lng"],
            end_location["coordinates"]["lat"],
            end_location["coordinates"]["lng"],
        )
        mode = infer_local_mode(distance, travel_mode_preference)
        leg_minutes = estimate_leg_minutes(distance, mode)
        final_leg = {
            "from": previous_point["name"],
            "to": end_location.get("name", "end"),
            "mode": mode,
            "distance_km": round(distance, 2),
            "duration_minutes": leg_minutes,
            "duration_label": duration_label(leg_minutes),
        }
        total_transit_minutes += leg_minutes

    optimized_stops = [
        {
            "name": item["stop"],
            "coordinates": item["coordinates"],
        }
        for item in itinerary
    ]
    map_links = {
        "openstreetmap_overview": build_osm_link(optimized_stops),
        "openstreetmap_leg_directions": build_osm_direction_links(optimized_stops, travel_mode_preference),
        "geo_uris": [build_geo_uri(stop) for stop in optimized_stops],
        "geojson": build_route_geojson(city, optimized_stops),
    }

    return {
        "ok": True,
        "city": title_case_city(city),
        "start_time": start_time,
        "travel_mode_preference": travel_mode_preference,
        "optimized_route": itinerary,
        "final_leg": final_leg,
        "totals": {
            "stops": len(itinerary),
            "visit_minutes": total_visit_minutes,
            "transit_minutes": total_transit_minutes,
            "day_minutes": total_visit_minutes + total_transit_minutes,
            "day_label": duration_label(total_visit_minutes + total_transit_minutes),
        },
        "map_links": map_links,
    }


@mcp.tool()
async def get_attraction_wiki(
    city: str,
    attraction_name: str,
    include_live_data: bool = True,
) -> dict[str, Any]:
    """관광지의 역사, 문화 배경, 운영 정보, 실전 팁을 풍부한 JSON으로 반환합니다."""
    seed = search_catalog_attraction(city, attraction_name) or fallback_attraction(city, attraction_name)
    live_sources = []
    latest_notes = []
    if include_live_data:
        query = f"{seed.name} {title_case_city(city)} opening hours tips"
        live_sources = await brave_search(query)
        latest_notes = [item["description"] for item in live_sources if item.get("description")]

    return {
        "ok": True,
        "city": title_case_city(city),
        "attraction": {
            "name": seed.name,
            "coordinates": {"lat": seed.lat, "lng": seed.lng},
            "area": seed.area,
            "categories": seed.categories,
            "recommended_visit_minutes": seed.visit_minutes,
        },
        "editorial": {
            "summary": seed.summary,
            "history": seed.history,
            "cultural_context": seed.cultural_note,
            "best_time_to_visit": "오전 첫 입장 또는 해 질 무렵이 일반적으로 가장 쾌적합니다.",
            "operating_hours_note": seed.hours,
            "pro_tips": seed.tips,
        },
        "live_updates": {
            "enabled": include_live_data,
            "provider": "Brave Search" if include_live_data and os.getenv("BRAVE_API_KEY") else "embedded_only",
            "notes": latest_notes[:3],
            "sources": live_sources,
        },
        "map_links": {
            "openstreetmap": build_osm_place_link(
                {"name": seed.name, "coordinates": {"lat": seed.lat, "lng": seed.lng}}
            ),
            "geo_uri": build_geo_uri(
                {"name": seed.name, "coordinates": {"lat": seed.lat, "lng": seed.lng}}
            ),
        },
    }


@mcp.tool()
async def generate_map_links(
    city: str,
    stops: list[dict[str, Any]],
    travel_mode: str = "walking",
) -> dict[str, Any]:
    """최적화된 경로 또는 임의 방문지 목록을 기반으로 다중 목적지 지도 URL을 생성합니다."""
    normalized = []
    for stop in stops:
        name = stop.get("name", "Unnamed stop")
        seed = search_catalog_attraction(city, name) or fallback_attraction(city, name)
        normalized.append(
            {
                "name": name,
                "coordinates": stop.get("coordinates") or {"lat": seed.lat, "lng": seed.lng},
            }
        )

    return {
        "ok": True,
        "city": title_case_city(city),
        "stop_count": len(normalized),
        "stops": normalized,
        "travel_mode": travel_mode,
        "links": {
            "openstreetmap_overview": build_osm_link(normalized),
            "openstreetmap_leg_directions": build_osm_direction_links(normalized, travel_mode),
            "openstreetmap_place_links": [
                {
                    "name": stop["name"],
                    "url": build_osm_place_link(stop),
                }
                for stop in normalized
            ],
            "geo_uris": [
                {
                    "name": stop["name"],
                    "uri": build_geo_uri(stop),
                }
                for stop in normalized
            ],
            "geojson": build_route_geojson(city, normalized),
        },
    }


def main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "streamable-http").strip().lower()
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    try:
        mcp.run(transport="streamable-http", host=host, port=port)
    except TypeError:
        mcp.run(transport="streamable-http")
        
    if transport == "stdio":
        mcp.run()
        return
    else:
        # streamable-http와 sse 모두 아래 방식으로 호스트 바인딩이 가능합니다.
        # 에러가 난다면 except로 숨기지 말고 로그를 찍어야 원인을 알 수 있습니다.
        mcp.run(
            transport=transport,
            host=host,
            port=port
        )

if __name__ == "__main__":
    main()
