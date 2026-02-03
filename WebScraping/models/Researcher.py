from django.db import models


class Researcher(models.Model):
  
    nationalNumber = models.CharField(max_length = 15 , primary_key=True , default= '0') 
    ORCID = models.TextField()
    scholarProfileLink = models.TextField()
    academicName = models.TextField(null=True , blank=True)
    scholarProfileImageURL = models.TextField(null=True , blank=True)
    organisationalDomain = models.TextField(null=True , blank=True)
    jobTitle = models.TextField()
    organisationId = models.DecimalField(max_digits=30, decimal_places=0)
    totalNumberOfCitiations = models.IntegerField(default=0)
    numberOfCitiationsInLastFiveYears = models.IntegerField(default=0)
    hindex = models.IntegerField(default=0)
    hindexInLastFiveYears = models.IntegerField(default=0)
    i10index = models.IntegerField(default=0)
    i10index5y = models.IntegerField(default=0)


    class Meta:
        db_table = 'Researchers'

