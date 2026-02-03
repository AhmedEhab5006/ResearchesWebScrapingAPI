from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pydantic import ValidationError
from ..Serializers.AddSerializers.ResearchFetchingSerializer import ResearchFetchingSerializer
from ..Services.FetchingResearchesByGoogleScholarProfileLink import FetchingResearchesByProfileLinkGoogleScholarService


class ResearchFetchingUsingScholarProfileLinkAPIVIew(APIView):

    def post(self, request):
        try:
            payload = ResearchFetchingSerializer(**request.data)
        except ValidationError as e:
            return Response(
                {"success": False, "message": e.errors()},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = FetchingResearchesByProfileLinkGoogleScholarService.fetch_and_store_works(
            profile_url=payload.scholarProfileLink,
            researcher_nationalNumber=payload.researcherNationalNumber,
            orcid=payload.ORCID
        )

        return Response(
            {
                "success": True,
                "message": "Request processed successfully",
                "data": result,  
            },
            
            status=status.HTTP_200_OK
        )