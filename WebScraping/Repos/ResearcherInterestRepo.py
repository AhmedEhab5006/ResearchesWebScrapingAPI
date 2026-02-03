from ..Repos.BaseRepo import BaseRepo
from ..models.ResearcherInterest import ResearcherInterest


class ResearcherInterestRepo(BaseRepo):
     def __init__(self):
        super().__init__(ResearcherInterest)