from rest_framework import serializers
from models import ResearcherResearch


class ResearcherResearchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearcherResearch
        fields = ['Researcher', 'Research', 'Role']


