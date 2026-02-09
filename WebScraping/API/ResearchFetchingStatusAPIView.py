from celery.result import AsyncResult
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class ResearchFetchingStatusAPIView(APIView):
    def get(self, request, job_id: str):
        res = AsyncResult(job_id)

        data = {
            "jobId": job_id,
            "state": res.state, 
        }

        if res.state == "SUCCESS":
            data["result"] = res.result
            return Response({"success": True, "data": data}, status=status.HTTP_200_OK)

        if res.state == "FAILURE":
            data["error"] = str(res.result)
            return Response({"success": False, "data": data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"success": True, "data": data}, status=status.HTTP_200_OK)
