from pydantic import BaseModel

class ResearcherProfileAndORCIDGetSerializer(BaseModel):
    google_scholar_url: str | None = None
    orcid: str | None = None
