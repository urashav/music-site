import json

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
import requests
from .models import Track
from .decorators import restful
from .services.get_stream_url import get_stream_url

from pytils.translit import slugify


def home(request):
    new = Track.objects.all()[:16]
    recommended = Track.objects.order_by('?')[:8]
    popular = Track.objects.order_by('-counter')[:10]

    context = {
        'site_name': 'audiorussia.net',
        'meta_title': 'Скачивайте и слушайте русскую музыку на нашем сайте бесплатно!',
        'meta_description': 'На нашем сайте вы можете скачать или послушать русскую музыку без регистрации и СМС',
        'new': new,
        'recommended': recommended,
        'popular': popular,
    }
    return render(request, 'index.html', context)


def detail(request, slug):
    track = get_object_or_404(Track, slug=slug)

    new = Track.objects.all()[:16]
    recommended = Track.objects.order_by('?')[:8]
    popular = Track.objects.order_by('-counter')[:10]
    beside = Track.objects.filter(pk__range=(track.id - 5, track.id + 4)).exclude(pk=track.id)
    context = {
        'site_name': 'audiorussia.net',
        'meta_title': f"Скачать mp3 {track.title} бесплатно",
        'meta_description': f"Качай песню {track.title} в mp3 формате бесплатно с качеством 320кбит/с или слушай {track.get_artist()} на сайте online!",
        'new': new,
        'recommended': recommended,
        'popular': popular,
        'track': track,
        'beside': beside,
        'download_name': f"{slugify(track.title)}.mp3",
    }

    return render(request, 'detail.html', context)


@restful('POST')
def play(request, track_id):
    response = get_stream_url(track_id)

    return JsonResponse(response)


def download(request, slug):
    track = Track.objects.get(slug=slug)
    track.download_counter = track.download_counter + 1;
    track.save()

    stream_link = get_stream_url(track.id)
    name = slugify(track.title)
    filename = f"{name}.mp3"

    opener = requests.get(stream_link['url'])
    response = HttpResponse(opener, content_type="application/octet-stream")
    response["Content-Disposition"] = f"attachment; filename={filename}"
    return response


@restful('GET')
def robots_txt(request):
    lines = [
        "User-Agent: *",
        "Disallow: /admin",

        "Sitemap: https://audiorussia.net/sitemap.xml",
        "Host: https://audiorussia.net",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
