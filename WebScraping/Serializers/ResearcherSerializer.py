from rest_framework import serializers
from models import Researcher
from Serializers import ResearchReadSerializer


class ResearcherReadSerializer(serializers.ModelSerializer):
    Researches = ResearchReadSerializer(many=True, read_only=True)

    class Meta:
        model = Researcher
        fields = ['Id', 'ORCID', 'Username', 'FormalName', 'Researches']


class ResearcherCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Researcher
        fields = ['ORCID', 'Username', 'FormalName']


class ResearcherUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Researcher
        fields = ['ORCID', 'Username', 'FormalName']
        extra_kwargs = {
            'ORCID': {'required': False},
            'Username': {'required': False},
            'FormalName': {'required': False},
        }
