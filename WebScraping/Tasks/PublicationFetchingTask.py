from celery import shared_task
from ..Services.FetchingResearchesByGoogleScholarProfileLink import (
    FetchingResearchesByProfileLinkGoogleScholarService
)


@shared_task(
    bind=True,
    rate_limit="1/m",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5}
)
def fetch_publication_task(self, pub: dict):
    service = FetchingResearchesByProfileLinkGoogleScholarService()
    result = service.prepare_publication_data(pub)
    return {
        "type": "publication",
        "data": result,
    }