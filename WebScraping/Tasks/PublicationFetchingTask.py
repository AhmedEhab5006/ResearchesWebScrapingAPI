from celery import shared_task
from ..Services.FetchingResearchesByGoogleScholarProfileLink import (
    FetchingResearchesByProfileLinkGoogleScholarService
)
import json
import redis
from ..Services.CacheService import CacheService

redis_client = redis.Redis(host="redis", port=6379, db=0)
cache_service = CacheService(default_timeout=60 * 15)


@shared_task(
    bind=True,
    rate_limit="1/m",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5}
)
def fetch_publication_task(self, pub: dict, total: int, researcher: str):
    service = FetchingResearchesByProfileLinkGoogleScholarService()

    result = service.prepare_publication_data(pub)

    current = redis_client.incr(f"research_counter:{researcher}")

    percentage = int((current / total) * 100)

    old_data = cache_service.get(f"research_progress:{researcher}") or {}

    progress_data = {
        "status": "in_progress",
        "current": current,
        "total": total,
        "percentage": percentage,
        "started_at": old_data.get("started_at"),
        "estimated_finish": old_data.get("estimated_finish"),
    }

    cache_service.set(
        f"research_progress:{researcher}",
        progress_data,
        timeout=None
    )

    redis_client.publish(
        f"research_progress:{researcher}",
        json.dumps(progress_data)
    )

    return {
        "type": "publication",
        "data": result,
    }