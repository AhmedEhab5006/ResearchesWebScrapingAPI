from .BaseRepo import BaseRepo
from ..models.ResearcherCoAuthor import ResearcherCoAuthor


class ResearcherCoAuthorRepo(BaseRepo):
     def __init__(self):
        super().__init__(ResearcherCoAuthor)