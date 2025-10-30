from rest_framework import serializers
from models import Research


class ResearchReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Research
        fields = ['Id', 'DOI', 'Link', 'Source']


class ResearchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Research
        fields = ['DOI', 'Link', 'Source']


class ResearchUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Research
        fields = ['DOI', 'Link', 'Source']
        extra_kwargs = {
            'DOI': {'required': False},
            'Link': {'required': False},
            'Source': {'required': False},
        }
