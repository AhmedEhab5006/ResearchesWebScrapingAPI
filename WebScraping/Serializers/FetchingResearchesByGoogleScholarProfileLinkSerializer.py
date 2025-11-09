from pydantic import Field
from ..Serializers.BaseFetchingResearchSerialzer import BaseFetchingResearchSerialzer

class FetchingResearchesByGoogleScholarProfileLinkSerializer(BaseFetchingResearchSerialzer):
    profileLink: str = Field(..., description="name of the researcher")
