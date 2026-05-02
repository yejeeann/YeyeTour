import httpx

async def get_wikipedia_summary(title: str) -> str:
    """Wikipedia 무료 API를 사용하여 장소의 요약 정보를 가져옵니다."""
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