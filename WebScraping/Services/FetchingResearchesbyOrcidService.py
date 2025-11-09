import requests
from ..Repos.ResearchRepo import ResarchRepo
from ..Repos.ResearcherResearchRepo import ResearcherResearchRepo
from ..models.Research import Research
from ..models.ResearcherResearch import ResearcherResearch
from ..models.Researcher import Researcher
from ..Enums.FetchingResearchValidation import FetchingResearchValidation
from requests.exceptions import RequestException


class FetchingResearchesbyOrcidService:
    BASE_URL = "https://api.openalex.org/works"

    @classmethod
    def fetch_and_store_works(cls, orcid, researcher_id=None, max_results=500):
        try:
            params = {"filter": f"author.orcid:{orcid}", "per_page": 50}
            next_page = cls.BASE_URL
            count = 0

            research_repo = ResarchRepo()
            researcher_research_repo = ResearcherResearchRepo()

            if researcher_id:
                if not Researcher.objects.filter(Id=researcher_id).exists():
                    return FetchingResearchValidation.ResearcherDoesnotExist

            while next_page and count < max_results:
                try:
                    resp = requests.get(next_page, params=params if next_page == cls.BASE_URL else None, timeout=10)
                    resp.raise_for_status()
                    data = resp.json()
                except RequestException:
                    return FetchingResearchValidation.ConnectionError

                for work in data.get("results", []):
                    doi = work.get("doi")
                    link = work.get("id")
                    title = work.get("title")

                    if not doi and not link:
                        continue 

                    research_obj = None
                    if doi:
                        research_obj = Research.objects.filter(DOI=doi).first()
                    if not research_obj and link:
                        research_obj = Research.objects.filter(Link=link).first()

                    try:
                        if not research_obj:
                            research_obj = Research.objects.create(
                                DOI=doi,
                                Link=link,
                                title=title,
                                Source="OpenAlex"
                            )

                        if researcher_id:
                            researcher_research_repo.model.objects.get_or_create(
                                Researcher_id=researcher_id,
                                Research_id=research_obj.Id
                            )

                        count += 1
                        if count >= max_results:
                            break
                    except Exception as e:
                        print(f"Error saving research: {e}")
                        return FetchingResearchValidation.DatabaseError

                next_page = data.get("meta", {}).get("next_cursor_url")

            return FetchingResearchValidation.Added

        except Exception as ex:
            print(f"Error fetching research: {ex}")
            return FetchingResearchValidation.DatabaseError
