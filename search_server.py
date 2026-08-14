from fastmcp import FastMCP
from ddgs import DDGS
import asyncio

mcp = FastMCP("search")


@mcp.tool()
async def web_search(query: str) -> str:
    """
    Search the internet using DuckDuckGo.

    Use this tool for current information, recent news,
    latest events, or information that may have changed recently.
    """

    results = await asyncio.to_thread(
        lambda: DDGS().text(query, max_results=5)
    )

    return str(results)


if __name__ == "__main__":
    mcp.run()