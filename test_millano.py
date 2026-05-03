import asyncio
from opentripmap import get_opentripmap_info
from wikipedia import get_wikipedia_summary

async def main():
    result = await get_opentripmap_info("milano")
    print("=== Test Result for OpenTripMap (milano) ===")
    print(result)

    print("\n=== Test Result for Wikipedia (milano) ===")
    wiki_result = await get_wikipedia_summary("milano")
    print(wiki_result)

if __name__ == "__main__":
    asyncio.run(main())