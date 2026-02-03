from django.db import models
from ..models.Researcher import Researcher
from ..models.Interest import Interest
import uuid


class ResearcherInterest(models.Model):
  
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    researcher = models.ForeignKey(
        Researcher,
        to_field='nationalNumber',
        on_delete=models.CASCADE,
        db_column='researcherNationalNumber',
        related_name='researcher'
    )

    interest = models.ForeignKey(
        Interest,
        to_field='id',
        on_delete=models.CASCADE,
        db_column='interestId',
        related_name='interest',
        null=True,
        blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['interest', 'researcher'],
                name='unique_researcher_interest'
            )
        ]

        db_table = 'ResearchersInterests'   