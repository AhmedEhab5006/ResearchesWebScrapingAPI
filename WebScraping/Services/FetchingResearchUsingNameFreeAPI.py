import asyncio
import math
import urllib.parse
import threading
from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext
from ..Repos.ResearchRepo import ResarchRepo
from ..Repos.ResearcherResearchRepo import ResearcherResearchRepo
from ..models.Research import Research
from ..models.Researcher import Researcher
from ..Enums.FetchingResearchValidation import FetchingResearchValidation

PLATFORMS = {
    "Semantic Scholar": {
        "base_url": "https://www.semanticscholar.org/search?q=",
        "item_selector": "div.cl-paper-row",
        "title": "h2 a",
        "url": "h2 a",
        "authors_year": ".author-list",
        "snippet": None,
        "results_per_page": 10
    },
    "PubMed": {
        "base_url": "https://pubmed.ncbi.nlm.nih.gov/?term=",
        "item_selector": "article.full-docsum",
        "title": "a.docsum-title",
        "url": "a.docsum-title",
        "authors_year": ".full-authors",
        "snippet": ".full-journal-citation",
        "results_per_page": 10
    }
}


class FetchingResearchUsingNameFreeAPI:

    @classmethod
    async def fetch_and_store_works(cls, name: str, researcher_id=None, max_results=50, batch_size=10):
        try:
            research_repo = ResarchRepo()
            researcher_research_repo = ResearcherResearchRepo()
            collected_papers = []
            count = 0

            if researcher_id and not Researcher.objects.filter(Id=researcher_id).exists():
                return FetchingResearchValidation.ResearcherDoesnotExist

            for platform, config in PLATFORMS.items():
                results_per_page = config.get("results_per_page", 10)
                total_pages = math.ceil(max_results / results_per_page)
                urls_to_crawl = []

                for page_num in range(total_pages):
                    urls_to_crawl.append(f"{config['base_url']}{urllib.parse.quote(name)}&page={page_num + 1}")

                crawler = PlaywrightCrawler(
                    max_requests_per_crawl=batch_size,
                    headless=True,
                    browser_type="firefox"
                )

                @crawler.router.default_handler
                async def handle_page(context: PlaywrightCrawlingContext):
                    try:
                        await context.page.wait_for_selector(config['item_selector'], timeout=5000)
                    except:
                        return

                    js_mapping = f"""
                    elements => elements.map(e => {{
                        return {{
                            title: e.querySelector("{config['title']}")?.textContent?.trim(),
                            url: e.querySelector("{config['url']}")?.href,
                            authors_year: e.querySelector("{config['authors_year']}")?.textContent?.trim(),
                            snippet: {f'e.querySelector("{config["snippet"]}")?.textContent?.trim()' if config.get("snippet") else "null"},
                            source: "{platform}"
                        }};
                    }})
                    """
                    items = await context.page.eval_on_selector_all(config['item_selector'], js_mapping)
                    for item in items:
                        if not item["title"]:
                            continue

                        research_obj = Research.objects.filter(Link=item["url"]).first()
                        if not research_obj:
                            research_obj = Research.objects.create(
                                title=item["title"],
                                Link=item["url"],
                                Source=platform
                            )

                        if researcher_id:
                            researcher_research_repo.model.objects.get_or_create(
                                Researcher_id=researcher_id,
                                Research_id=research_obj.Id
                            )

                        collected_papers.append(research_obj)
                        nonlocal count
                        count += 1
                        if count >= max_results:
                            break

                for i in range(0, len(urls_to_crawl), batch_size):
                    batch_urls = urls_to_crawl[i:i + batch_size]
                    print(f"[{platform}] Crawling batch {i // batch_size + 1} ({len(batch_urls)} URLs)...")
                    await crawler.run(batch_urls)

            return FetchingResearchValidation.Added

        except Exception as ex:
            print(f"Error fetching research: {ex}")
            return FetchingResearchValidation.ConnectionError

    @classmethod
    def fetch_and_store_works_sync(cls, name: str, researcher_id=None, max_results=50, batch_size=10):
        def run_async():
            asyncio.run(cls.fetch_and_store_works(name, researcher_id, max_results, batch_size))

        thread = threading.Thread(target=run_async)
        thread.start()
        thread.join()  
        return FetchingResearchValidation.Added