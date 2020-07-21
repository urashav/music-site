from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from .models import Track


# class StaticViewSitemap(Sitemap):
# Используется для статических страниц
#     def items(self):
#         return ['about']

def location(self, item):
    return reverse(item)

class TrackSitemap(Sitemap):
    protocol = 'https'

    def items(self):
        return Track.objects.all()
