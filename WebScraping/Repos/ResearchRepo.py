from Repos import BaseRepo
from Models import Research

class ResarchRepo(BaseRepo):
      def __init__(self):
        super().__init__(Research)