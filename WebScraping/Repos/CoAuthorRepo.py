from ..Repos.BaseRepo import BaseRepo
from ..models.CoAuthor import CoAuthor


class CoAuthorRepo(BaseRepo):
     def __init__(self):
        super().__init__(CoAuthor)