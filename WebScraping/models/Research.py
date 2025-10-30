from django.db import models
import uuid

class Research(models.Model):
    Id = models.UUIDField(
         primary_key=True,     
         default=uuid.uuid4,    
         editable=False         
    )

    DOI = models.CharField(max_length = 100)
    Link = models.TextField()
    Source = models.TextField()     