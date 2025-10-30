from django.db import models
import uuid


class Researcher(models.Model):
    Id = models.UUIDField(
         primary_key=True,     
         default=uuid.uuid4,    
         editable=False         
        )
    
    ORCID = models.TextField()
    Username = models.TextField()
    FormalName = models.TextField()