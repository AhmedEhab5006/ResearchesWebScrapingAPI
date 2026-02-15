from django.core.cache import cache

LOCK_TIMEOUT_SECONDS = 300  


def acquire_member_lock(national_number: str) -> bool:
    key = f"scholar:job:{national_number}"
    return cache.add(key, "1", timeout=LOCK_TIMEOUT_SECONDS)


def release_member_lock(national_number: str):
    key = f"scholar:job:{national_number}"
    cache.delete(key)
