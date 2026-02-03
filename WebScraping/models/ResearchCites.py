from django.db import models
from ..models.Researcher import Researcher
from ..models.Research import Research
import uuid

class ResearchCites(models.Model):
    
    Id = models.UUIDField(
         primary_key=True,     
         default=uuid.uuid4,    
         editable=False         
    )

    research = models.ForeignKey(
        Research,
        to_field='Id',  
        on_delete=models.CASCADE,
        db_column='researchId',
        related_name='researchCites'
    ) 
  
    year = models.IntegerField()
    numberOfCites = models.IntegerField()

    class Meta:
            db_table = 'ResearchCites'   
            constraints = [
                models.UniqueConstraint(
                    fields=['research', 'Id'],
                    name='Research_Cites'
                )
            ] 
   

