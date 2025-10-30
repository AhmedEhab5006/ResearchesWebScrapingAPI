from Repos import BaseRepo
from Models import ResearcherResearch

class ResearcherResearchRepo(BaseRepo):
      def __init__(self):
        super().__init__(ResearcherResearch)