from django.contrib import admin
from django.urls import path
from WebScraping.API.ResearchFetchingAPIVIew import ResearchFetchAPIView 
from WebScraping.API.ResearchFetchingUsingNameSerpApiView import ResearchFetchingUsingNameSerpApiView 
from WebScraping.API.ResearchFetchingUsingCrawleeAPiView import ResearchFetchingUsingCrawleeAPiView 
from WebScraping.API.ResearchFetchingUsingScholarProfileLinkAPIVIew import ResearchFetchingUsingScholarProfileLinkAPIVIew 


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/fetch-research-using-orcid/', ResearchFetchAPIView.as_view(), name='orcid'),
    path('api/fetch-research-using-name-serp/', ResearchFetchingUsingNameSerpApiView.as_view(), name='serp-api'),
    path('api/fetch-research-using-name-crawlee/', ResearchFetchingUsingCrawleeAPiView.as_view(), name='crawlee'),
    path('api/fetch-research-using-scholar-profile-link/', ResearchFetchingUsingScholarProfileLinkAPIVIew.as_view(), name='scholar'),


]
