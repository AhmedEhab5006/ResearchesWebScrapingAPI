import asyncio
import urllib.parse
import threading
from asgiref.sync import sync_to_async
from django.db import connections
from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext
from ..Repos.ResearchRepo import ResarchRepo
from ..Repos.ResearcherResearchRepo import ResearcherResearchRepo
from ..models.Research import Research
from ..models.Researcher import Researcher
from ..Enums.FetchingResearchValidation import FetchingResearchValidation

# Domains to exclude
EXCLUDE_DOMAINS = [
    "youtube.com", "facebook.com", "twitter.com", "linkedin.com", "instagram.com",
    "reddit.com", "tiktok.com", "pinterest.com"
]

# Domains considered as research sources
RESEARCH_DOMAINS = [
    "semanticscholar.org", "pubmed.ncbi.nlm.nih.gov", "researchgate.net", ".edu", ".ac"
]

class FetchingResearchUsingNameFreeAPI:

    @classmethod
    async def fetch_and_store_works(cls, name: str, researcher_id=None, max_results=50, batch_size=10, concurrency=3):
        """
        Fetch research links for a given name and store them in DB.
        Optimized for large numbers of results.
        """
        try:
            researcher_research_repo = ResearcherResearchRepo()
            collected_count = 0
            new_research_objs = []
            semaphore = asyncio.Semaphore(concurrency)

            # Check if researcher exists
            if researcher_id and not await sync_to_async(
                Researcher.objects.filter(Id=researcher_id).exists
            )():
                return FetchingResearchValidation.ResearcherDoesnotExist

            # Initialize Playwright crawler
            crawler = PlaywrightCrawler(headless=True, browser_type="chromium")

            # Default handler defined once
            @crawler.router.default_handler
            async def handle_google(context: PlaywrightCrawlingContext):
                nonlocal collected_count
                try:
                    await context.page.wait_for_selector('a', timeout=5000)
                except:
                    return

                links = await context.page.eval_on_selector_all(
                    'a',
                    """
                    elements => elements.map(e => e.href)
                        .filter(href => href && !href.includes('google.com') && !href.includes('/search?'))
                    """
                )

                # Filter links
                filtered_links = [
                    link for link in links
                    if not any(domain in link for domain in EXCLUDE_DOMAINS)
                ]

                research_links = [
                    link for link in filtered_links
                    if any(domain in link for domain in RESEARCH_DOMAINS)
                ]

                final_links = research_links if research_links else filtered_links

                for link in final_links:
                    if collected_count >= max_results:
                        return

                    existing = await sync_to_async(Research.objects.filter(Link=link).first)()
                    if not existing:
                        new_research_objs.append(Research(title=link, Link=link, Source="Google"))
                    else:
                        if researcher_id:
                            await sync_to_async(researcher_research_repo.model.objects.get_or_create)(
                                Researcher_id=researcher_id, Research_id=existing.Id
                            )

                    collected_count += 1
                    print(f"✅ Processed #{collected_count}: {link}")

                await asyncio.sleep(0.5)

            # Prepare Google search URLs for pagination
            urls_to_crawl = []
            pages_needed = (max_results + batch_size - 1) // batch_size
            for i in range(pages_needed):
                start = i * batch_size
                query = f'"{name}" research'
                url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&start={start}"
                urls_to_crawl.append(url)

            print(f"[Google] Searching for '{name}' across {pages_needed} pages...")

            # Add all URLs to the crawler
            await crawler.add_requests(urls_to_crawl)

            # Run crawler only once
            await crawler.run()

            # Bulk create new research objects
            if new_research_objs:
                await sync_to_async(Research.objects.bulk_create)(new_research_objs)

                # Link to researcher if researcher_id is given
                if researcher_id:
                    tasks = []
                    for obj in new_research_objs:
                        tasks.append(sync_to_async(researcher_research_repo.model.objects.get_or_create)(
                            Researcher_id=researcher_id, Research_id=obj.Id
                        ))
                    await asyncio.gather(*tasks)

            print(f"\n✅ Total collected and stored: {collected_count}")
            return FetchingResearchValidation.Added

        except Exception as ex:
            print(f"❌ Error fetching research: {ex}")
            return FetchingResearchValidation.ConnectionError

    @classmethod
    def fetch_and_store_works_sync(cls, name: str, researcher_id=None, max_results=50, batch_size=10):
        """
        Synchronous wrapper for Django views or APIs.
        """
        def run_async():
            connections.close_all()
            try:
                asyncio.run(cls.fetch_and_store_works(name, researcher_id, max_results, batch_size))
            finally:
                connections.close_all()

        thread = threading.Thread(target=run_async)
        thread.start()
        thread.join()
        return FetchingResearchValidation.Added


