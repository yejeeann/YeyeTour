from fastmcp import FastMCP

# YeyeTour MCP 서버 인스턴스 생성
mcp = FastMCP("YeyeTourServer")

@mcp.tool()
def plan_trip(cities: list[str], start_date: str, end_date: str) -> str:
    """
    도시 목록과 날짜를 입력받아 전체 뼈대 일정을 생성합니다.
    
    Args:
        cities: 방문할 도시 이름 목록 (예: ["Paris", "Rome"])
        start_date: 여행 시작 날짜 (YYYY-MM-DD 형식)
        end_date: 여행 종료 날짜 (YYYY-MM-DD 형식)
    """
    # TODO: 실제 일정 생성 로직 구현
    return f"{start_date}부터 {end_date}까지 {', '.join(cities)} 여행 일정을 계획합니다."

@mcp.tool()
def optimize_daily_route(locations: list[str]) -> str:
    """
    특정 도시 내의 방문지들을 가장 효율적인 순서로 정렬하고 동선을 최적화합니다.
    
    Args:
        locations: 방문할 장소 이름 목록 (예: ["Eiffel Tower", "Louvre Museum"])
    """
    # TODO: 실제 동선 최적화 로직 구현
    return f"다음 장소들의 동선을 최적화했습니다: {', '.join(locations)}"

@mcp.tool()
def get_attraction_wiki(attraction_name: str) -> str:
    """
    관광지의 역사, 문화적 배경, 운영 시간, 꿀팁 등 상세 설명을 제공합니다.
    
    Args:
        attraction_name: 관광지 이름 (예: "Eiffel Tower")
    """
    # TODO: 위키백과/관광지 정보 수집 로직 구현
    return f"{attraction_name}에 대한 상세 정보입니다."

@mcp.tool()
def generate_map_links(route: list[str]) -> str:
    """
    최적화된 경로를 바탕으로 구글 지도 다중 목적지(Multi-stop) 링크를 생성합니다.
    
    Args:
        route: 최적화된 순서대로 정렬된 방문 장소 목록
    """
    return f"구글 지도 링크: https://www.google.com/maps/dir/{'/'.join(route).replace(' ', '+')}"

if __name__ == "__main__":
    # MCP 서버 실행 (stdio 통신 모드)
    mcp.run()