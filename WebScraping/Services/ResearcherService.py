from models import Researcher
from Repos import ResearcherRepo
from Serializers.ResearcherSerializer import (
    ResearcherReadSerializer,
    ResearcherCreateSerializer,
    ResearcherUpdateSerializer
)


class ResearcherService:
    def __init__(self):
        self.repo = ResearcherRepo()

    def get_all(self):
        researchers = self.repo.get_all()
        return ResearcherReadSerializer(researchers, many=True).data

    def get_by_id(self, id):
        researcher = self.repo.get_by_id(id)
        if not researcher:
            raise ValueError("Researcher not found")
        return ResearcherReadSerializer(researcher).data

    def create(self, data):
        serializer = ResearcherCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        researcher = serializer.save()
        return ResearcherReadSerializer(researcher).data

    def update(self, id, data):
        researcher = self.repo.get_by_id(id)
        if not researcher:
            raise ValueError("Researcher not found")
        serializer = ResearcherUpdateSerializer(researcher, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        return ResearcherReadSerializer(updated).data

    def delete(self, id):
        deleted, _ = self.repo.delete(id)
        if deleted == 0:
            raise ValueError("Researcher not found")
        return {"message": "Researcher deleted successfully"}
