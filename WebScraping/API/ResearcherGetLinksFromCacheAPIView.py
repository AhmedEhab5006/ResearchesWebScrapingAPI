from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..Serializers.GetSerializers.ResearcherProfileAndORCIDGetSerializer import ResearcherProfileAndORCIDGetSerializer
from ..Serializers.GetSerializers.ResearcherSearchByNationalNumberSerializer import ResearcherSearchByNationalNumberSerializer
from ..Services.CacheService import CacheService

class ResearcherLinksView(APIView):
    def get(self, request):
        cache_service = CacheService()
        
        nationalNumber = ResearcherSearchByNationalNumberSerializer(**request.data)
        scholarLink = cache_service.get(f"researcher:{nationalNumber.national_number}:scholar")
        orcid = cache_service.get(f"researcher:{nationalNumber.national_number}:orcid")
        print(orcid)

        if orcid == None or scholarLink == None:
            return Response(
                {"detail": "Data Wasn't Entered Before Please Enter it"},
                status=status.HTTP_404_NOT_FOUND
            )

        model = ResearcherProfileAndORCIDGetSerializer(
            google_scholar_url=scholarLink,
            orcid=orcid
        )

        return Response(model.model_dump(), status=status.HTTP_200_OK)