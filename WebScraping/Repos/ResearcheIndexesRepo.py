from .BaseRepo import BaseRepo
from ..models.ResearchIndex import ResearchIndex


class ResearcheIndexesRepo(BaseRepo):
     def __init__(self):
        super().__init__(ResearchIndex)