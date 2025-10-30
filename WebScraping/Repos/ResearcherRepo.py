from Repos import BaseRepo
from Models import Researcher


class ResearcherRepo(BaseRepo):
     def __init__(self):
        super().__init__(Researcher)