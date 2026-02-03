from typing import Annotated
from pydantic import BaseModel , StringConstraints


class ResearcherSearchByNationalNumberSerializer(BaseModel):
    national_number: Annotated[
        str,
        StringConstraints(max_length=15)
    ]
