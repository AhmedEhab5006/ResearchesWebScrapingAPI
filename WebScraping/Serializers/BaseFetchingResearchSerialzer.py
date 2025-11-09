from pydantic import BaseModel, Field
from uuid import UUID

class BaseFetchingResearchSerialzer(BaseModel):
    researcherId: UUID = Field(..., description="UUID of the researcher")
    max_results: int = Field(..., gt=0, description="Maximum number of results to fetch")