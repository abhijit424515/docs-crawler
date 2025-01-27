import os
import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.models import MarkdownGenerationResult
from surrealdb import AsyncSurrealDB
from dotenv import load_dotenv


def setup_env():
    load_dotenv()
    for i in ["USERNAME", "PASSWORD", "URL", "DB", "NS"]:
        if os.getenv(i) is None:
            raise ValueError(f"[error] {i} env var not set")


async def crawl_page(url: str) -> str:
    x = None
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url)
        x = result.markdown

    if isinstance(x, MarkdownGenerationResult):
        x = x.fit_markdown
        x = x if x is not None else ""
    elif x is None:
        x = ""
    return x


async def save_markdown(data: str, url: str, db: AsyncSurrealDB):
    await db.insert("pages", {"url": url, "data": data})


async def main():
    setup_env()

    db = AsyncSurrealDB(os.getenv("URL"))
    await db.connect()
    await db.use(os.getenv("NS", ""), os.getenv("DB", ""))
    token = await db.sign_in(os.getenv("USERNAME", ""), os.getenv("PASSWORD", ""))
    await db.authenticate(token)

    z = await db.query("select url from pages;")
    urls = set()
    for x in z[0]["result"]:
        urls.add(x["url"])

    while True:
        url = input("> ")
        if url in ["exit", "quit", "q"]:
            break
        if url in urls:
            print("[skip] Already crawled")
            continue
        urls.add(url)
        markdown = await crawl_page(url)
        await save_markdown(markdown, url, db)

    await db.close()


if __name__ == "__main__":
    asyncio.run(main())
