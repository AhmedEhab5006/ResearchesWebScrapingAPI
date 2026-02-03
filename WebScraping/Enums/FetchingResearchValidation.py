from enum import Enum

class FetchingResearchValidation(Enum):
    Added = 1
    ConnectionError = 2
    DatabaseError = 3
    ResearcherDoesnotExist = 4
    AlreadyExist = 5
    NoResearchesToAdd = 6

