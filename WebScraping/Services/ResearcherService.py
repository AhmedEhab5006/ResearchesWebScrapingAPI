from ..Specifications.ResearcherSpecifcations import FieldEqualSpecification
from ..models.Researcher import Researcher
from ..Serializers.GetSerializers.ResearcherDataGetSerializer import ResearcherGetSerializer

def get_resercher_data (national_number):
    spec = FieldEqualSpecification("nationalNumber" , national_number)
    researcher = Researcher.objects.filter(spec.to_query())
    serializer = ResearcherGetSerializer(researcher, many=True)
    return serializer.data
