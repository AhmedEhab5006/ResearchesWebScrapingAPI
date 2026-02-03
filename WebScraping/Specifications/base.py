from django.db.models import Q

class Specification:
    def to_query(self):
        raise NotImplementedError()

    def __and__(self, other):
        return AndSpecification(self, other)

    def __or__(self, other):
        return OrSpecification(self, other)

    def __invert__(self):
        return NotSpecification(self)


class AndSpecification(Specification):
    def __init__(self, spec1, spec2):
        self.spec1 = spec1
        self.spec2 = spec2

    def to_query(self):
        return self.spec1.to_query() & self.spec2.to_query()


class OrSpecification(Specification):
    def __init__(self, spec1, spec2):
        self.spec1 = spec1
        self.spec2 = spec2

    def to_query(self):
        return self.spec1.to_query() | self.spec2.to_query()


class NotSpecification(Specification):
    def __init__(self, spec):
        self.spec = spec

    def to_query(self):
        return ~self.spec.to_query()
