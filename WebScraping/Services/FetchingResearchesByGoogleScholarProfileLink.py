from scholarly import scholarly
import re
import json
from ..Serializers.JsonConverstion import JsonConvert
from WebScraping.Repos.ResearcherRepo import ResearcherRepo
from WebScraping.Repos.ResearcherResearchRepo import ResearcherResearchRepo
from WebScraping.Repos.ResearcherInterestRepo import ResearcherInterestRepo
from WebScraping.Repos.ResearcherCitesRepo import ResearcherCitesRepo
from WebScraping.Repos.ResearchContributionsRepo import ResearchContributionsRepo
from WebScraping.Repos.ResearchCitesRepo import ResearchCitesRepo
from WebScraping.Repos.InterestRepo import InterestRepo
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


class FetchingResearchesByProfileLinkGoogleScholarService:
    PAGE_SIZE = 50

    @classmethod
    def fetch_and_store_works(cls, profile_url: str, orcid, researcher_nationalNumber):
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
                author = scholarly.search_author_id(author_id)
                author = scholarly.fill(author, sections=["basics", "indices", "publications"])
                publications = author.get("publications", [])
            except Exception as e:
                raise ConnectionError("Error fetching author data", extra={"reason": str(e)})

            if not publications:
                raise NoResearchesFoundError("No researches found for this profile")

            # =========================
            # Author basics
            # =========================
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
            citesPerYear = author.get("cites_per_year", {})

            # =========================
            # Track ONLY new data to publish
            # =========================
            new_researches_payload = []
            new_interests_payload = []
            new_researcher_cites_payload = []

            try:
                researcher_instance, _ = researcher_repo.model.objects.get_or_create(
                    nationalNumber=researcher_nationalNumber,
                    scholarProfileLink=profile_url,
                    academicName=academicName,
                    scholarProfileImageURL=profilePicture,
                    organisationalDomain=emailDomain,
                    totalNumberOfCitiations=noOfCitations,
                    numberOfCitiationsInLastFiveYears=noOfCitationsInLastFiveYears,
                    hindex=hindex,
                    hindexInLastFiveYears=hindexInLastFiveYears,
                    i10index=i10index,
                    i10index5y=i10indexInLastFiveYears,
                    jobTitle=affiliation,
                    organisationId=organizationId,
                    ORCID=orcid,
                )

                # -------------------------
                # Interests (track only NEW links)
                # -------------------------
                for interest in interests:
                    interest_model, _interest_created = interest_repo.model.objects.get_or_create(
                        name=interest
                    )

                    _link_obj, link_created = researcher_interest_repo.model.objects.get_or_create(
                        interest=interest_model,
                        researcher=researcher_instance,
                    )

                    if link_created:
                        new_interests_payload.append({"Name": interest_model.name})

                # -------------------------
                # Researcher cites per year (track only NEW rows)
                # -------------------------
                for year, noOfCites in citesPerYear.items():
                    obj, created = researcher_cites_repo.model.objects.get_or_create(
                        researcher=researcher_instance,
                        year=year,
                        defaults={"noOfCitations": noOfCites},
                    )
                    if created:
                        new_researcher_cites_payload.append(
                            {"Year": int(year), "NoOfCitations": int(noOfCites) if noOfCites is not None else 0}
                        )
                    else:
                        # optional: update if changed (doesn't count as "new")
                        if obj.noOfCitations != noOfCites:
                            obj.noOfCitations = noOfCites
                            obj.save(update_fields=["noOfCitations"])

                # -------------------------
                # Publications loop
                # Only add/store + publish if NEW research (by pubURL)
                # -------------------------
                count = 0

                for pub in publications:
                    bib = pub.get("bib", {})

                    # ==========================================================
                    # PERFORMANCE OPTIMIZATION (minimal change):
                    # Only call scholarly.fill(pub) when needed
                    # ==========================================================
                    filled_pub = None

                    title = bib.get("title", "Untitled")
                    pub_year = bib.get("pub_year", "Unknown")
                    no_of_citiations = pub.get("num_citations", 0)
                    journal = bib.get("journal", "Unknown")
                    abstract = bib.get("abstract", "Unknown")
                    publisher = bib.get("publisher", "Unknown")
                    volume = bib.get("volume", "Unknown")
                    number = bib.get("number", "Unknown")
                    pages = bib.get("pages", "Unknown")

                    # coauthors may come as string "A and B and C"
                    coauthors = bib.get("author", [])
                    if isinstance(coauthors, str):
                        coauthors = [a.strip() for a in coauthors.split(" and ") if a.strip()]
                    elif coauthors is None:
                        coauthors = []

                    # Try to get external_url without fill (faster)
                    external_url = pub.get("pub_url")

                    if not external_url:
                        filled_pub = scholarly.fill(pub)
                        external_url = filled_pub.get("pub_url")

                    # fallback: citation page
                    if not external_url:
                        author_pub_id = pub.get("author_pub_id")
                        if author_pub_id:
                            external_url = (
                                "https://scholar.google.com/citations?"
                                f"view_op=view_citation&citation_for_view={author_pub_id}"
                            )

                    if not external_url:
                        continue

                    # Skip if already exists (NOT new => do NOT publish it)
                    if Research.objects.filter(pubURL=external_url).exists():
                        continue

                    # If we didn't fill before, but we need extra fields, fill now (only for NEW research)
                    if filled_pub is None:
                        filled_pub = scholarly.fill(pub)

                    related_pub_url = filled_pub.get("url_related_articles", None)
                    cites_per_year = filled_pub.get("cites_per_year") or {}

                    # Create Research row (NEW)
                    research_obj = Research.objects.create(
                        title=title,
                        Source="GoogleScholar",
                        pubYear=pub_year,
                        publisher=publisher,
                        DOI="Not Avaliable",
                        noOfCititations=no_of_citiations if no_of_citiations is not None else 0,
                        noOfPages=pages,
                        volume=volume,
                        number=number,
                        pubURL=external_url,
                        relatedResearchURL=related_pub_url,
                        abstract=abstract,
                        journal=journal,
                    )

                    # Link researcher <-> research
                    if researcher_nationalNumber:
                        researcher_research_repo.model.objects.create(
                            Researcher=researcher_instance,
                            Research=research_obj,
                        )

                    # Research cites per year (store) + payload list
                    cites_payload = []
                    for research_year, research_year_cites in (cites_per_year or {}).items():
                        research_cites_repo.model.objects.create(
                            research=research_obj,
                            year=research_year,
                            numberOfCites=research_year_cites,
                        )

                        cites_payload.append(
                            {
                                "Id": None,
                                "Year": int(research_year),
                                "NumberOfCites": int(research_year_cites)
                                if research_year_cites is not None
                                else 0,
                            }
                        )

                    contributions_payload = []
                    for idx, author_name in enumerate(coauthors, start=1):
                        research_contribution_repo.model.objects.create(
                            research=research_obj,
                            researcher=researcher_instance,
                            memberAcademicName=author_name,
                        )

                        contributions_payload.append(
                            {
                                "Id": None,
                                "researcherNationalNumber": str(researcher_nationalNumber)
                                if researcher_nationalNumber
                                else None,
                                "MemberAcademicName": author_name,
                                "memberOrcid": None,
                                "memberPositionInSearch": str(idx),
                            }
                        )

                    new_researches_payload.append(
                        {
                            "DOI": "Not Avaliable",
                            "Title": title,
                            "Source": "Google Scholar",
                            "PubYear": str(pub_year),
                            "PubDate": None,  
                            "Journal": journal,
                            "Publisher": publisher,
                            "NoOfCititations": int(no_of_citiations)
                            if no_of_citiations not in (None, "Unknown")
                            else 0,
                            "IsConfirmed": False,
                            "created_at": str(research_obj.created_at)
                            if hasattr(research_obj, "created_at")
                            else None,
                            "NoOfPages": pages,
                            "Volume": volume,
                            "Number": number,
                            "ResearchLink": str(external_url),
                            "Abstract": abstract,
                            "RelatedResearchLink": str(related_pub_url),
                            "Contributions": contributions_payload,
                            "Cites": cites_payload,
                        }
                    )

                    count += 1

            except Exception as e:
                raise DatabaseError("Error while fetching researches", extra={"reason": str(e)})

            if count == 0 or len(new_researches_payload) == 0:
                raise NoResearchesToAddError("No researches to add (already exist)")

            researcher_payload = {
                "nationalNumber": researcher_instance.nationalNumber,
                "ORCID": researcher_instance.ORCID,
                "ScholarProfileLink": str(researcher_instance.scholarProfileLink),
                "AcademicName": researcher_instance.academicName,
                "scholarProfileImageURL": str(researcher_instance.scholarProfileImageURL),
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

            payload = researcher_payload
            correlation_id = str(researcher_nationalNumber) if researcher_nationalNumber else None

            try:
                publish_message(
                    routing_key=RK_PAPERS_INGEST_REQUESTED,
                    payload=payload,
                    correlation_id=correlation_id,
                )
            except Exception as e:
                raise ConnectionError("Failed to publish message", extra={"reason": str(e)})

            return {
                "detail": "Added & Published",
                "new_researches_count": len(new_researches_payload),
            }

        except (InvalidInputError, NoResearchesFoundError, ConnectionError, DatabaseError, NoResearchesToAddError):
            raise
        except Exception as ex:
            raise ConnectionError("Unexpected error", extra={"reason": str(ex)})
