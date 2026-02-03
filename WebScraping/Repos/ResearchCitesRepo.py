from ..Repos.BaseRepo import BaseRepo
from ..models.ResearchCites import ResearchCites


class ResearchCitesRepo(BaseRepo):
     def __init__(self):
        super().__init__(ResearchCites)