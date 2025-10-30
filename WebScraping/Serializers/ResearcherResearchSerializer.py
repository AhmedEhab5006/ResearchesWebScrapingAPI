from rest_framework import serializers
from models import ResearcherResearch
from models import ResearchReadSerializer
from models import ResearcherReadSerializer


class ResearcherResearchReadSerializer(serializers.ModelSerializer):
    Researcher = ResearcherReadSerializer(read_only=True)
    Research = ResearchReadSerializer(read_only=True)

    class Meta:
        model = ResearcherResearch
        fields = ['Researcher', 'Research', 'Role', 'AddedAt']


class ResearcherResearchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearcherResearch
        fields = ['Researcher', 'Research', 'Role']


class ResearcherResearchUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearcherResearch
        fields = ['Role']
        extra_kwargs = {
            'Role': {'required': False},
        }
