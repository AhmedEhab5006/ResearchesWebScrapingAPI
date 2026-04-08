import re
from typing import Any, Dict, List, Tuple

from django.db import transaction
from WebScraping.models.Research import Research

from ..AppExceptions.AppError import (
    InvalidInputError,
    NoResearchesFoundError,
    ConnectionError,
    DatabaseError,
    NoResearchesToAddError,
)
from ..utils.ScholarClient import ScholarClient
from ..Services.PayloadBuilder import parse_coauthors, build_research_payload
from ..Messaging.rabbitmq.publisher import publish_message
from ..Messaging.rabbitmq.config import RK_PAPERS_INGEST_REQUESTED

from WebScraping.Repos.ResearcherRepo import ResearcherRepo
from WebScraping.Repos.ResearcherResearchRepo import ResearcherResearchRepo
from WebScraping.Repos.ResearcherInterestRepo import ResearcherInterestRepo
from WebScraping.Repos.ResearcherCitesRepo import ResearcherCitesRepo
from WebScraping.Repos.ResearchContributionsRepo import ResearchContributionsRepo
from WebScraping.Repos.ResearchCitesRepo import ResearchCitesRepo
from WebScraping.Repos.InterestRepo import InterestRepo
from WebScraping.Repos.CoAuthorRepo import CoAuthorRepo
from WebScraping.Repos.ResearcherCoAuthorRepo import ResearcherCoAuthorRepo
from ..AppExceptions.TooManyRequestsException import TooManyRequestsException


class FetchingResearchesByProfileLinkGoogleScholarService:
    def __init__(self):
        self.client = ScholarClient(min_delay=10.0, max_delay=20.0, max_retries=5)
        

    def check_what_to_fetch(
        self,
        researcher_nationalNumber: str,
        publications: List[Dict[str, Any]],
        coauthors: List[Dict[str, Any]],
    ) -> Dict[str, Any]:

        researcher_repo = ResearcherRepo()
        co_author_repo = CoAuthorRepo()

        researcher = researcher_repo.model.objects.filter(
            nationalNumber=researcher_nationalNumber
        ).first()

        pub_urls = [
            self.client.get_pub_url_fast(pub)
            for pub in publications
            if self.client.get_pub_url_fast(pub)
        ]

        existing_pub_urls = set(
            Research.objects.filter(pubURL__in=pub_urls)
            .values_list("pubURL", flat=True)
        )

        missing_publications = [
            pub for pub in publications
            if self.client.get_pub_url_fast(pub)
            not in existing_pub_urls
        ]

        coauthor_ids = [c.get("scholar_id") for c in coauthors if c.get("scholar_id")]

        existing_coauthors = set(
            co_author_repo.model.objects.filter(
                scholarProfileLink__in=coauthor_ids
            ).values_list("scholarProfileLink", flat=True)
        )

        missing_coauthors = [
            c for c in coauthors
            if c.get("scholar_id") not in existing_coauthors
        ]

        return {
            "profile_exists": researcher is not None,
            "missing_publications": missing_publications,
            "missing_coauthors": missing_coauthors,
            "existing_publications_count": len(existing_pub_urls),
            "incoming_publications_count": len(publications),
            "existing_coauthors_count": len(existing_coauthors),
            "incoming_coauthors_count": len(coauthors),
        }
    
    
    def extract_author_id(self, profile_url: str) -> str:
        match = re.search(r"user=([a-zA-Z0-9_-]+)", str(profile_url))
        if not match:
            raise InvalidInputError("Invalid Google Scholar profile link")
        return match.group(1)

    def fetch_main_author(self, profile_url: str) -> Dict[str, Any]:
        author_id = self.extract_author_id(profile_url)
        return self.client.fetch_author(author_id)

    def prepare_coauthor_data(self, coauthor: Dict[str, Any]) -> Dict[str, Any]:
        scholar_id = coauthor.get("scholar_id")
        name = coauthor.get("name") or "Unknown"
        affiliation = coauthor.get("affiliation") or coauthor.get("organization") or ""
        picture = coauthor.get("url_picture")
        email_domain = coauthor.get("email_domain")

        profile_link = (
            f"https://scholar.google.com/citations?hl=ar&user={scholar_id}"
            if scholar_id else None
        )

        return {
            "scholar_id": scholar_id,
            "name": name,
            "affiliation": affiliation,
            "url_picture": picture,
            "email_domain": email_domain,
            "profile_link": profile_link,
        }

    def prepare_publication_data(self, pub: Dict[str, Any]) -> Dict[str, Any]:
        filled_pub = self.client.fill_pub_if_needed(
            pub,
            need_top_keys=["cites_per_year", "url_related_articles", "pub_url"],
            need_bib_keys=[
                "title",
                "pub_year",
                "author",
                "journal",
                "publisher",
                "abstract",
                "volume",
                "number",
                "pages",
            ],
        )

        bib = filled_pub.get("bib", {}) or {}

        return {
            "pub_url": self.client.get_pub_url_fast(filled_pub),
            "title": bib.get("title") or "Untitled",
            "pub_year": bib.get("pub_year"),
            "journal": bib.get("journal") or bib.get("venue") or bib.get("conference") or "Unknown",
            "publisher": bib.get("publisher") or "Unknown",
            "abstract": bib.get("abstract") or "Unknown",
            "volume": bib.get("volume") or "Unknown",
            "number": bib.get("number") or "Unknown",
            "pages": bib.get("pages") or "Unknown",
            "num_citations": filled_pub.get("num_citations", 0) or 0,
            "related_pub_url": filled_pub.get("url_related_articles"),
            "cites_per_year": filled_pub.get("cites_per_year") or {},
            "coauthors": parse_coauthors(
                bib.get("author"),
                filled_pub.get("author_id", [])
            ),
        }

    def save_all_to_db(
        self,
        profile_url: str,
        orcid: str,
        researcher_nationalNumber: str,
        author: Dict[str, Any],
        publications_data: List[Dict[str, Any]],
        coauthors_data: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        researcher_research_repo = ResearcherResearchRepo()
        researcher_repo = ResearcherRepo()
        researcher_interest_repo = ResearcherInterestRepo()
        researcher_cites_repo = ResearcherCitesRepo()
        research_cites_repo = ResearchCitesRepo()
        research_contribution_repo = ResearchContributionsRepo()
        interest_repo = InterestRepo()
        co_author_repo = CoAuthorRepo()
        researcher_co_author_repo = ResearcherCoAuthorRepo()

        affiliation = author.get("affiliation")
        academicName = author.get("name")
        profilePicture = author.get("url_picture")
        organizationId = author.get("organization")
        emailDomain = author.get("email_domain")
        noOfCitations = author.get("citedby")
        noOfCitationsInLastFiveYears = author.get("citedby5y")
        hindex = author.get("hindex")
        hindexInLastFiveYears = author.get("hindex5y")
        i10index = author.get("i10index")
        i10indexInLastFiveYears = author.get("i10index5y")
        interests = author.get("interests", [])
        citesPerYear = author.get("cites_per_year", {}) or {}

        new_researches_payload = []
        new_interests_payload = []
        new_researcher_cites_payload = []
        co_authors_payload = []

        with transaction.atomic():
            researcher_instance, _ = researcher_repo.model.objects.get_or_create(
                nationalNumber=researcher_nationalNumber,
                defaults={
                    "scholarProfileLink": profile_url,
                    "academicName": academicName,
                    "scholarProfileImageURL": profilePicture,
                    "organisationalDomain": emailDomain,
                    "totalNumberOfCitiations": noOfCitations,
                    "numberOfCitiationsInLastFiveYears": noOfCitationsInLastFiveYears,
                    "hindex": hindex,
                    "hindexInLastFiveYears": hindexInLastFiveYears,
                    "i10index": i10index,
                    "i10index5y": i10indexInLastFiveYears,
                    "jobTitle": affiliation,
                    "organisationId": organizationId,
                    "ORCID": orcid,
                },
            )

            researcher_instance.scholarProfileLink = profile_url
            researcher_instance.academicName = academicName
            researcher_instance.scholarProfileImageURL = profilePicture
            researcher_instance.organisationalDomain = emailDomain
            researcher_instance.totalNumberOfCitiations = noOfCitations
            researcher_instance.numberOfCitiationsInLastFiveYears = noOfCitationsInLastFiveYears
            researcher_instance.hindex = hindex
            researcher_instance.hindexInLastFiveYears = hindexInLastFiveYears
            researcher_instance.i10index = i10index
            researcher_instance.i10index5y = i10indexInLastFiveYears
            researcher_instance.jobTitle = affiliation
            researcher_instance.organisationId = organizationId
            researcher_instance.ORCID = orcid
            researcher_instance.save()

            for interest in interests:
                interest_model, _ = interest_repo.model.objects.get_or_create(name=interest)
                _, link_created = researcher_interest_repo.model.objects.get_or_create(
                    interest=interest_model,
                    researcher=researcher_instance,
                )
                if link_created:
                    new_interests_payload.append({"Name": interest_model.name})

            for year, noOfCites in citesPerYear.items():
                obj, created = researcher_cites_repo.model.objects.get_or_create(
                    researcher=researcher_instance,
                    year=year,
                    defaults={"noOfCitations": noOfCites},
                )
                if created:
                    new_researcher_cites_payload.append(
                        {"Year": int(year), "NoOfCitations": int(noOfCites or 0)}
                    )
                elif obj.noOfCitations != noOfCites:
                    obj.noOfCitations = noOfCites
                    obj.save(update_fields=["noOfCitations"])

            for coauthor in coauthors_data:
                scholar_id = coauthor.get("scholar_id")
                if not scholar_id:
                    continue

                co_name = coauthor.get("name") or "Unknown"
                co_affiliation = coauthor.get("affiliation") or ""
                co_picture = coauthor.get("url_picture")
                co_email_domain = coauthor.get("email_domain")
                profile_link = coauthor.get("profile_link")

                co_author_obj, _ = co_author_repo.model.objects.get_or_create(
                    scholarProfileLink=str(scholar_id),
                    academicName = co_name,
                    scholarProfileImageURL = co_picture,
                    jobTitle = co_affiliation
                )

                dirty_fields = []

                if getattr(co_author_obj, "academicName", None) != co_name:
                    co_author_obj.academicName = co_name
                    dirty_fields.append("academicName")

                if getattr(co_author_obj, "jobTitle", None) != co_affiliation:
                    co_author_obj.jobTitle = co_affiliation
                    dirty_fields.append("jobTitle")

                if getattr(co_author_obj, "scholarProfileImageURL", None) != co_picture:
                    co_author_obj.scholarProfileImageURL = co_picture
                    dirty_fields.append("scholarProfileImageURL")

                if dirty_fields:
                    co_author_obj.save(update_fields=dirty_fields)

                researcher_co_author_repo.model.objects.get_or_create(
                    Researcher=researcher_instance,
                    CoAuthor=co_author_obj,
                )

                co_authors_payload.append(
                    {
                        "ScholarProfileLink": profile_link,
                        "AcademicName": co_name,
                        "JobTitle": co_affiliation,
                        "ScholarProfileImageURL": str(co_picture) if co_picture else None,
                        "OrganisationalDomain": co_email_domain,
                    }
                )            
                existing_urls = set(
                Research.objects.filter(
                    pubURL__in=[p["pub_url"] for p in publications_data if p["pub_url"]]
                ).values_list("pubURL", flat=True)
            )

            research_to_create = []
            valid_publications = []

            for pub_data in publications_data:
                if not pub_data["pub_url"] or pub_data["pub_url"] in existing_urls:
                    continue

                value = pub_data["pub_year"]
                match = re.search(r"\d{4}", str(value)) if value else None
                pubYear = int(match.group()) if match else 0
    
                research_to_create.append(
                    Research(
                        title=pub_data["title"],
                        Source="GoogleScholar",
                        pubYear= pubYear ,
                        publisher=pub_data["publisher"],
                        DOI="",
                        noOfCititations=int(pub_data["num_citations"]),
                        noOfPages=pub_data["pages"],
                        volume=pub_data["volume"],
                        number=pub_data["number"],
                        pubURL=pub_data["pub_url"],
                        relatedResearchURL=pub_data["related_pub_url"],
                        abstract=pub_data["abstract"],
                        journal=pub_data["journal"],
                    )
                )
                valid_publications.append(pub_data)

            if not research_to_create:
                print("No researches to add (already exist)")

            Research.objects.bulk_create(research_to_create, batch_size=200)

            created_map = {
                r.pubURL: r
                for r in Research.objects.filter(pubURL__in=[r.pubURL for r in research_to_create])
            }

            links_to_create = []
            cites_to_create = []
            contribs_to_create = []

            for pub_data in valid_publications:
                research_obj = created_map[pub_data["pub_url"]]

                links_to_create.append(
                    researcher_research_repo.model(
                        Researcher=researcher_instance,
                        Research=research_obj,
                    )
                )

                cites_payload = []
                for y, c in (pub_data["cites_per_year"] or {}).items():
                    cites_to_create.append(
                        research_cites_repo.model(
                            research=research_obj,
                            year=int(y),
                            numberOfCites=int(c or 0),
                        )
                    )
                    cites_payload.append(
                        {"Id": None, "Year": int(y), "NumberOfCites": int(c or 0)}
                    )

                contributions_payload = []
                for idx, member in enumerate(pub_data["coauthors"], start=1):
                    contribs_to_create.append(
                        research_contribution_repo.model(
                            research=research_obj,
                            researcher=researcher_instance,
                            memberAcademicName=member["academic_name"],
                            memberScholarProfileURL=member["scholar_id"],
                        )
                    )
                    contributions_payload.append(
                        {
                            "Id": None,
                            "researcherNationalNumber": str(researcher_nationalNumber),
                            "MemberAcademicName": member["academic_name"],
                            "memberOrcid": None,
                            "memberPositionInSearch": str(idx),
                            "MemberScholarId": member["scholar_id"],
                        }
                    )

                value = pub_data["pub_year"]
                match = re.search(r"\d{4}", str(value)) if value else None
                pubYear = int(match.group()) if match else 0

                new_researches_payload.append(
                    build_research_payload(
                        title=pub_data["title"],
                        pub_year= pubYear,
                        journal=pub_data["journal"],
                        publisher=pub_data["publisher"],
                        no_of_citations=int(pub_data["num_citations"]),
                        pages=pub_data["pages"],
                        volume=pub_data["volume"],
                        number=pub_data["number"],
                        external_url=pub_data["pub_url"],
                        abstract=pub_data["abstract"],
                        related_pub_url=pub_data["related_pub_url"],
                        contributions_payload=contributions_payload,
                        cites_payload=cites_payload,
                        created_at=str(research_obj.created_at) if hasattr(research_obj, "created_at") else None,
                    )
                )

            researcher_research_repo.model.objects.bulk_create(
                links_to_create, batch_size=500, ignore_conflicts=True
            )
            research_cites_repo.model.objects.bulk_create(
                cites_to_create, batch_size=500, ignore_conflicts=True
            )
            research_contribution_repo.model.objects.bulk_create(
                contribs_to_create, batch_size=500, ignore_conflicts=True
            )

        researcher_payload = {
            "NationalNumber": researcher_instance.nationalNumber,
            "ORCID": researcher_instance.ORCID,
            "ScholarProfileLink": str(researcher_instance.scholarProfileLink),
            "AcademicName": researcher_instance.academicName,
            "ScholarProfileImageURL": str(researcher_instance.scholarProfileImageURL),
            "OrganisationalDomain": researcher_instance.organisationalDomain,
            "JobTitle": researcher_instance.jobTitle,
            "OrganisationId": str(researcher_instance.organisationId),
            "TotalNumberOfCitiations": researcher_instance.totalNumberOfCitiations,
            "NumberOfCitiationsInLastFiveYears": researcher_instance.numberOfCitiationsInLastFiveYears,
            "Hindex": researcher_instance.hindex,
            "HindexInLastFiveYears": researcher_instance.hindexInLastFiveYears,
            "I10index": researcher_instance.i10index,
            "I10index5y": researcher_instance.i10index5y,
            "ResearcherCites": new_researcher_cites_payload,
            "Interests": new_interests_payload,
            "Researches": new_researches_payload,
            "CoAuthors": co_authors_payload,
        }

        publish_message(
            routing_key=RK_PAPERS_INGEST_REQUESTED,
            payload=researcher_payload,
            correlation_id=str(researcher_nationalNumber),
        )

        return {
            "detail": "Added & Published",
            "new_researches_count": len(new_researches_payload),
            "co_authors_count": len(co_authors_payload),
        }