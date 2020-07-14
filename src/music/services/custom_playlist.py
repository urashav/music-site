from ..models import Track
from ..services.get_stream_url import get_stream_url

def custom_playlist():
    tracks = Track.objects.order_by('-counter')[:1]
    playlist = []
    for track in tracks:
        seconds = (track.duration / 1000) % 60
        minutes = (track.duration / (1000 * 60)) % 60

        # playlist.append({
        #     "id": "item-" + str(track.id),
        #     "title": track.title,
        #     "link": 'track.details.html',
        #     "thumb": {"src": track.artwork_img_url},
        #     "src": "#",
        #     "meta": {
        #         "author": "",
        #         "authorlink": "",
        #         "date": "",
        #         "category": "",
        #         "play": track.counter,
        #         "duration": f"{minutes}:{seconds}"
        #     }
        # })

    return playlist