from ..Repos.BaseRepo import BaseRepo
from ..models.ResearcherCites import ResearcherCites


class ResearcherCitesRepo(BaseRepo):
     def __init__(self):
        super().__init__(ResearcherCites)