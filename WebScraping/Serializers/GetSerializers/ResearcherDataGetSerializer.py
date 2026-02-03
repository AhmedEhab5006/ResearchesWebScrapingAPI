from rest_framework import serializers

class ResearcherGetSerializer(serializers.Serializer):
    nationalNumber = serializers.CharField(max_length=15, default='0')
    ORCID = serializers.CharField()  
    scholarProfileLink = serializers.CharField()
    academicName = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    scholarProfileImageURL = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    organisationalDomain = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    jobTitle = serializers.CharField()
    organisationId = serializers.IntegerField() 
    totalNumberOfCitiations = serializers.IntegerField(default=0)
    numberOfCitiationsInLastFiveYears = serializers.IntegerField(default=0)
    hindex = serializers.IntegerField(default=0)
    hindexInLastFiveYears = serializers.IntegerField(default=0)
    i10index = serializers.IntegerField(default=0)
    i10index5y = serializers.IntegerField(default=0)