from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pydantic import ValidationError

from ..Serializers.AddSerializers.ResearchFetchingSerializer import ResearchFetchingSerializer
from WebScraping.Tasks.ResearchFetchingTask import fetch_researches_task

from WebScraping.throttles import (
    ScholarNationalNumberThrottle,
    ScholarProfileThrottle,
    ScholarGlobalThrottle,
)

from WebScraping.utils.JobLock import acquire_member_lock


class ResearchFetchingUsingScholarProfileLinkAPIVIew(APIView):
    throttle_classes = [
        ScholarNationalNumberThrottle,
        ScholarProfileThrottle,
        ScholarGlobalThrottle,
    ]

    def post(self, request):
        try:
            payload = ResearchFetchingSerializer(**request.data)
        except ValidationError as e:
            return Response(
                {"success": False, "message": e.errors()},
                status=status.HTTP_400_BAD_REQUEST
            )

        national_number = str(payload.researcherNationalNumber)

        if not acquire_member_lock(national_number):
            return Response(
                {
                    "success": False,
                    "message": "A job is already running for this researcher."
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        job = fetch_researches_task.delay(
            profile_url=str(payload.scholarProfileLink),
            researcher_nationalNumber=national_number,
            orcid=str(payload.ORCID)
        )

        return Response(
            {
                "success": True,
                "message": "Working in progress",
                "jobId": job.id,
                "statusEndpoint": f"/api/research-fetching/status/{job.id}",
            },
            status=status.HTTP_202_ACCEPTED
        )
