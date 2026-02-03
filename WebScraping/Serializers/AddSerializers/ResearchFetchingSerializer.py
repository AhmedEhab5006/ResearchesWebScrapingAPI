from typing import Annotated
from pydantic import BaseModel, HttpUrl, StringConstraints


class ResearchFetchingSerializer(BaseModel):
    researcherNationalNumber: Annotated[
        str,
        StringConstraints(max_length=15)
    ]

    ORCID: Annotated[
        str,
        StringConstraints(pattern=r'^\d{4}-\d{4}-\d{4}-\d{4}$')
    ]

    scholarProfileLink: HttpUrl
