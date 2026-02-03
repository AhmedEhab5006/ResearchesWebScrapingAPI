from django.db import models
from ..models.Researcher import Researcher
import uuid


class ResearcherCites(models.Model):
  
    Id = models.UUIDField(     
         default=uuid.uuid4,    
         editable=False,
         primary_key=True         
    )

    researcher = models.ForeignKey(
        Researcher,
        to_field='nationalNumber',  
        on_delete=models.CASCADE,
        db_column='researcherNationalNumber',
        related_name='cites'
    ) 
    
    year = models.IntegerField()
    noOfCitations = models.IntegerField()


    class Meta:
            db_table = 'ResearchersCites'   
            constraints = [
                models.UniqueConstraint(
                    fields=['Id', 'researcher'],
                    name='unique_id_researcher'
                )
            ] 
        
