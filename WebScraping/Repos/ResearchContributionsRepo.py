from .BaseRepo import BaseRepo
from ..models.ResearchContributions import ResearchContributions


class ResearchContributionsRepo(BaseRepo):
     def __init__(self):
        super().__init__(ResearchContributions)