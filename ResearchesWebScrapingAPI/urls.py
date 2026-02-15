from django.contrib import admin
from django.urls import path
from WebScraping.API.GoogleScholarResearchFetch import ResearchFetchingUsingScholarProfileLinkAPIVIew 
from WebScraping.API.ResearcherGetLinksFromCacheAPIView import ResearcherLinksView 


urlpatterns = [
    path('api/fetch-research-using-scholar-profile-link/', ResearchFetchingUsingScholarProfileLinkAPIVIew.as_view(), name='scholar'),
    path('api/fetch-researcher-links/', ResearcherLinksView.as_view(), name='cache'),

]
