from django.db.models import Q
from ..Specifications.base import Specification

class FieldEqualSpecification(Specification):
    
    def __init__(self, field_name, value):
        self.field_name = field_name
        self.value = value

    
   
    def to_query(self):
        return Q(**{self.field_name: self.value})
