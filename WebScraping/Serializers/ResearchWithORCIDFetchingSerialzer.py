from pydantic import Field
from ..Serializers.BaseFetchingResearchSerialzer import BaseFetchingResearchSerialzer

class ResearchWithORCIDFetchingSerialzer(BaseFetchingResearchSerialzer):
    orcid: str = Field(..., description="ORCID of the researcher")
