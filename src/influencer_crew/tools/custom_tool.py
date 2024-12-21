from langchain.tools import BaseTool
from pydantic import Field
from playwright.async_api import async_playwright

class CrewAIScraperTool(BaseTool):
    """
    Custom CrewAI Tool to scrape influencer pages and extract relevant information like
    name, bio, followers count, and other key metrics from the page.
    """
    name: str = "crewAI_influencer_scraper"
    description: str = (
        "This tool scrapes influencer pages and returns structured information about the influencer. "
        "It extracts data such as name, bio, followers count, and relevant content from the page."
    )
    urls: list[str] = Field(default_factory=list)  # ✅ Proper Pydantic Field declaration

    async def _scrape_influencer_page(self, page, url):
        """
        Navigates to the influencer's page and extracts data such as bio, name, and followers.

        Args:
            page: The Playwright page instance.
            url: The URL of the page to scrape.

        Returns:
            dict: Extracted information from the page.
        """
        try:
            await page.goto(url, wait_until="domcontentloaded")
            # Example scraping logic (customize selectors as needed)
            name = await page.locator('meta[property="og:title"]').get_attribute('content')
            bio = await page.locator('meta[name="description"]').get_attribute('content')
            
            return {
                "url": url,
                "name": name.strip() if name else None,
                "bio": bio.strip() if bio else None,
            }
        except Exception as e:
            return {
                "url": url,
                "error": str(e)
            }

    async def _run(self, query: str):
        """
        Run the tool to scrape the URLs for influencer information.

        Args:
            query (str): This argument is required but not used since the tool scrapes a fixed set of URLs.

        Returns:
            list: A list of extracted information for each influencer.
        """
        results = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            for url in self.urls:  # ✅ self.urls is properly initialized
                print(f"Scraping URL: {url}")
                result = await self._scrape_influencer_page(page, url)
                results.append(result)
            
            await browser.close()
        
        return results

    async def _arun(self, query: str):
        """
        This async method runs the scraper asynchronously.

        Args:
            query (str): Required argument for async execution, not used here.

        Returns:
            list: A list of extracted influencer information.
        """
        return await self._run(query)


if __name__ == "__main__":
    import asyncio

    # ✅ List of influencer pages to scrape (replace with real URLs)
    urls = [
        "https://www.instagram.com/allisontenney/"
    ]

    # ✅ Create an instance of the CrewAI scraper tool using Pydantic's constructor
    scraper_tool = CrewAIScraperTool(urls=urls)  # Pass urls directly to the constructor

    # Run the tool and get results
    async def main():
        results = await scraper_tool._run(query="")
        print("Scraping Results:", results)

    asyncio.run(main())
