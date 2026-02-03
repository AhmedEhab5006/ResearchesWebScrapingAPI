from rest_framework import serializers
from models import ResearcherCites

class ResearcherCitesCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearcherCites
        fields = [
             'researcher', 
             'year', 
             'noOfCitations'
        ]