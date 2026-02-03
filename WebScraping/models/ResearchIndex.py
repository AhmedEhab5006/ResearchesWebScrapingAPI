from django.db import models
from .Researcher import Researcher
from .Research import Research
import uuid

class ResearchIndex(models.Model):
    
    Id = models.UUIDField(
         primary_key=True,     
         default=uuid.uuid4,    
         editable=False         
    )

    researcher = models.ForeignKey(
        Researcher,
        to_field='nationalNumber',  
        on_delete=models.CASCADE,
        db_column='researcherNationalNumber',
        related_name='researcherIndex'
    )

    research = models.ForeignKey(
        Research,
        to_field='Id',  
        on_delete=models.CASCADE,
        db_column='researcherId',
        related_name='researchIndex'
    ) 
  
  
    platform = models.TextField(null=True, blank=True)
 
    class Meta:
            db_table = 'ResearchIndexes'   
            constraints = [
                models.UniqueConstraint(
                    fields=['researcher' , 'Id'],
                    name='Researcher_Indexes'
                )
            ] 
   

