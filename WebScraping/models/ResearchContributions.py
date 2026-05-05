from django.db import models
from ..models.Researcher import Researcher
from ..models.Research import Research
import uuid

class ResearchContributions(models.Model):
    
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
        related_name='researcherContributions'
    )

    research = models.ForeignKey(
        Research,
        to_field='Id',  
        on_delete=models.CASCADE,
        db_column='researchId',
        related_name='researchContributions'
    ) 
  
  
    memberOrcid = models.TextField(null=True, blank=True)
    memberPositionInSearch = models.TextField(null=True, blank=True)
    memberAcademicName = models.TextField(blank=True , null = True) 
    memberScholarProfileURL = models.TextField(null=True, blank=True) 


    class Meta:
            db_table = 'ResearchContributions'   
            constraints = [
                models.UniqueConstraint(
                    fields=['research', 'Id'],
                    name='Research_Contribution'
                )
            ] 
   

