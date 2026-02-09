import re
from typing import Any, Dict, List, Tuple
from django.db import transaction
from WebScraping.models.Research import Research
from ..Messaging.rabbitmq.publisher import publish_message
from ..Messaging.rabbitmq.config import RK_PAPERS_INGEST_REQUESTED
from ..AppExceptions.AppError import (
    InvalidInputError,
    NoResearchesFoundError,
    ConnectionError,
    DatabaseError,
    NoResearchesToAddError,
)

from WebScraping.Repos.ResearcherRepo import ResearcherRepo
from WebScraping.Repos.ResearcherResearchRepo import ResearcherResearchRepo
from WebScraping.Repos.ResearcherInterestRepo import ResearcherInterestRepo
from WebScraping.Repos.ResearcherCitesRepo import ResearcherCitesRepo
from WebScraping.Repos.ResearchContributionsRepo import ResearchContributionsRepo
from WebScraping.Repos.ResearchCitesRepo import ResearchCitesRepo
from WebScraping.Repos.InterestRepo import InterestRepo

from ..utils.ScholarClient import ScholarClient
from ..Services.PayloadBuilder import parse_coauthors, build_research_payload


class FetchingResearchesByProfileLinkGoogleScholarService:
    @classmethod
    def fetch_and_store_works(cls, profile_url: str, orcid, researcher_nationalNumber):
        client = ScholarClient(min_delay=2.0, max_delay=5.0, max_retries=3)

        try:
            researcher_research_repo = ResearcherResearchRepo()
            researcher_repo = ResearcherRepo()
            researcher_interest_repo = ResearcherInterestRepo()
            researcher_cites_repo = ResearcherCitesRepo()
            research_cites_repo = ResearchCitesRepo()
            research_contribution_repo = ResearchContributionsRepo()
            interest_repo = InterestRepo()

            match = re.search(r"user=([a-zA-Z0-9_-]+)", str(profile_url))
            if not match:
                raise InvalidInputError("Invalid Google Scholar profile link")
            author_id = match.group(1)

            try:
                author = client.fetch_author(author_id)
                publications = author.get("publications", [])
            except Exception as e:
                raise ConnectionError("Error fetching author data", extra={"reason": str(e)})

            if not publications:
                raise NoResearchesFoundError("No researches found for this profile")

            # author fields
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

            new_researches_payload: List[Dict[str, Any]] = []
            new_interests_payload: List[Dict[str, Any]] = []
            new_researcher_cites_payload: List[Dict[str, Any]] = []

            try:
                url_to_pub: Dict[str, Dict[str, Any]] = {}
                candidate_urls: List[str] = []

                for pub in publications:
                    url = client.get_pub_url_fast(pub)
                    if url:
                        url_to_pub[url] = pub
                        candidate_urls.append(url)

                if not candidate_urls:
                    raise NoResearchesFoundError("No reachable publication URLs found")

                # We only fill pubs that are NOT already in DB.
                existing_urls = set(
                    Research.objects.filter(pubURL__in=candidate_urls).values_list("pubURL", flat=True)
                )

                payload_buffer: List[Tuple] = []
                research_to_create: List[Research] = []

                # FILL + EXTRACT HERE (outside transaction)
                for url, pub in url_to_pub.items():
                    if url in existing_urls:
                        continue

                    # If you truly want "fill every new paper", this is fine.
                    # (If fill_pub_if_needed decides not to fill because keys exist, you can replace it with: client.call(lambda: scholarly.fill(pub)))
                    filled_pub = client.fill_pub_if_needed(
                        pub,
                        need_top_keys=["cites_per_year", "url_related_articles", "pub_url"],
                        need_bib_keys=[
                            "title", "pub_year", "author", "journal", "publisher",
                            "abstract", "volume", "number", "pages"
                        ],
                    )

                    bib = filled_pub.get("bib", {}) or {}

                    title = bib.get("title") or "Untitled"
                    pub_year = bib.get("pub_year") or "Unknown"
                    no_of_citations = filled_pub.get("num_citations", 0) or 0

                    journal = bib.get("journal") or bib.get("venue") or bib.get("conference") or "Unknown"
                    publisher = bib.get("publisher") or "Unknown"
                    abstract = bib.get("abstract") or "Unknown"
                    volume = bib.get("volume") or "Unknown"
                    number = bib.get("number") or "Unknown"
                    pages = bib.get("pages") or "Unknown"

                    coauthors = parse_coauthors(
                            bib.get("author"),
                            filled_pub.get("author_id", [])
                        )
                    
                    related_pub_url = filled_pub.get("url_related_articles")
                    cites_per_year = filled_pub.get("cites_per_year") or {}

                    research_to_create.append(
                        Research(
                            title=title,
                            Source="GoogleScholar",
                            pubYear=str(pub_year),
                            publisher=publisher,
                            DOI="Not Avaliable",
                            noOfCititations=int(no_of_citations),
                            noOfPages=pages,
                            volume=volume,
                            number=number,
                            pubURL=url,
                            relatedResearchURL=related_pub_url,
                            abstract=abstract,
                            journal=journal,
                            
                        )
                    )

                    payload_buffer.append(
                        (
                            url,
                            title,
                            pub_year,
                            journal,
                            publisher,
                            no_of_citations,
                            pages,
                            volume,
                            number,
                            abstract,
                            related_pub_url,
                            coauthors,
                            cites_per_year,
                        )
                    )

                if not research_to_create:
                    raise NoResearchesToAddError("No researches to add (already exist)")

            except (InvalidInputError, NoResearchesFoundError, NoResearchesToAddError):
                raise
            except Exception as e:
                raise ConnectionError("Error while preparing publications", extra={"reason": str(e)})

            # ============================================
            # 2) DB transaction ONLY (fast DB operations)
            # ============================================
            try:
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

                    # update
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

                    # interests
                    for interest in interests:
                        interest_model, _ = interest_repo.model.objects.get_or_create(name=interest)
                        _link_obj, link_created = researcher_interest_repo.model.objects.get_or_create(
                            interest=interest_model,
                            researcher=researcher_instance,
                        )
                        if link_created:
                            new_interests_payload.append({"Name": interest_model.name})

                    # researcher cites
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
                        else:
                            if obj.noOfCitations != noOfCites:
                                obj.noOfCitations = noOfCites
                                obj.save(update_fields=["noOfCitations"])

                    # bulk create researches
                    Research.objects.bulk_create(research_to_create, batch_size=200)

                    # map created
                    created_map = {
                        r.pubURL: r
                        for r in Research.objects.filter(pubURL__in=[r.pubURL for r in research_to_create])
                    }

                    links_to_create = []
                    cites_to_create = []
                    contribs_to_create = []

                    for (
                        url,
                        title,
                        pub_year,
                        journal,
                        publisher,
                        no_of_citations,
                        pages,
                        volume,
                        number,
                        abstract,
                        related_pub_url,
                        coauthors,
                        cites_per_year,
                    ) in payload_buffer:
                        research_obj = created_map[url]

                        links_to_create.append(
                            researcher_research_repo.model(
                                Researcher=researcher_instance,
                                Research=research_obj,
                            )
                        )

                        cites_payload = []
                        for y, c in (cites_per_year or {}).items():
                            cites_to_create.append(
                                research_cites_repo.model(
                                    research=research_obj,
                                    year=int(y),
                                    numberOfCites=int(c or 0),
                                )
                            )
                            cites_payload.append({"Id": None, "Year": int(y), "NumberOfCites": int(c or 0)})

                        contributions_payload = []
                        for idx, member in enumerate(coauthors, start=1):
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
                                    "researcherNationalNumber": str(researcher_nationalNumber)
                                    if researcher_nationalNumber
                                    else None,
                                    "MemberAcademicName": member["academic_name"],
                                    "memberOrcid": None,
                                    "memberPositionInSearch": str(idx),
                                    "MemberScholarId":member["scholar_id"]
                                }
                            )

                        new_researches_payload.append(
                            build_research_payload(
                                title=title,
                                pub_year=str(pub_year),
                                journal=journal,
                                publisher=publisher,
                                no_of_citations=int(no_of_citations or 0),
                                pages=pages,
                                volume=volume,
                                number=number,
                                external_url=url,
                                abstract=abstract,
                                related_pub_url=related_pub_url,
                                contributions_payload=contributions_payload,
                                cites_payload=cites_payload,
                                created_at=str(research_obj.created_at)
                                if hasattr(research_obj, "created_at")
                                else None,
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

            except (InvalidInputError, NoResearchesFoundError, NoResearchesToAddError):
                raise
            except Exception as e:
                raise DatabaseError("Error while fetching researches", extra={"reason": str(e)})

            # publish (outside transaction)
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
            }

            correlation_id = str(researcher_nationalNumber) if researcher_nationalNumber else None
            try:
                publish_message(
                    routing_key=RK_PAPERS_INGEST_REQUESTED,
                    payload=researcher_payload,
                    correlation_id=correlation_id,
                )
            except Exception as e:
                raise ConnectionError("Failed to publish message", extra={"reason": str(e)})

            return {"detail": "Added & Published", "new_researches_count": len(new_researches_payload)}

        except (InvalidInputError, NoResearchesFoundError, ConnectionError, DatabaseError, NoResearchesToAddError):
            raise
        except Exception as ex:
            raise ConnectionError("Unexpected error", extra={"reason": str(ex)})
