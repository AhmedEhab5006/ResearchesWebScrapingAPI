from typing import Any, Dict, List, Tuple
from itertools import zip_longest


def parse_coauthors(author_field, author_ids):
    names = []

    if not author_field:
        return []

    if isinstance(author_field, str):
        names = [a.strip() for a in author_field.split(" and ") if a.strip()]
    elif isinstance(author_field, list):
        names = [str(a).strip() for a in author_field if str(a).strip()]

    author_ids = author_ids or []

    coauthors = []

    for name, sid in zip_longest(names, author_ids, fillvalue=None):
        coauthors.append({
            "academic_name": name,
            "scholar_id": sid,
            "profile_url": (
                f"https://scholar.google.com/citations?hl=en&user={sid}"
                if sid else None
            )
        })

    return coauthors

def build_research_payload(
    *,
    title: str,
    pub_year: str,
    journal: str,
    publisher: str,
    no_of_citations: int,
    pages: str,
    volume: str,
    number: str,
    external_url: str,
    abstract: str,
    related_pub_url: str | None,
    contributions_payload: List[Dict[str, Any]],
    cites_payload: List[Dict[str, Any]],
    created_at: str | None,
) -> Dict[str, Any]:
    return {
        "DOI": "Not Avaliable",
        "Title": title,
        "Source": "Google Scholar",
        "PubYear": str(pub_year),
        "PubDate": None,
        "Journal": journal,
        "Publisher": publisher,
        "NoOfCititations": int(no_of_citations or 0),
        "IsConfirmed": "False",
        "created_at": created_at,
        "NoOfPages": pages,
        "Volume": volume,
        "Number": number,
        "ResearchLink": str(external_url),
        "Abstract": abstract,
        "RelatedResearchLink": str(related_pub_url) if related_pub_url else None,
        "Contributions": contributions_payload,
        "Cites": cites_payload,
    }
