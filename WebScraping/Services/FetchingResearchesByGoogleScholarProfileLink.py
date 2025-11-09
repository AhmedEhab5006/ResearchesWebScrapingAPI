from scholarly import scholarly
import re

from ..Repos.ResearchRepo import ResarchRepo
from ..Repos.ResearcherResearchRepo import ResearcherResearchRepo
from ..models.Research import Research
from ..models.Researcher import Researcher
from ..Enums.FetchingResearchValidation import FetchingResearchValidation


class FetchingResearchesByProfileLinkGoogleScholarService:

    PAGE_SIZE = 50  

    @classmethod
    def fetch_and_store_works(cls, profile_url: str, researcher_id=None):
        try:
            research_repo = ResarchRepo()
            researcher_research_repo = ResearcherResearchRepo()

            if researcher_id and not Researcher.objects.filter(Id=researcher_id).exists():
                return FetchingResearchValidation.ResearcherDoesnotExist

            match = re.search(r"user=([a-zA-Z0-9_-]+)", profile_url)
            if not match:
                return FetchingResearchValidation.InvalidInput

            author_id = match.group(1)

            try:
                author = scholarly.search_author_id(author_id)
                author = scholarly.fill(author, sections=["basics", "indices", "publications"])
            except Exception as e:
                print(f"Error fetching author data: {e}")
                return FetchingResearchValidation.ConnectionError

            publications = author.get("publications", [])
            if not publications:
                return FetchingResearchValidation.NoResearchesFound

            count = 0
            for pub in publications:
                bib = pub.get("bib", {})
                title = bib.get("title", "Untitled")
                pub_year = bib.get("pub_year", "Unknown")
                citation = bib.get("citation", "Unknown")

                pub_url = pub.get("pub_url")
                if not pub_url:
                    author_pub_id = pub.get("author_pub_id")
                    if author_pub_id:
                        pub_url = f"https://scholar.google.com/citations?view_op=view_citation&citation_for_view={author_pub_id}"

                if not pub_url:
                    continue

                if Research.objects.filter(Link=pub_url).exists():
                    continue

                try:
                    research_obj = Research.objects.create(
                        Link=pub_url,
                        title=title,
                        Source="GoogleScholar",
                    )

                    if researcher_id:
                        researcher_research_repo.model.objects.get_or_create(
                            Researcher_id=researcher_id,
                            Research_id=research_obj.Id
                        )

                    count += 1

                except Exception as e:
                    print(f"Error saving research: {e}")
                    return FetchingResearchValidation.DatabaseError

            if count == 0:
                return FetchingResearchValidation.NoResearchesFound

            return FetchingResearchValidation.Added

        except Exception as ex:
            print(f"Unexpected error: {ex}")
            return FetchingResearchValidation.ConnectionError
