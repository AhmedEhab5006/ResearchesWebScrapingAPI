import random
import time
from typing import Any, Callable, Dict, List, Optional

from scholarly import scholarly


class ScholarClient:
    def __init__(self, min_delay: float = 4.0, max_delay: float = 10.0, max_retries: int = 5):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.max_retries = max_retries

    def _sleep(self):
        time.sleep(random.uniform(self.min_delay, self.max_delay))

    def call(self, fn: Callable[[], Any]) -> Any:
        last_err = None
        for attempt in range(self.max_retries):
            try:
                self._sleep()
                return fn()
            except Exception as e:
                last_err = e
                backoff = (2 ** attempt) + random.uniform(0, 1.5)
                time.sleep(backoff)
        raise last_err

    def fetch_author(self, author_id: str) -> Dict[str, Any]:
        try: 
            author = self.call(lambda: scholarly.search_author_id(author_id))
            author = self.call(lambda: scholarly.fill(author, sections=["basics", "indices", "counts" , "coauthors"]))
            author = self.call(lambda: scholarly.fill(author, sections=["publications"]))
            author = self.call(lambda: scholarly.fill(author))

            return author
        except Exception as e:
            print(e)

    def get_pub_url_fast(self, pub: Dict[str, Any]) -> Optional[str]:
        url = pub.get("pub_url")
        if url:
            return url

        author_pub_id = pub.get("author_pub_id")
        if author_pub_id:
            return (
                "https://scholar.google.com/citations?"
                f"view_op=view_citation&citation_for_view={author_pub_id}"
            )
        return None

    def fill_pub_if_needed(
        self,
        pub: Dict[str, Any],
        need_top_keys: Optional[List[str]] = None,
        need_bib_keys: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        need_top_keys = need_top_keys or []
        need_bib_keys = need_bib_keys or []

        bib = pub.get("bib") or {}

        missing = False

        for k in need_top_keys:
            v = pub.get(k)
            if v is None or v == "" or v == {}:
                missing = True
                break

        if not missing:
            for k in need_bib_keys:
                v = bib.get(k)
                if v is None or v == "":
                    missing = True
                    break

        if missing:
            return self.call(lambda: scholarly.fill(pub))  
        return pub
    
    
    
    def fill_author_if_needed(
        self,
        author: Dict[str, Any],
        need_keys: Optional[List[str]] = None,
    ) -> Dict[str, Any]:

        need_keys = need_keys or []

        missing = False

        for k in need_keys:
            v = author.get(k)
            if v is None or v == "" or v == {}:
                missing = True
                break

        if missing:
            return self.call(lambda: scholarly.fill(author))

        return author