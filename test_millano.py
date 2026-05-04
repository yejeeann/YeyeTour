import asyncio
from server import get_attraction_wiki

async def main():
    print("=== Test Result for Mont-Blanc ===")
    result = await get_attraction_wiki("Mont-Blanc")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())