from models import Research
from Repos import ResearchRepo
from Serializers.ResearchSerilazer import (
    ResearchCreateSerializer,
    ResearchUpdateSerializer,
    ResearchReadSerializer
)


class ResearchService:
    def __init__(self):
        self.repo = ResearchRepo()

    def get_all(self):
        researches = self.repo.get_all()
        return ResearchReadSerializer(researches, many=True).data

    def get_by_id(self, id):
        research = self.repo.get_by_id(id)
        if not research:
            raise ValueError("Research not found")
        return ResearchReadSerializer(research).data

    def create(self, data):
        serializer = ResearchCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        research = serializer.save()
        return ResearchReadSerializer(research).data

    def update(self, id, data):
        research = self.repo.get_by_id(id)
        if not research:
            raise ValueError("Research not found")
        serializer = ResearchUpdateSerializer(research, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        return ResearchReadSerializer(updated).data

    def delete(self, id):
        deleted, _ = self.repo.delete(id)
        if deleted == 0:
            raise ValueError("Research not found")
        return {"message": "Research deleted successfully"}
