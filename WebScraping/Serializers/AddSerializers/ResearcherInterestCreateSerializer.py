from rest_framework import serializers
from models import ResearcherInterest

class ResearcherInterestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearcherInterest
        fields = [
            'researcher', 
            'name'   
        ]