from pydantic import Field
from ..Serializers.BaseFetchingResearchSerialzer import BaseFetchingResearchSerialzer

class ResearchWithNameSerializer(BaseFetchingResearchSerialzer):
    name: str = Field(..., description="name of the researcher")
