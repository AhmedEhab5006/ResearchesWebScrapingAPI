from django.db import models

class ResearcherCoAuthor(models.Model):
    Researcher = models.ForeignKey(
        'Researcher',
        on_delete=models.CASCADE,
        db_column='nationalNumber'
    )
    
    CoAuthor = models.ForeignKey(
        'CoAuthor',
        on_delete=models.CASCADE,
        db_column='CoAuthorId'
    )

   
    class Meta:
        unique_together = ('Researcher', 'CoAuthor')
        db_table = 'ResearcherCoAuthors'
        indexes = [
            models.Index(fields=['Researcher', 'CoAuthor']),
        ]