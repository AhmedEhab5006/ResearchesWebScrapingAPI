from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..Serializers.GetSerializers.ResearcherSearchByNationalNumberSerializer import (
    ResearcherSearchByNationalNumberSerializer
)
from ..Services.CacheService import CacheService

class ResearcherLinksView(APIView):
    def get(self, request):
        cache_service = CacheService(None)

        # Convert QueryDict to dict
        data = request.query_params.dict()

        # Validate with Pydantic
        payload = ResearcherSearchByNationalNumberSerializer.model_validate(data)
        national_number = payload.national_number

        scholar_link = cache_service.get(f"researcher:{national_number}:scholar")
        orcid = cache_service.get(f"researcher:{national_number}:orcid")

        if scholar_link is None or orcid is None:
            return Response(
                {"detail": "Data Wasn't Entered Before Please Enter it"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {
                "google_scholar_url": scholar_link,
                "orcid": orcid
            },
            status=status.HTTP_200_OK
        )
