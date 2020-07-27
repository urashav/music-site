from ..models import Playlist
from django.db.utils import DataError


def store_playlist(playlist_data):
    for playlist in playlist_data['collection']:
        if not Playlist.objects.filter(original_id=playlist['id']):
            try:
                playlist_obj = Playlist()
                playlist_obj.original_id = playlist.get('id')
                playlist_obj.full_url = playlist.get('permalink_url')
                playlist_obj.status = 'ready'
                playlist_obj.save()

            except (KeyError, DataError) as exc:
                # TODO: Настроить логирование
                print('exc')
    return True
