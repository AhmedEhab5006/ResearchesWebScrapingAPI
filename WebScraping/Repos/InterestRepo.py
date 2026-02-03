from ..Repos.BaseRepo import BaseRepo
from ..models.Interest import Interest


class InterestRepo(BaseRepo):
     def __init__(self):
        super().__init__(Interest)