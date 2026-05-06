from django.db import models
import uuid


class CoAuthor(models.Model):
  
    Id = models.UUIDField(
         primary_key=True,     
         default=uuid.uuid4,    
         editable=False         
    )

    scholarProfileLink = models.TextField()
    academicName = models.TextField(null=True , blank=True)
    scholarProfileImageURL = models.TextField(null=True , blank=True)
    jobTitle = models.TextField(null=True , blank=True)
    
    class Meta:
        db_table = 'CoAuthors'

