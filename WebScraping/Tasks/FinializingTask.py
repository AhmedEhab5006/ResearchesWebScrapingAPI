from celery import shared_task
from ..Services.FetchingResearchesByGoogleScholarProfileLink import (
    FetchingResearchesByProfileLinkGoogleScholarService
)

from ..Services.CacheService import CacheService
import redis
import json
from datetime import datetime

redis_client = redis.Redis(host="localhost", port=6379, db=0)


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

    publications_data = [
        r.get("data") for r in (results or [])
        if r and r.get("type") == "publication"
    ]    
    cache_service = CacheService(default_timeout=60 * 15)

    progress_key = f"research_progress:{researcher_nationalNumber}"
    final_state = cache_service.get(progress_key) or {}

    final_state.update({
        "status": "completed",
        "current": final_state.get("total", 0),
        "percentage": 100,
        "finished_at": datetime.utcnow().isoformat()
    })

    cache_service.set(progress_key, final_state, timeout=None)

    redis_client.publish(
        f"research_progress:{researcher_nationalNumber}",
        json.dumps(final_state)
    )

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