import hashlib
from rest_framework.throttling import SimpleRateThrottle


class ScholarNationalNumberThrottle(SimpleRateThrottle):
    scope = "scholar_nn"

    def get_cache_key(self, request, view):
        data = request.data if isinstance(request.data, dict) else {}
        nn = (data.get("researcherNationalNumber") or "").strip()

        if not nn:
            return None

        ident = hashlib.sha256(nn.encode("utf-8")).hexdigest()
        return self.cache_format % {"scope": self.scope, "ident": ident}


class ScholarProfileThrottle(SimpleRateThrottle):
    scope = "scholar_profile"

    def get_cache_key(self, request, view):
        data = request.data if isinstance(request.data, dict) else {}
        link = (data.get("scholarProfileLink") or "").strip()

        if not link:
            return None

        ident = hashlib.sha256(link.encode("utf-8")).hexdigest()
        return self.cache_format % {"scope": self.scope, "ident": ident}


class ScholarGlobalThrottle(SimpleRateThrottle):
    scope = "scholar_global"

    def get_cache_key(self, request, view):
        return self.cache_format % {"scope": self.scope, "ident": "global"}
