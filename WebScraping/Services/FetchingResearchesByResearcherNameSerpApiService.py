from serpapi import GoogleSearch
from ..Repos.ResearchRepo import ResarchRepo
from ..Repos.ResearcherResearchRepo import ResearcherResearchRepo
from ..models.Research import Research
from ..models.Researcher import Researcher
from ..Enums.FetchingResearchValidation import FetchingResearchValidation


class FetchingResearchesByResearcherNameSerpApiService:

    API_KEY = "631a0f2d0b78f02e3dcf12f8e7dc30d4f79a4cf2c1748c4efae251db7d1a53f4"
    PER_PAGE = 10

    @classmethod
    def fetch_and_store_works(cls, username, researcher_id=None, total_results=50):
        try:
            research_repo = ResarchRepo()
            researcher_research_repo = ResearcherResearchRepo()
            count = 0

            if researcher_id and not Researcher.objects.filter(Id=researcher_id).exists():
                return FetchingResearchValidation.ResearcherDoesnotExist

            for start in range(0, total_results, cls.PER_PAGE):
                params = {
                    "q": username,
                    "api_key": cls.API_KEY,
                    "engine": "google_scholar",
                    "num": cls.PER_PAGE,
                    "start": start
                }

                search = GoogleSearch(params)
                results = search.get_dict()
                papers = results.get("organic_results", [])

                if not papers:
                    break

                for paper in papers:
                    link = paper.get("link")
                    title = paper.get("title")

                    if not link:
                        continue  # skip if no link

                    # Skip if research already exists
                    if Research.objects.filter(Link=link).exists():
                        continue

                    try:
                        # Save new Research
                        research_obj = Research.objects.create(
                            Link=link,
                            title=title,
                            Source="GoogleScholar"
                        )

                        # Link to researcher if provided
                        if researcher_id:
                            researcher_research_repo.model.objects.get_or_create(
                                Researcher_id=researcher_id,
                                Research_id=research_obj.Id
                            )

                        count += 1
                        if count >= total_results:
                            break
                    except Exception as e:
                        print(f"Error saving research: {e}")
                        return FetchingResearchValidation.DatabaseError

            return FetchingResearchValidation.Added

        except Exception as ex:
            print(f"Error fetching research: {ex}")
            return FetchingResearchValidation.ConnectionError
