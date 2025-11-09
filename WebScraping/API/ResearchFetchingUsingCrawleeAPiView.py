from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pydantic import ValidationError
from ..Serializers.ResearchWithNameSerializer import ResearchWithNameSerializer
from ..Services.FetchingResearchUsingNameFreeAPI import FetchingResearchUsingNameFreeAPI
from .ResponseHelpers.ResearchFetchingReponseHelper import ResearchFetchingReponseHelper


class ResearchFetchingUsingCrawleeAPiView(APIView):

    def post(self, request):
        try:
            payload = ResearchWithNameSerializer(**request.data)
        except ValidationError as e:
            return Response(
                {"success": False, "message": e.errors()},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = FetchingResearchUsingNameFreeAPI.fetch_and_store_works_sync(
            name=payload.name,
            researcher_id=payload.researcherId,
            max_results=payload.max_results
        )
        return ResearchFetchingReponseHelper.from_fetching_enum(result)
