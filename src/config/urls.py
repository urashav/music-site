from django.contrib.sitemaps.views import sitemap
from django.contrib import admin
from django.urls import path, include
from music.sitemaps import TrackSitemap

sitemaps = {'track': TrackSitemap}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sitemap.xml/', sitemap, {'sitemaps': sitemaps}),
    path('', include('music.urls')),
]
