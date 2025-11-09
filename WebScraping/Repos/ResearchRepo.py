from ..Repos.BaseRepo import BaseRepo
from ..models.Research import Research

class ResarchRepo(BaseRepo):
      def __init__(self):
        super().__init__(Research)