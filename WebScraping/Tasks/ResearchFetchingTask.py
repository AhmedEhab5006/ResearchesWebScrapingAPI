from celery import shared_task
from ..Services.FetchingResearchesByGoogleScholarProfileLink import (
    FetchingResearchesByProfileLinkGoogleScholarService
)

@shared_task(bind=True)
def fetch_researches_task(self, profile_url: str, researcher_nationalNumber: str, orcid: str):
    result = FetchingResearchesByProfileLinkGoogleScholarService.fetch_and_store_works(
        profile_url=profile_url,
        researcher_nationalNumber=researcher_nationalNumber,
        orcid=orcid
    )
    return result
