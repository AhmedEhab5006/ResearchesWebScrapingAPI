from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..Serializers.GetSerializers.ResearcherSearchByNationalNumberSerializer import ResearcherSearchByNationalNumberSerializer
from ..Services.ResearcherService import get_resercher_data
from .ResponseHelpers.ResearchFetchingReponseHelper import ResearchFetchingReponseHelper
from pydantic import ValidationError

class ResearcherDataAPIView(APIView):

    def get(self, request):
        try:
            payload = ResearcherSearchByNationalNumberSerializer(**request.data)
        except ValidationError as e:
            return Response({"success": False, "message": e.errors()},
                            status=status.HTTP_400_BAD_REQUEST)

        result = get_resercher_data(
            national_number=payload.national_number
        )

        return Response(
                {"success": True, "message": result},
                status=status.HTTP_200_OK
            )

