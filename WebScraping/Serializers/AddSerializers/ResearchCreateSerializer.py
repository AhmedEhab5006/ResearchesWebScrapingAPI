from rest_framework import serializers
from models import Research

class ResearchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Research
        fields = [
            'DOI',
            'Link',
            'title',
            'Source',
            'pubYear',
            'publisher',
            'noOfCititations',
            'isConfirmed'
        ]