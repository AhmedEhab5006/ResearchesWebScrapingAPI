from rest_framework import serializers
from models import Researcher

class ResearcherCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Researcher
        fields = [
            'nationalNumber',
            'ORCID',
            'scholarProfileLink',
            'academicName',
            'scholarProfileImageURL',
            'organisationalDomain',
            'jobTitle',
            'organisationId',
            'totalNumberOfCitiations',
            'numberOfCitiationsInLastFiveYears',
            'hindex',
            'hindexInLastFiveYears',
            'i10index',
            'i10index5y'
        ]