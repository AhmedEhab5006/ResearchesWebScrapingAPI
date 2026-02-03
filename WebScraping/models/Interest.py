from django.db import models
from ..models.Researcher import Researcher
import uuid


class Interest(models.Model):
  
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.TextField()

    class Meta:
        db_table = 'Interests'   