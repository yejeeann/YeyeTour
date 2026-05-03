import httpx
import re

async def get_korean_title(title: str) -> str:
    """영문 위키백과 표제어를 한국어 위키백과 표제어로 변환합니다."""
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "langlinks",
        "titles": title,
        "lllang": "ko",
        "format": "json"
    }
    headers = {"User-Agent": "YeyeTour/1.0 (sdsclass)"}
    
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            resp = await client.get(url, params=params, headers=headers, timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                pages = data.get("query", {}).get("pages", {})
                for page_id, page_data in pages.items():
                    if "langlinks" in page_data:
                        return page_data["langlinks"][0]["*"]
    except Exception as e:
        print(f"Wikipedia langlinks API error for {title}: {e}")
    
    return title

async def correct_wikipedia_title(title: str) -> str:
    """위키백과 OpenSearch API를 사용하여 검색어의 오타를 교정하고 정확한 표제어를 찾습니다."""
    url = "https://ko.wikipedia.org/w/api.php"
    params = {
        "action": "opensearch",
        "search": title,
        "limit": 1,
        "namespace": 0,
        "format": "json"
    }
    headers = {"User-Agent": "YeyeTour/1.0 (sdsclass)"}
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            resp = await client.get(url, params=params, headers=headers, timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                if len(data) >= 2 and len(data[1]) > 0:
                    return data[1][0]  # 교정된 첫 번째 표제어 반환
    except Exception as e:
        print(f"Wikipedia OpenSearch API error for {title}: {e}")
    return title

async def get_wikipedia_summary(title: str) -> str:
    """Wikipedia 무료 API를 사용하여 장소의 요약 정보를 가져옵니다."""
    # 영문이 포함된 경우 한국어 표제어로 변환 시도
    if re.search(r'[a-zA-Z]', title):
        title = await get_korean_title(title)

    # 정확한 표제어로 검색어 교정 (오타 보완)
    title = await correct_wikipedia_title(title)

    url = f"https://ko.wikipedia.org/api/rest_v1/page/summary/{title}"
    headers = {"User-Agent": "YeyeTour/1.0 (sdsclass)"}
    
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            resp = await client.get(url, headers=headers, timeout=8.0)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("extract", f"{title}에 대한 요약 정보가 없습니다.")
            elif resp.status_code == 404:
                return f"{title}에 대한 문서를 찾을 수 없습니다. 외부 검색을 활용해보세요."
    except Exception as e:
        print(f"Wikipedia API error for {title}: {e}")
    return f"{title}에 대한 상세 정보가 제공되지 않았습니다."