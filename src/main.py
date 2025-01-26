import os
import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.models import MarkdownGenerationResult


async def crawl_page(url: str) -> str | MarkdownGenerationResult | None:
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url)
        return result.markdown


def save_markdown(markdown: str, url: str):
    url_path = "outputs/" + url.replace("https://", "").replace("http://", "")
    os.makedirs(url_path, exist_ok=True)

    file_path = f"{url_path}/index.md".replace("//", "/")
    with open(file_path, "w") as f:
        f.write(markdown)
    print(f"[SAVED] {file_path}")


async def main():
    url = input("> ")
    markdown = await crawl_page(url)

    if isinstance(markdown, MarkdownGenerationResult):
        x = markdown.fit_markdown
        x = x if x is not None else ""
        save_markdown(x, url)
    elif isinstance(markdown, str):
        save_markdown(markdown, url)


if __name__ == "__main__":
    asyncio.run(main())
