from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..Serializers.AddSerializers.ResearchFetchingSerializer import ResearchFetchingSerializer
from ..Services.FetchingResearchesbyOrcidService import FetchingResearchesbyOrcidService
from .ResponseHelpers.ResearchFetchingReponseHelper import ResearchFetchingReponseHelper
from pydantic import ValidationError

class ResearchFetchAPIView(APIView):

    def post(self, request):
        try:
            payload = ResearchFetchingSerializer(**request.data)
        except ValidationError as e:
            return Response({"success": False, "message": e.errors()},
                            status=status.HTTP_400_BAD_REQUEST)

        result = FetchingResearchesbyOrcidService.fetch_and_store_works(
            orcid=payload.ORCID,
            researcher_national_number=payload.researcherNationalNumber
        )

        return ResearchFetchingReponseHelper.from_fetching_enum(result)

