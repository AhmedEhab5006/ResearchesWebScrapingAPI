import requests
from ..Repos.ResearchRepo import ResarchRepo
from ..Repos.ResearcherResearchRepo import ResearcherResearchRepo
from ..Repos.ResearcheIndexesRepo import ResearcheIndexesRepo
from ..Repos.ResearchContributionsRepo import ResearchContributionsRepo
from ..models.Research import Research
from ..models.ResearcherResearch import ResearcherResearch
from ..models.Researcher import Researcher
from ..Enums.FetchingResearchValidation import FetchingResearchValidation
from requests.exceptions import RequestException
import traceback

class FetchingResearchesbyOrcidService:
    BASE_URL = "https://api.openalex.org/works"

    @classmethod
    def fetch_and_store_works(cls, orcid, researcher_national_number=None, max_results=50):
        try:
            params = {"filter": f"author.orcid:{orcid}", "per_page": 50}
            next_page = cls.BASE_URL
            count = 0

            researcher_research_repo = ResearcherResearchRepo()
            researcher_instance = Researcher.objects.filter(nationalNumber=researcher_national_number).first()
            researcher_contributions_repo = ResearchContributionsRepo()
            research_indexes_repo = ResearcheIndexesRepo()

            if researcher_national_number:
                if not researcher_instance:
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
                    pubYear = work.get("publication_year")
                    pubDate = work.get("publication_date")
                    noOfCitations = work.get("cited_by_count")
                    indexedIn = work.get("indexed_in")
                    authors = work.get("authorships")
                    primary_location = work.get("primary_location")
                    publisher = None

                    if isinstance(primary_location, dict):
                        source = primary_location.get("source")
                        if isinstance(source, dict):
                            publisher = source.get("display_name")

                    elif work.get("source") and isinstance(work["source"], dict):
                        publisher = work["source"].get("display_name")
                
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
                                Source="OpenAlex",
                                pubYear = pubYear,
                                publisher = publisher,
                                noOfCititations = noOfCitations,
                                pubDate = pubDate
                            )

                        if researcher_national_number:
                            researcher_research_repo.model.objects.get_or_create(
                                Researcher=researcher_instance,
                                Research=research_obj
                            )

                        for index in indexedIn:
                            research_indexes_repo.model.objects.get_or_create(
                                researcher=researcher_instance,
                                research=research_obj,
                                platform = index
                            )
                        
                        for element in authors:
                            researcher_contributions_repo.model.objects.get_or_create(
                                researcher=researcher_instance,
                                research=research_obj,
                                memberAcademicName = element["author"]["display_name"],  
                                memberPositionInSearch = element["author_position"],
                                memberOrcid = str(element["author"]["orcid"]).split("/")[-1]   
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
            traceback.print_exc()  # prints full traceback
            return FetchingResearchValidation.DatabaseError
