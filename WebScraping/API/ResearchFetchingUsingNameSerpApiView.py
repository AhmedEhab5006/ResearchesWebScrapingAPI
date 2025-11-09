from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..Serializers.ResearchWithNameSerializer import ResearchWithNameSerializer
from ..Services.FetchingResearchesByResearcherNameSerpApiService import FetchingResearchesByResearcherNameSerpApiService
from .ResponseHelpers.ResearchFetchingReponseHelper import ResearchFetchingReponseHelper
from pydantic import ValidationError

class ResearchFetchingUsingNameSerpApiView(APIView):

    def post(self, request):
        try:
            payload = ResearchWithNameSerializer(**request.data)
        except ValidationError as e:
            return Response(
                {"success": False, "message": e.errors()},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = FetchingResearchesByResearcherNameSerpApiService.fetch_and_store_works(
            username=payload.name,
            researcher_id=payload.researcherId,
            total_results=payload.max_results
        )

        return ResearchFetchingReponseHelper.from_fetching_enum(result)
