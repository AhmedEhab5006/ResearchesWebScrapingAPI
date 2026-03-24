from celery import shared_task
from ..Services.FetchingResearchesByGoogleScholarProfileLink import (
    FetchingResearchesByProfileLinkGoogleScholarService
)

from ..Services.CacheService import CacheService


@shared_task(bind=True)
def finalize_fetch_task(
    self,
    results,
    profile_url: str,
    researcher_nationalNumber: str,
    orcid: str,
    author: dict,
    coauthors_data: list,
):
    service = FetchingResearchesByProfileLinkGoogleScholarService()

    publications_data = [r["data"] for r in results if r["type"] == "publication"]
    
    cache_service = CacheService(default_timeout=60 * 15)
    cache_service.delete(f"researcher:{researcher_nationalNumber}:scholar")
    cache_service.delete(f"researcher:{researcher_nationalNumber}:orcid")

    return service.save_all_to_db(
        profile_url=profile_url,
        orcid=orcid,
        researcher_nationalNumber=researcher_nationalNumber,
        author=author,
        publications_data=publications_data,
        coauthors_data=coauthors_data,
    )