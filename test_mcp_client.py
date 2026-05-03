import argparse
import asyncio
import json
import os
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


DEFAULT_MCP_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000/mcp")


def build_health_url(mcp_url: str) -> str:
    parsed = urlsplit(mcp_url)
    path = parsed.path.rstrip("/")
    if path.endswith("/mcp"):
        path = path[:-4] or ""
    health_path = f"{path}/health" if path else "/health"
    return urlunsplit((parsed.scheme, parsed.netloc, health_path, "", ""))


def pretty(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, default=str)


def summarize_tool_result(result: Any) -> str:
    structured = getattr(result, "structuredContent", None)
    if structured is not None:
        return pretty(structured)

    content = getattr(result, "content", None)
    if content is not None:
        blocks = []
        for item in content:
            text = getattr(item, "text", None)
            if text is not None:
                blocks.append(text)
            else:
                blocks.append(str(item))
        return "\n".join(blocks)

    if hasattr(result, "model_dump"):
        return pretty(result.model_dump())

    return str(result)


async def check_health(health_url: str) -> None:
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        response = await client.get(health_url)
        response.raise_for_status()
        print(f"[health] {health_url}")
        print(pretty(response.json()))


def default_plan_trip_payload() -> dict[str, Any]:
    return {
        "trip_name": "YeyeTour MCP Smoke Test",
        "start_date": "2026-10-01",
        "end_date": "2026-10-04",
        "cities": [
            {
                "name": "Rome",
                "nights": 2,
                "must_visit": ["Colosseum", "Pantheon"],
                "notes": "고대 로마 핵심 동선 확인",
            },
            {
                "name": "Florence",
                "nights": 1,
                "must_visit": ["Duomo di Firenze", "Uffizi Gallery"],
            },
        ],
        "traveler_profile": {
            "pace": "balanced",
            "interests": ["history", "architecture", "food"],
        },
    }


def full_test_cases() -> list[tuple[str, dict[str, Any]]]:
    return [
        ("plan_trip", {"request": default_plan_trip_payload()}),
        (
            "optimize_daily_route",
            {
                "city": "Rome",
                "stops": [
                    {"name": "Colosseum"},
                    {"name": "Pantheon"},
                    {"name": "Trevi Fountain"},
                ],
                "start_time": "09:00",
                "travel_mode_preference": "walk",
            },
        ),
        (
            "get_attraction_wiki",
            {
                "attraction_name": "Colosseum",
            },
        ),
        (
            "generate_map_links",
            {
                "city": "Rome",
                "stops": [
                    {"name": "Colosseum"},
                    {"name": "Pantheon"},
                    {"name": "Trevi Fountain"},
                ],
                "travel_mode": "walking",
            },
        ),
    ]


async def run_session(mcp_url: str, run_full_suite: bool) -> None:
    async with streamable_http_client(mcp_url) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            initialize_result = await session.initialize()
            print("[initialize]")
            if hasattr(initialize_result, "model_dump"):
                print(pretty(initialize_result.model_dump()))
            else:
                print(initialize_result)

            tools_response = await session.list_tools()
            tool_names = [tool.name for tool in tools_response.tools]
            print("\n[tools]")
            print(pretty(tool_names))

            tests = full_test_cases() if run_full_suite else [
                ("plan_trip", {"request": default_plan_trip_payload()})
            ]

            for tool_name, arguments in tests:
                print(f"\n[call_tool] {tool_name}")
                print("[arguments]")
                print(pretty(arguments))
                result = await session.call_tool(tool_name, arguments=arguments)
                print("[result]")
                print(summarize_tool_result(result))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Smoke-test the YeyeTour MCP server over streamable HTTP."
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_MCP_URL,
        help="MCP endpoint URL. Example: http://127.0.0.1:8000/mcp",
    )
    parser.add_argument(
        "--skip-health",
        action="store_true",
        help="Skip the /health HTTP check before opening the MCP session.",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run all YeyeTour tools instead of only the default plan_trip smoke test.",
    )
    return parser.parse_args()


async def async_main() -> int:
    args = parse_args()
    if not args.skip_health:
        await check_health(build_health_url(args.url))

    print(f"\n[mcp] {args.url}")
    await run_session(args.url, run_full_suite=args.full)
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(async_main()))


if __name__ == "__main__":
    main()
