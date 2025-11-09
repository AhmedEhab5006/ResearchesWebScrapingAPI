from ..Repos.BaseRepo import BaseRepo
from ..models.ResearcherResearch import ResearcherResearch

class ResearcherResearchRepo(BaseRepo):
      def __init__(self):
        super().__init__(ResearcherResearch)