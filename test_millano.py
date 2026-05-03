import asyncio
from server import get_attraction_wiki

async def main():
    result = await get_attraction_wiki("milano")
    print("=== Test Result for milano ===")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())