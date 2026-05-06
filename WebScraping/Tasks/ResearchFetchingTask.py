from celery import shared_task, chord
from ..Services.FetchingResearchesByGoogleScholarProfileLink import (
    FetchingResearchesByProfileLinkGoogleScholarService
)
from .PublicationFetchingTask import fetch_publication_task
from .FinializingTask import finalize_fetch_task
from ..Services.CacheService import CacheService
import redis
from datetime import datetime, timezone, timedelta


cache_service = CacheService(default_timeout=60 * 15)
redis_client = redis.Redis(host="localhost", port=6379, db=0)

@shared_task(
    bind=True,
    rate_limit="1/m",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5}
)


def fetch_researches_task(self, profile_url: str, researcher_nationalNumber: str, orcid: str):
    service = FetchingResearchesByProfileLinkGoogleScholarService()
    cache_service.set(f"researcher:{researcher_nationalNumber}:scholar", profile_url , timeout=None)
    cache_service.set(f"researcher:{researcher_nationalNumber}:orcid", orcid , timeout=None)

    author = service.fetch_main_author(profile_url)

    publications = author.get("publications", [])
    coauthors = author.get("coauthors", [])
    total = len(publications)


    coauthors_data = [
        service.prepare_coauthor_data(coauthor)
        for coauthor in coauthors
    ]

    publication_jobs = [
        fetch_publication_task.s(
            pub,
            total,
            researcher_nationalNumber
        )        
        for pub in publications
    ]

    callback = finalize_fetch_task.s(
        profile_url=profile_url,
        researcher_nationalNumber=researcher_nationalNumber,
        orcid=orcid,
        author=author,
        coauthors_data=coauthors_data,
    )


    redis_client.set(f"research_counter:{researcher_nationalNumber}", 0)

    started_at = datetime.now().strftime("%I:%M %p")    
    progress_state = {
        "status": "in_progress",
        "current": 0,
        "total": total,
        "percentage": 0,
        "started_at": started_at,
        "estimated_finish": (
            datetime.now() + timedelta(minutes=total)
        ).strftime("%I:%M %p")  
    }

    cache_service.set(
        f"research_progress:{researcher_nationalNumber}",
        progress_state,
        timeout=None
    )

    if publication_jobs:
        chord(publication_jobs)(callback)
    else:
        finalize_fetch_task.delay(
            results=[],
            profile_url=profile_url,
            researcher_nationalNumber=researcher_nationalNumber,
            orcid=orcid,
            author=author,
            coauthors_data=coauthors_data,
        )

    return {
        "status": "dispatched",
        "publications_count": len(publications),
        "coauthors_count": len(coauthors_data),
    }