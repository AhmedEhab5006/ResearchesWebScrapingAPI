from models import ResearcherResearch
from WebScraping.Repos import ResearcherResearchRepo
from Serializers.ResearcherResearchSerializer import (
    ResearcherResearchReadSerializer,
    ResearcherResearchCreateSerializer,
    ResearcherResearchUpdateSerializer
)


class ResearcherResearchService:
    def __init__(self):
        self.repo = ResearcherResearchRepo()

    def get_all(self):
        links = self.repo.get_all()
        return ResearcherResearchReadSerializer(links, many=True).data

    def get_by_ids(self, researcher_id, research_id):
        link = self.repo.get_by_ids(researcher_id, research_id)
        if not link:
            raise ValueError("Link not found")
        return ResearcherResearchReadSerializer(link).data

    def create(self, data):
        serializer = ResearcherResearchCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        link = serializer.save()
        return ResearcherResearchReadSerializer(link).data

    def update(self, researcher_id, research_id, data):
        link = self.repo.get_by_ids(researcher_id, research_id)
        if not link:
            raise ValueError("Link not found")
        serializer = ResearcherResearchUpdateSerializer(link, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        return ResearcherResearchReadSerializer(updated).data

    def delete(self, researcher_id, research_id):
        deleted, _ = self.repo.delete(researcher_id, research_id)
        if deleted == 0:
            raise ValueError("Link not found")
        return {"message": "ResearcherResearch deleted successfully"}
