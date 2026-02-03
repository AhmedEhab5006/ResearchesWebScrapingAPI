from django.db import models
import uuid

class Research(models.Model):
    
    Id = models.UUIDField(
         primary_key=True,     
         default=uuid.uuid4,    
         editable=False         
    )

    DOI = models.CharField(max_length = 100 , null=True, blank=True)
    title = models.TextField()
    Source = models.TextField()
    pubYear = models.TextField(blank=True , null = True)
    pubDate = models.TextField(blank=True , null= True)
    journal = models.TextField(blank=True , null = True)
    publisher = models.TextField(blank=True , null = True)
    noOfCititations = models.IntegerField(default= 0)
    isConfirmed = models.BooleanField(default= False)
    created_at = models.DateTimeField(auto_now_add=True)
    noOfPages = models.TextField(blank=True , null = True) 
    volume = models.TextField(blank=True , null = True)
    number = models.TextField(blank=True , null = True)
    pubURL = models.TextField(blank=True , null = True)
    abstract = models.TextField(blank=True , null = True)
    relatedResearchURL = models.TextField(blank=True , null = True)
    
    class Meta:
        db_table = 'Researches'

