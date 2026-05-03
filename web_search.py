import httpx
import re

async def get_duckduckgo_snippets(query: str) -> str:
    """DuckDuckGo HTML 검색을 통해 최신 웹 스니펫(무료)을 가져옵니다."""
    url = "https://html.duckduckgo.com/html/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    data = {"q": query}
    
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            resp = await client.post(url, headers=headers, data=data, timeout=8.0)
            if resp.status_code == 200:
                # 정규식을 사용하여 결과 스니펫 추출
                snippets = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', resp.text, re.IGNORECASE | re.DOTALL)
                
                if snippets:
                    # HTML 태그(<b>, </b> 등) 제거 및 공백 정리
                    clean_snippets = [re.sub(r'<[^>]+>', '', s).strip() for s in snippets[:3]]
                    result = "\n- ".join(clean_snippets)
                    return f"💡 최신 검색 꿀팁 및 운영 정보 (무료 웹 검색):\n- {result}"
    except Exception as e:
        print(f"Web search API error for {query}: {e}")
        
    return "💡 최신 검색 꿀팁: 무료 검색 서버 응답 지연으로 관련 정보를 가져오지 못했습니다."