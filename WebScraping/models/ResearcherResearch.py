from django.db import models

class ResearcherResearch(models.Model):
    Researcher = models.ForeignKey(
        'Researcher',
        on_delete=models.CASCADE,
        db_column='ResearcherId'
    )
    
    Research = models.ForeignKey(
        'Research',
        on_delete=models.CASCADE,
        db_column='ResearchId'
    )

   
    class Meta:
        unique_together = ('Researcher', 'Research')
        db_table = 'ResearcherResearch'
        indexes = [
            models.Index(fields=['Researcher', 'Research']),
        ]