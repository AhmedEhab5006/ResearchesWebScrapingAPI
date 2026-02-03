from django.contrib import admin
from django.urls import path
from WebScraping.API.ORCIDResearchFetch import ResearchFetchAPIView 
from WebScraping.API.GoogleScholarResearchFetch import ResearchFetchingUsingScholarProfileLinkAPIVIew 
from WebScraping.API.ResearcherDataAPIView import ResearcherDataAPIView 


urlpatterns = [
    path('api/fetch-research-using-orcid/', ResearchFetchAPIView.as_view(), name='orcid'),
    path('api/fetch-research-using-scholar-profile-link/', ResearchFetchingUsingScholarProfileLinkAPIVIew.as_view(), name='scholar'),
    path('api/get-researcher-data/', ResearcherDataAPIView.as_view(), name='data'),

]
