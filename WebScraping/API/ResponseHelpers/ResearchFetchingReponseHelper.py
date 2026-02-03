from rest_framework.response import Response
from rest_framework import status
from ...Enums.FetchingResearchValidation import FetchingResearchValidation

class ResearchFetchingReponseHelper:
    @staticmethod
    def from_fetching_enum(result: FetchingResearchValidation):
        """
        Converts a FetchingResearchValidation enum to a DRF Response.
        """
        if result == FetchingResearchValidation.Added:
            return Response(
                {"success": True, "message": "Works fetched and stored successfully."},
                status=status.HTTP_200_OK
            )
        elif result == FetchingResearchValidation.ConnectionError:
            return Response(
                {"success": False, "message": "Failed to connect to Web Scraping API."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        elif result == FetchingResearchValidation.DatabaseError:
            return Response(
                {"success": False, "message": "Database error occurred while saving works."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        elif result == FetchingResearchValidation.ResearcherDoesnotExist:
            return Response(
                {"success": False, "message": "Researcher does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )
        elif result == FetchingResearchValidation.AlreadyExist:
            return Response(
                {"success": False, "message": "Researcher data already exist."},
                status=status.HTTP_409_CONFLICT
            )
        elif result == FetchingResearchValidation.NoResearchesToAdd:
            return Response(
                {"success": True, "message": "No new Researches to be added"},
                status=status.HTTP_204_NO_CONTENT
            )
        
        else:
            return Response(
                {"success": False, "message": "Unknown error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
