import requests
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from ..models import Track

def get_stream_url(track_id):
    track = get_object_or_404(Track, pk=track_id)
    CLIENT_ID = "a3dd183a357fcff9a6943c0d65664087"

    soundcloud_url = f"https://api.soundcloud.com/i1/tracks/{track.original_id}/streams?client_id={CLIENT_ID}"

    stream_url = cache.get(track_id)

    if not stream_url:
        json_data = requests.get(soundcloud_url)
        stream_url = json_data.json()['http_mp3_128_url']
        cache.set(track_id, stream_url, timeout=240)

    response = {
        'url': stream_url
    }
    track.counter = track.counter + 1
    track.save()

    return response