from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pydantic import ValidationError
from ..Serializers.FetchingResearchesByGoogleScholarProfileLinkSerializer import FetchingResearchesByGoogleScholarProfileLinkSerializer
from ..Services.FetchingResearchesByGoogleScholarProfileLink import FetchingResearchesByProfileLinkGoogleScholarService
from .ResponseHelpers.ResearchFetchingReponseHelper import ResearchFetchingReponseHelper


class ResearchFetchingUsingScholarProfileLinkAPIVIew(APIView):

    def post(self, request):
        try:
            payload = FetchingResearchesByGoogleScholarProfileLinkSerializer(**request.data)
        except ValidationError as e:
            return Response(
                {"success": False, "message": e.errors()},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = FetchingResearchesByProfileLinkGoogleScholarService.fetch_and_store_works(
            profile_url=payload.profileLink,
            researcher_id=payload.researcherId
        )

        return ResearchFetchingReponseHelper.from_fetching_enum(result)
