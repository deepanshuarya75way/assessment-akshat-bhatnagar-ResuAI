import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


AUTH_DIR = Path("app/auth")
STORAGE_STATE = AUTH_DIR / "storage_state.json"


class PlaywrightService:
    """
    Wrapper around Playwright.

    Responsibilities:
    - Reuse authenticated browser session
    - Open RecruitSage pages
    - Detect expired sessions
    - Extract HTML and visible text
    """

    async def _scrape_async(self, url: str) -> dict:

        async with async_playwright() as p:

            context = await p.chromium.launch_persistent_context(
                user_data_dir="app/auth/storage_state.json",
                headless=True
            )

            try:
                page=context.pages[0] if context.pages else await context.new_pages()
                
                print(page.url)
                print(await page.title())
                await page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=60000,
                )

                await page.wait_for_timeout(3000)
                print(page.url)
                print(await page.title())
                current_url = page.url.lower()

                if (
                    "login" in current_url
                    or "signin" in current_url
                    or "microsoftonline" in current_url
                ):

                  

                    raise Exception(
                        "RecruitSage session expired. "
                        "Run login_recruitsage.py again."
                    )

                html = await page.content()

                title = await page.title()

                with open(
                    "debug.html",
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(html)

                soup = BeautifulSoup(
                    html,
                    "html.parser",
                )

                text = soup.get_text(
                    separator="\n",
                    strip=True,
                )

                return {
                    "url": page.url,
                    "title": title,
                    "html": html,
                    "text": text,
                }

            finally:

                await context.close()

    def scrape(self, url: str) -> dict:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                lambda: asyncio.run(
                    self._scrape_async(url)
                )
            )
            return future.result()


playwright_service = PlaywrightService()
