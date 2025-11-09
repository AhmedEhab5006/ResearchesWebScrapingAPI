from ..Repos.BaseRepo import BaseRepo
from ..models.Researcher import Researcher


class ResearcherRepo(BaseRepo):
     def __init__(self):
        super().__init__(Researcher)