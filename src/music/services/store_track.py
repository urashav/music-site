from ..models import Track


def store_track(track_data, playlist):
    for track in track_data['tracks']:
        if not Track.objects.filter(original_id=track['id']):
            try:
                track_obj = Track()
                # track_obj.slug = track.get('title')
                track_obj.original_id = track.get('id')
                track_obj.title = track.get('title')
                track_obj.permalink_url = track.get('permalink_url')
                track_obj.artwork_img_url = track.get('artwork_url')
                track_obj.waveform_img_url = track.get('waveform_url')
                track_obj.duration = track.get('duration')
                track_obj.original_content_size = track.get('original_content_size')
                track_obj.genre = track.get('genre')
                track_obj.playlist_id = playlist
                track_obj.original_format = track.get('original_format')
                track_obj.bpm = track.get('bpm')
                track_obj.release_year = track.get('release_year')
                track_obj.release_month = track.get('release_month')
                track_obj.release_day = track.get('release_day')
                track_obj.save()

            except KeyError as exc:
                # TODO: Настроить логирование
                print('exc')
    return True
